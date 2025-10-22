import os
from collections import Counter
import json
import re

from typing import List, Tuple

DEFAULT_CORPUS = os.path.join('hiwiki-latest-all-titles', 'hiwiki-latest-all-titles')


class CorpusDict:
  

    def __init__(self, corpus_path: str = DEFAULT_CORPUS, cache_path: str = None):
        self.corpus_path = corpus_path
        self.cache_path = cache_path
        self.word_freq = self._load()

    def _load(self) -> Counter:
        if self.cache_path and os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as cf:
                    data = json.load(cf)
                return Counter({k: int(v) for k, v in data.items()})
            except Exception:
                pass

        if not os.path.exists(self.corpus_path):
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}")

        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            text = f.read()
        words = re.findall(r'[\u0900-\u097F]+', text)
        cnt = Counter(words)

        if self.cache_path:
            try:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                with open(self.cache_path, 'w', encoding='utf-8') as cf:
                    json.dump(dict(cnt), cf, ensure_ascii=False)
            except Exception:
                pass

        return cnt

    def is_known(self, word: str) -> bool:
        return word in self.word_freq

    def frequency(self, word: str) -> int:
        return self.word_freq.get(word, 0)

    def vocab(self) -> List[str]:
        return list(self.word_freq.keys())

    def top_n_candidates(self, candidates: List[Tuple[str, int]], n: int = 5) -> List[Tuple[str, int, int]]:
        enriched = [(c, d, self.frequency(c)) for c, d in candidates]
        enriched.sort(key=lambda x: (x[1], -x[2], x[0]))
        return enriched[:n]
