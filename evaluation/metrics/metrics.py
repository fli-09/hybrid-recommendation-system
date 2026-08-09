import numpy as np
from typing import List, Set


def precision_at_k(recommended: List[int], ground_truth: Set[int], k: int) -> float:
    """Calculates Precision@K for a single user."""
    if not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / float(k)


def recall_at_k(recommended: List[int], ground_truth: Set[int], k: int) -> float:
    """Calculates Recall@K for a single user."""
    
    if not ground_truth or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / float(len(ground_truth))


def average_precision_at_k(recommended: List[int], ground_truth: Set[int], k: int) -> float:
    """Calculates Average Precision at K (AP@K) for a single user."""
    if not recommended or not ground_truth or k <= 0:
        return 0.0
    
    score = 0.0
    num_hits = 0.0

    for i, item in enumerate(recommended[:k]):
        if item in ground_truth and item not in recommended[:i]:
            num_hits += 1.0
            score += num_hits / (i + 1.0)

    return score / min(len(ground_truth), k)
