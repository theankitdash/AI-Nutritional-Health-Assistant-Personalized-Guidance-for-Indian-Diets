from typing import List
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from app.services.faiss_service import faiss_search_with_indices, get_food_texts, get_food_metadata
from app.services.bm25_service import bm25_search

# Cross-Encoder reranker (loaded once at startup)
reranker_model = None


def initialize_reranker():
    global reranker_model
    try:
        reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("Cross-Encoder reranker loaded successfully!")
    except Exception as e:
        print(f"Failed to load reranker: {e}")


def reciprocal_rank_fusion(
    faiss_results: List[tuple],
    bm25_results: List[tuple],
    k_rrf: int = 60
) -> List[int]:
    """
    Fuse FAISS and BM25 results using Reciprocal Rank Fusion.
    Returns a list of document indices sorted by fused score.
    
    Args:
        faiss_results: List of (doc_index, Document) from FAISS
        bm25_results: List of (doc_index, score) from BM25
        k_rrf: RRF constant (default 60)
    """
    fused_scores = {}

    # Score from FAISS (rank-based)
    for rank, (doc_idx, _) in enumerate(faiss_results):
        fused_scores[doc_idx] = fused_scores.get(doc_idx, 0) + 1.0 / (k_rrf + rank + 1)

    # Score from BM25 (rank-based)
    for rank, (doc_idx, _) in enumerate(bm25_results):
        fused_scores[doc_idx] = fused_scores.get(doc_idx, 0) + 1.0 / (k_rrf + rank + 1)

    # Sort by fused score descending
    sorted_indices = sorted(fused_scores.keys(), key=lambda idx: fused_scores[idx], reverse=True)
    return sorted_indices


def rerank(query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
    """
    Re-rank documents using the Cross-Encoder model.
    Returns the top_k most relevant documents.
    """
    if reranker_model is None or not documents:
        return documents[:top_k]

    # Create query-document pairs for scoring
    pairs = [[query, doc.page_content] for doc in documents]
    scores = reranker_model.predict(pairs)

    # Sort by score descending
    scored_docs = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored_docs[:top_k]]


def hybrid_search(query: str, k_final: int = 5) -> List[Document]:
    """
    Two-stage hybrid retrieval:
      Stage 1: Run BM25 + FAISS in parallel, fuse with RRF
      Stage 2: Re-rank the fused candidates with a Cross-Encoder
    
    Returns the top k_final most relevant Documents.
    """
    k_fetch = 20  # Number of candidates from each retriever

    # Stage 1a: FAISS dense retrieval
    faiss_results = faiss_search_with_indices(query, k=k_fetch)

    # Stage 1b: BM25 sparse retrieval
    bm25_results = bm25_search(query, k=k_fetch)

    # Fuse results with RRF
    fused_indices = reciprocal_rank_fusion(faiss_results, bm25_results)

    # Build Document objects for fused candidates
    texts = get_food_texts()
    meta_list = get_food_metadata()
    candidate_docs = []
    for idx in fused_indices[:k_fetch]:  # Take top k_fetch fused candidates
        text = texts[idx] if idx < len(texts) else ""
        meta = meta_list[idx] if idx < len(meta_list) else {}
        candidate_docs.append(Document(page_content=text, metadata=meta))

    if not candidate_docs:
        return []

    # Stage 2: Re-rank with Cross-Encoder
    return rerank(query, candidate_docs, top_k=k_final)
