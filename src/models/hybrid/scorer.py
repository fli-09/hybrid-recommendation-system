from typing import List, Tuple, Dict, Any
import numpy as np


def normalize_scores(
    score_tuples: List[Tuple[Any, float]],
    method: str = "minmax"
) -> Dict[Any, float]:
    """
    Normalizes a list of (item_id, raw_score) tuples into a dictionary mapping item_id to normalized float score.

    Args:
        score_tuples: List of (item_id, float_score)
        method: Normalization technique ('minmax', 'zscore', 'softmax')

    Returns:
        Dict mapping item_id to normalized float score.
    """
    if not score_tuples:
        return {}

    if isinstance(score_tuples[0], dict):
        items = [d["item_id"] for d in score_tuples]
        scores = [d["score"] for d in score_tuples]
    else:
        items, scores = zip(*score_tuples)
    scores_arr = np.array(scores, dtype=np.float64)

    method = method.lower()

    if method == "minmax":
        min_val = np.min(scores_arr)
        max_val = np.max(scores_arr)
        if max_val == min_val:
            norm_scores = np.ones_like(scores_arr) * 0.5
        else:
            norm_scores = (scores_arr - min_val) / (max_val - min_val)

    elif method == "zscore":
        mean_val = np.mean(scores_arr)
        std_val = np.std(scores_arr)
        if std_val == 0:
            norm_scores = np.ones_like(scores_arr) * 0.5
        else:
            z_scores = (scores_arr - mean_val) / std_val
            # Map z-scores to [0, 1] using logistic sigmoid
            norm_scores = 1.0 / (1.0 + np.exp(-z_scores))

    elif method == "softmax":
        # Numerical stability shift
        exp_scores = np.exp(scores_arr - np.max(scores_arr))
        sum_exp = np.sum(exp_scores)
        if sum_exp == 0:
            norm_scores = np.ones_like(scores_arr) / len(scores_arr)
        else:
            norm_scores = exp_scores / sum_exp

    else:
        raise ValueError(f"Unsupported normalization method: '{method}'. Choose 'minmax', 'zscore', or 'softmax'.")

    return {item_id: float(norm_score) for item_id, norm_score in zip(items, norm_scores)}
