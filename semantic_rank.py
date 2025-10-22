import os
from typing import List, Tuple, Optional

def _char_ngrams(s: str, n: int = 3):
    s = s or ''
    s = s.strip()
    if len(s) < n:
        return {s}
    return {s[i:i+n] for i in range(len(s)-n+1)}

def char_ngram_similarity(a: str, b: str, n: int = 3) -> float:
    a_grams = _char_ngrams(a, n)
    b_grams = _char_ngrams(b, n)
    if not a_grams or not b_grams:
        return 0.0
    inter = a_grams & b_grams
    union = a_grams | b_grams
    return len(inter) / len(union)

def try_load_embeddings(path: str):
    """Try to load gensim KeyedVectors from given path. Return model or None."""
    if not path or not os.path.exists(path):
        return None
    try:
        from gensim.models import KeyedVectors
        model = KeyedVectors.load(path, mmap='r')
        return model
    except Exception:
        # try loading Word2Vec format (text or bin)
        try:
            from gensim.models import KeyedVectors
            model = KeyedVectors.load_word2vec_format(path, binary=False)
            return model
        except Exception:
            return None

def semantic_similarity(word: str, candidate: str, model=None) -> float:
    """Return semantic similarity in range [0,1]. Uses model if available else char-ngram proxy."""
    if model is not None:
        try:
            # gensim KeyedVectors similarity may return -1..1
            if word in model.key_to_index and candidate in model.key_to_index:
                sim = float(model.similarity(word, candidate))
                # normalize from [-1,1] to [0,1]
                return max(0.0, (sim + 1.0) / 2.0)
        except Exception:
            pass
    # fallback proxy
    return char_ngram_similarity(word, candidate, n=3)

def rerank_candidates(word: str, candidates: List[Tuple[str, int, int]], model=None, weight_semantic: float = 1.0) -> List[Tuple[str, int, int]]:
    """Given candidates as (candidate, dist, freq) produce a re-ranked list using semantic score.

    Lower score is better. We compute:
      score = dist*100 - min(freq,3000)/10 - semantic_norm*100*weight_semantic
    where semantic_norm in [0,1]
    """
    scored = []
    for c, dist, freq in candidates:
        sem = semantic_similarity(word, c, model=model)
        freq_bonus = min(freq, 3000) / 10.0
        sem_bonus = sem * 100.0 * float(weight_semantic)
        score = dist * 100.0 - freq_bonus - sem_bonus
        scored.append((c, dist, freq, sem, score))

    # sort by score ascending, tie-breaker by higher freq
    scored.sort(key=lambda x: (x[4], -x[2], x[0]))
    # return same shape as input (candidate, dist, freq)
    return [(c, d, f) for c, d, f, s, score in scored]
