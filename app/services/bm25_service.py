import json
from rank_bm25 import BM25Okapi
from typing import List, Tuple

# Global BM25 index
bm25_index = None
bm25_corpus = None


def initialize_bm25():
    """Load tokenized corpus and build BM25 index at startup."""
    global bm25_index, bm25_corpus
    try:
        with open("app/food_dataset/bm25_corpus.json", "r", encoding="utf-8") as f:
            bm25_corpus = json.load(f)
        bm25_index = BM25Okapi(bm25_corpus)
        print("BM25 index loaded successfully!")
    except Exception as e:
        print(f"Failed to load BM25 index: {e}")


def bm25_search(query: str, k: int = 20) -> List[Tuple[int, float]]:
    """
    Search BM25 index and return top-k (doc_index, score) pairs.
    """
    if bm25_index is None:
        return []

    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    # Get top-k indices sorted by score descending
    top_indices = scores.argsort()[-k:][::-1]
    return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]
