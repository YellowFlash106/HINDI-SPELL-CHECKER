#!/usr/bin/env python3
"""
File-based Spell Checker (Hindi)
"""

from data_loader import load_index
from spell_checker import generate_candidates, levenshtein_distance, operation_type
import re
from semantic_rank import try_load_embeddings, rerank_candidates
import time
import os


def process_input_file(input_file='input.txt', output_file='output.txt', use_semantic=False, embed_path=None, sem_weight=1.0):

    print("Loading dictionary...")
    freq_dict = load_index()
    if not freq_dict:
        print("Error: dictionary not found. Run data_loader.py to build the index first.")
        return

    print(f"Dictionary loaded: {len(freq_dict)} words")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print(f"Error: {input_file} is empty")
            return

        print(f"Processing {len(lines)} lines from: {input_file}...")

        results = []
        total_misspelled = 0
        total_corrections = 0

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            print(f"Processing line {i}: {line[:50]}...")

            start_time = time.time()

            tokens = [t for t in re.findall(r'[\u0900-\u097F]+|[^\u0900-\u097F]+', line)]

            misspelled = {}
            corrected_tokens = tokens[:]

            for idx_tok, tok in enumerate(tokens):
                leading = ''
                trailing = ''
                core = tok
                while core and not re.match(r'[\u0900-\u097F]', core[0]):
                    leading += core[0]
                    core = core[1:]
                while core and not re.match(r'[\u0900-\u097F]', core[-1]):
                    trailing = core[-1] + trailing
                    core = core[:-1]
                if not core:
                    continue
                word = core
                if word in freq_dict:
                    continue

                cands = generate_candidates(word, freq_dict)
                if use_semantic:
                    model = try_load_embeddings(embed_path) if embed_path else try_load_embeddings('embeddings.model')
                    cands = rerank_candidates(word, cands, model=model, weight_semantic=float(sem_weight))

                display = []
                for cand, dist, freq in cands[:5]:
                    op = operation_type(word, cand) if dist == 1 else None
                    if op:
                        display.append(f"{cand} (dist={dist}, op={op}, freq={freq})")
                    else:
                        display.append(f"{cand} (dist={dist}, freq={freq})")

                best = cands[0] if cands else None
                best_word = best[0] if best else None
                best_dist = best[1] if best else None
                best_freq = best[2] if best else 0

                misspelled[word] = display

                apply_correction = False
                if best:
                    if best_dist == 1:
                        apply_correction = True
                    elif best_dist == 2 and best_freq >= 200:
                        apply_correction = True

                if apply_correction and best_word:
                    corrected_tokens[idx_tok] = leading + best_word + trailing
                else:
                    corrected_tokens[idx_tok] = leading + word + trailing

            corrected_sentence = ''.join(corrected_tokens)

            m = re.search(r'([^\u0900-\u097F\s])\s*$', line)
            if m:
                end_punct = m.group(1)
                if not corrected_sentence.endswith(end_punct):
                    corrected_sentence = corrected_sentence + end_punct

            corrected_sentence = ''.join(corrected_tokens)

            results.append({
                'line_number': i,
                'original': line,
                'corrected': corrected_sentence,
                'misspelled': misspelled,
            })

        write_output_file(results, output_file)

        print("\nProcessing complete!")
        print(f"Results written to: {output_file}")
        print(f"Total lines processed: {len(results)}")

    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except Exception as e:
        print(f"Processing error: {e}")


def write_output_file(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("HINDI SPELL CHECKER - OUTPUT RESULTS\n")
        f.write("=" * 60 + "\n\n")
        for res in results:
            f.write(f"Line {res['line_number']}:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Original:  {res['original']}\n")
            f.write(f"Corrected: {res['corrected']}\n")
            if res['misspelled']:
                f.write(f"\nMisspelled Words ({len(res['misspelled'])}):\n")
                for w, s in res['misspelled'].items():
                    f.write(f"  '{w}' -> {', '.join(s)}\n")
            else:
                f.write("\nNo misspelled words found.\n")
            f.write("\n" + "=" * 60 + "\n\n")


if __name__ == '__main__':
    import sys
    input_file = 'input.txt'
    output_file = 'output.txt'
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    process_input_file(input_file, output_file)
