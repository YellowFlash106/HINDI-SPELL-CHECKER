<!-- prettier-ignore -->
# IR Assignment — Hindi Spell Checker


[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

Repository: https://github.com/YellowFlash106/HINDI-SPELL-CHECKER

A compact toolkit to build a Hindi vocabulary from Wikipedia title dumps and run a frequency + edit-distance based spell checker.

--

Table of contents
- What’s inside
- Quick start (Windows)
- Advanced usage & tips
- Cleanup / disk-saver notes
- Next steps

What’s inside
- `data_loader.py` — locate title files (auto-detects `*all-titles*`), tokenize titles, build a frequency index `index.pkl` (Counter).
- `spell_checker.py` — core algorithms (edits, Levenshtein, candidate generation) and a small CLI runner.
- `corpus_dict.py` — lightweight wrapper to read a titles file and expose top candidates / frequencies.
- `run_spell_check_using_dict.py` — runner that uses the titles file (or cache) directly; outputs `output_dict.txt`.
- `file_processor.py` — file-oriented runner that reads `input.txt` and writes `output.txt` (prints messages in English).
- `input.txt` — example sentences for quick testing.

Quick start (Windows cmd)

1) Build index (auto-detects hiwiki if present):

If you don't yet have the project locally, clone the repository and open a terminal in the project folder:

```cmd
git clone https://github.com/YellowFlash106/HINDI-SPELL-CHECKER.git
cd HINDI-SPELL-CHECKER
```

If you already have the repository locally, open a terminal in the project folder and run:

```cmd
python data_loader.py
```

If your titles file is stored elsewhere, pass its path explicitly:

```cmd
python data_loader.py path\to\hiwiki-latest-all-titles
```

2) Run the simple file processor (reads `input.txt`, writes `output.txt`):

```cmd
python file_processor.py
```

3) Or run the dict-based runner (uses titles file or cache and writes `output_dict.txt`):

```cmd
python run_spell_check_using_dict.py --input input.txt --output output_dict.txt --corpus hiwiki-latest-all-titles\hiwiki-latest-all-titles
```

Advanced usage & flags
- `--cache`: path for JSON cache of corpus frequencies (used by runners to avoid rebuilding full Counter each run).
- `--top N`: change how many suggestions to show per misspelled word.
- `--maxdist D`: maximum edit distance to consider when scanning vocabulary.

Tips & notes
- If `index.pkl` is present, `file_processor.py` uses it (much faster). If you delete it, re-run `data_loader.py`.
- Title files (wiki dumps) are large — keep a copy if you want to avoid re-downloading.
- The checker ranks candidates by (1) edit distance, (2) frequency, then lexicographically. It does not use a contextual language model.

Recommended safe cleanup
- `__pycache__/` and `*.pyc` — safe to remove.
- `output.txt`, `output_dict.txt` — generated outputs.
- `output/corpus.json` — cache file.
- `hiwiki-latest-all-titles/` — remove only if you can re-download or don't plan to rebuild the index.

Want help?
- I can: build the index now, delete generated files for you, or improve the README further (add Hindi section, examples, or badges).

Feel free to tell me which of the above to run next and I’ll execute it.
 
---

✨ Features

- Complete edit operations (Damerau–Levenshtein style): insertion, deletion, substitution, transposition
- Smart auto-correction: confidence-based automatic correction using frequency ranking
- Flexible candidate ranking: edit-distance + corpus frequency prioritization
- File processing: batch processing from `input.txt` → `output.txt` (detailed reports)
- Secondary storage: fast dictionary load/save via pickle (`index.pkl`) and optional JSON cache (`output/corpus.json`)
- Unicode support: full Devanagari (Hindi) Unicode handling (regex range \u0900-\u097F)

🖥️ System requirements

- Python: 3.6+
- OS: Windows / macOS / Linux
- Memory: 512 MB minimum
- Disk: depends on corpus; large wiki title files can be tens to hundreds of MB
- Encoding: UTF-8 (ensure terminal/editor supports UTF-8 for Hindi)

🚀 Installation

1. Clone or download the project and open a terminal in the project folder:

```cmd
https://github.com/YellowFlash106/HINDI-SPELL-CHECKER
```

