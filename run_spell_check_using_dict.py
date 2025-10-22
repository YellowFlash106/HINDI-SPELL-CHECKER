import argparse
import os
import re

from corpus_dict import CorpusDict
import spell_checker as sc


def check_file_with_dict(input_path, output_path, corpus_path, cache_path=None, top_n=5, max_distance=4):
    print("Corpus loaded...")
    corpus = CorpusDict(corpus_path, cache_path=cache_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]

    results = []

    for idx, sentence in enumerate(lines, start=1):
        tokens = re.findall(r'[\u0900-\u097F]+|[^\u0900-\u097F]+', sentence)
        corrected = tokens[:]
        miss_info = []
        for i, tok in enumerate(tokens):
            if re.fullmatch(r'[\u0900-\u097F]+', tok):
                word = tok
                if corpus.is_known(word):
                    continue
                e1 = sc.edits1(word)
                cand_set = set(w for w in e1 if corpus.is_known(w))
                if not cand_set:
                    e2 = set(e2 for e1w in e1 for e2 in sc.edits1(e1w))
                    cand_set |= set(w for w in e2 if corpus.is_known(w))
                if not cand_set:
                    for v in corpus.vocab():
                        d = sc.levenshtein_distance(word, v)
                        if d <= max_distance:
                            cand_set.add(v)

                candidates = []
                for c in cand_set:
                    candidates.append((c, sc.levenshtein_distance(word, c)))

                enriched = corpus.top_n_candidates(candidates, n=top_n)

                display = []
                for c, dist, freq in enriched:
                    op = sc.operation_type(word, c) if dist == 1 else None
                    if op:
                        display.append(f"{c} (dist={dist}, op={op}, freq={freq})")
                    else:
                        display.append(f"{c} (dist={dist}, freq={freq})")

                best = enriched[0][0] if enriched else None
                miss_info.append({'word': word, 'candidates': display, 'best': best})
                if best:
                    corrected[i] = best

        if miss_info:
            results.append(f"Line {idx} corrections:")
            for info in miss_info:
                results.append(f"  Word: {info['word']}")
                results.append(f"  Suggestions: {', '.join(info['candidates'])}")
                results.append(f"  Best correction: {info['best']}")
                results.append("")
        else:
            results.append(f"Line {idx}: No misspelled Hindi words.")

        results.append(f"Original (line {idx}): {sentence}")
        results.append(f"Corrected (line {idx}): {''.join(corrected)}")
        results.append('-' * 60)
        results.append('')

    with open(output_path, 'w', encoding='utf-8') as outf:
        outf.write("Hindi Spell Checker (dict wrapper) - Detailed Output\n\n")
        outf.write('\n'.join(results))

    print(f" Completed। output saved to: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='input.txt')
    parser.add_argument('--output', '-o', default='output_dict.txt')
    parser.add_argument('--corpus', '-c', default=os.path.join('hiwiki-latest-all-titles', 'hiwiki-latest-all-titles'))
    parser.add_argument('--cache', default=os.path.join('output', 'corpus.json'))
    parser.add_argument('--top', type=int, default=5)
    parser.add_argument('--maxdist', type=int, default=4)
    args = parser.parse_args()

    check_file_with_dict(args.input, args.output, args.corpus, cache_path=args.cache, top_n=args.top, max_distance=args.maxdist)
