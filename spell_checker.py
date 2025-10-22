import re
from collections import Counter
import sys
import argparse
import os
import json


def load_hindi_corpus(file_path, cache_path=None):
    if cache_path and os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as cf:
                data = json.load(cf)
            return Counter({k: int(v) for k, v in data.items()})
        except Exception:
            pass

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Corpus file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    words = re.findall(r'[\u0900-\u097F]+', text)
    word_freq = Counter(words)

    if cache_path:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as cf:
                json.dump(dict(word_freq), cf, ensure_ascii=False)
        except Exception:
            pass

    return word_freq

# Hindi letters for edits

hindi_letters = [
    'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ',
    'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण',
    'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह',
    'ळ', 'क्ष', 'ज्ञ', '०', '१', '२', '३', '४', '५', '६', '७', '८', '९',
    'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः', '़', '्'
]

def levenshtein_distance(s1, s2):
    len1, len2 = len(s1), len(s2)
    dp = [[0]*(len2+1) for _ in range(len1+1)]
    for i in range(len1+1):
        dp[i][0] = i
    for j in range(len2+1):
        dp[0][j] = j
    for i in range(1, len1+1):
        for j in range(1, len2+1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )
            if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                dp[i][j] = min(dp[i][j], dp[i-2][j-2] + cost)
    return dp[len1][len2]

# Generate edits1 for operation type detection and quick candidates
def edits1(word):
    splits = [(word[:i], word[i:]) for i in range(len(word)+1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in hindi_letters]
    inserts = [L + c + R for L, R in splits for c in hindi_letters]
    return set(deletes + transposes + replaces + inserts)

# Quick check for known words
def known(words, word_freq):
    return set(w for w in words if w in word_freq)

# Determine single-edit operation type (only meaningful when dist==1)
def operation_type(orig, cand):
    if orig == cand:
        return None
    if len(cand) == len(orig) + 1:
        return 'insertion'
    if len(cand) + 1 == len(orig):
        return 'deletion'
    if len(cand) == len(orig):
        diffs = [(i, orig[i], cand[i]) for i in range(len(orig)) if orig[i] != cand[i]]
        if len(diffs) == 1:
            return 'substitution'
        for i in range(len(orig)-1):
            if (orig[:i] + orig[i+1] + orig[i] + orig[i+2:]) == cand:
                return 'transposition'
    return None

def generate_candidates(word, word_freq, max_distance=4):
    cand_set = set()
    cand_set |= known([word], word_freq)
    cand_set |= known(edits1(word), word_freq)
    if len(cand_set) == 0:
        e2 = set(e2 for e1 in edits1(word) for e2 in edits1(e1))
        cand_set |= known(e2, word_freq)
    if not cand_set:
        for v in word_freq:
            d = levenshtein_distance(word, v)
            if d <= max_distance:
                cand_set.add(v)
    candidates = []
    for c in cand_set:
        d = levenshtein_distance(word, c)
        candidates.append((c, d, word_freq.get(c, 0)))
    candidates.sort(key=lambda x: (x[1], -x[2], x[0]))
    return candidates   

# Process an input file (multiple sentences). Output per-line details and corrected sentences.
def spell_check_file(input_path, output_path, corpus_path, top_n=5, max_distance=4, cache_path=None):
    word_freq = load_hindi_corpus(corpus_path, cache_path=cache_path)
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]

    results_lines = []
    for idx, sentence in enumerate(lines, start=1):
        tokens = re.findall(r'[\u0900-\u097F]+|[^\u0900-\u097F]+', sentence)
        corrected_tokens = tokens[:]   
        misspelled_info = [] 

        for i, tok in enumerate(tokens):
            if re.fullmatch(r'[\u0900-\u097F]+', tok):
                word = tok
                if word in word_freq:
                    continue   
                cand_tuples = generate_candidates(word, word_freq, max_distance=max_distance)
                display_cands = []
                for cand, dist, freq in cand_tuples[:top_n]:
                    op = operation_type(word, cand) if dist == 1 else None
                    if op:
                        display_cands.append(f"{cand} (dist={dist}, op={op}, freq={freq})")
                    else:
                        display_cands.append(f"{cand} (dist={dist}, freq={freq})")
                best = cand_tuples[0][0] if cand_tuples else None
                misspelled_info.append({
                    'word': word,
                    'candidates': display_cands,
                    'best': best
                })
                if best:
                    corrected_tokens[i] = best
        corrected_sentence = ''.join(corrected_tokens)
        if misspelled_info:
            results_lines.append(f"Line {idx} corrections:")
            for info in misspelled_info:
                results_lines.append(f"  Word: {info['word']}")
                results_lines.append(f"  Suggestions: {', '.join(info['candidates'])}")
                results_lines.append(f"  Best correction: {info['best']}")
                results_lines.append("")
        else:
            results_lines.append(f"Line {idx}: No misspelled Hindi words.")

        results_lines.append(f"Original (line {idx}): {sentence}")
        results_lines.append(f"Corrected (line {idx}): {corrected_sentence}")
        results_lines.append("-" * 60)
        results_lines.append("")

    with open(output_path, 'w', encoding='utf-8') as outf:
        outf.write("Hindi Spell Checker - Detailed Output\n\n")
        outf.write("\n".join(results_lines))

    print(f"✅ Done. Results saved to {output_path}")

# If run as script, example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hindi spell checker using a titles corpus")
    parser.add_argument('--input', '-i', default='input.txt', help='Input file with sentences (one per line)')
    parser.add_argument('--output', '-o', default='output.txt', help='Output file for detailed results')
    parser.add_argument('--corpus', '-c', default=os.path.join('hiwiki-latest-all-titles', 'hiwiki-latest-all-titles'),
                        help='Corpus file to build Hindi vocabulary (default: hiwiki titles included in repo)')
    parser.add_argument('--cache', default=os.path.join('output', 'corpus.json'), help='Optional cache for corpus word frequencies')
    parser.add_argument('--top', type=int, default=5, help='Top N suggestions to show per misspelled word')
    parser.add_argument('--maxdist', type=int, default=4, help='Maximum edit distance to consider when scanning vocabulary')
    args = parser.parse_args()

    try:
        os.makedirs(os.path.dirname(args.cache), exist_ok=True)
    except Exception:
        pass

    try:
        spell_check_file(args.input, args.output, args.corpus, top_n=args.top, max_distance=args.maxdist, cache_path=args.cache)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(2)