2. (Recommended) Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies (if a `requirements.txt` is provided):

```cmd
pip install -r requirements.txt
```

4. If you plan to build an index from titles, ensure you have a titles file in the workspace (e.g. `hiwiki-latest-all-titles/hiwiki-latest-all-titles`). Then build the index:

```cmd
python data_loader.py
```

If `data_loader.py` cannot find titles automatically, pass paths explicitly:

```cmd
python data_loader.py path\to\hiwiki-latest-all-titles
```

🎯 How to run

- Basic (use `index.pkl` if present):

```cmd
python main.py
```

- Run the file-based processor (reads `input.txt`, writes `output.txt`):

```cmd
python file_processor.py
```

- Run the dict-based runner (uses titles file or cache; writes `output_dict.txt`):

```cmd
python run_spell_check_using_dict.py --input input.txt --output output_dict.txt --corpus hiwiki-latest-all-titles\hiwiki-latest-all-titles
```

CLI flags (runners)
- `--input` / `-i` : input file (default `input.txt`)
- `--output` / `-o`: output file (default `output.txt` or `output_dict.txt`)
- `--corpus` / `-c`: path to a titles corpus file
- `--cache`: path to JSON cache for corpus frequencies
- `--top`: number of candidate suggestions to show
- `--maxdist`: max edit distance to scan vocabulary

📁 Module descriptions

1) `main.py` — Entry point
- Loads `index.pkl` (if present) and calls the file processor.
- Shows simple statistics and progress messages.

2) `data_loader.py` — Dictionary creation & management
- Loads title files, tokenizes for Devanagari words, adds common Hindi words, and builds a frequency Counter.
- Saves/loads the index using pickle (`index.pkl`).

3) `spell_checker.py` — Core algorithms
- Implements edit generation (`edits1`), Damerau-like Levenshtein distance with transpositions, candidate generation, and a CLI runner.
- Ranking: (edit distance ascending, frequency descending). A short auto-correct heuristic is used for high-confidence cases.

4) `file_processor.py` — File processing engine
- Reads `input.txt`, finds misspellings, generates suggestions, and writes a detailed `output.txt` report.

5) `corpus_dict.py` & `run_spell_check_using_dict.py` — Alternate runner
- `corpus_dict.py` loads a titles file into a Counter and offers helper APIs.
- `run_spell_check_using_dict.py` demonstrates running the checker directly against a titles corpus (no pickle index required).

🔬 Algorithm details (summary)

- Edit operations: insertion, deletion, substitution, transposition (Damerau-like)
- Candidate scoring: combination of edit distance and frequency. Lower is better.
- Auto-correction rules (example heuristic):
	- distance == 1 → auto-correct
	- distance == 2 and frequency ≥ threshold → consider auto-correct

Example scoring (used conceptually):
score = edit_distance * 100 - min(frequency, 3000) / 10

📄 Input / Output

- Input: `input.txt` (UTF-8), one sentence per line (Hindi text)
- Output: `output.txt` or `output_dict.txt` — detailed reports with original & corrected sentences, suggestions, and processing stats

💡 Examples

Input line:
```
भगत सिंग भारत के महन स्वतन्तरता सेनानी थे।
```
Output line:
```
भगत सिंग भारत के मोहन स्वतन्त्रता सेनानी थे।
```


Possible suggestion(s):
- `महन` → `मोहन` (dist=1, freq=high)

Troubleshooting
- `FileNotFoundError: guwiki-latest-all-titles` or similar: run `data_loader.py` and/or provide a corpus path.
- Unicode/terminal display issues: ensure your terminal/editor uses UTF-8.

Cleanup (safe to delete)
- `__pycache__/`, `*.pyc` (automatically re-generated)
- `output.txt`, `output_dict.txt` (generated results)
- `output/corpus.json` (corpus cache)
- `hiwiki-latest-all-titles/` — delete only if you don't need to rebuild the index

Authors & license
- Student / Author: Your project (update author line as needed)
- License: None specified

If you want, I can now:
- Build the index from the provided hiwiki titles file (may take a few minutes), or
- Clean up generated caches/output files, or
- Add a short Hindi section to the README for users who prefer instructions in Hindi.
