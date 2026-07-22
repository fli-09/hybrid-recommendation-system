from typing import Dict, List, Tuple, Any


def fuse_and_rank(
    als_norm: Dict[Any, float],
    content_norm: Dict[Any, float],
    als_weight: float = 0.5,
    content_weight: float = 0.5,
    top_n: int = 10,
    fusion_strategy: str = "weighted_sum",
    rrf_k: int = 60,
) -> List[Tuple[Any, float]]:
    """
    Fuses normalized scores or candidate rankings from ALS and Content models.

    Args:
        als_norm: Dict mapping item_id -> normalized score (or score ranking input)
        content_norm: Dict mapping item_id -> normalized score (or score ranking input)
        als_weight: Weight assigned to ALS model.
        content_weight: Weight assigned to Content model.
        top_n: Number of final top items to return.
        fusion_strategy: 'weighted_sum', 'reciprocal_rank' (RRF), or 'max'.
        rrf_k: Constant denominator shift for Reciprocal Rank Fusion (default 60).

    Returns:
        List of (item_id, float_fused_score) ordered descending.
    """
    all_item_ids = set(als_norm.keys()).union(set(content_norm.keys()))
    fusion_strategy = fusion_strategy.lower()

    fused_scores = {}

    if fusion_strategy == "weighted_sum":
        for item_id in all_item_ids:
            s_als = als_norm.get(item_id, 0.0)
            s_content = content_norm.get(item_id, 0.0)
            fused_scores[item_id] = (als_weight * s_als) + (content_weight * s_content)

    elif fusion_strategy == "max":
        for item_id in all_item_ids:
            s_als = als_norm.get(item_id, 0.0) * als_weight
            s_content = content_norm.get(item_id, 0.0) * content_weight
            fused_scores[item_id] = max(s_als, s_content)

    elif fusion_strategy == "reciprocal_rank":
        # Sort item IDs by raw score to derive 1-based ranks
        als_ranked = [item_id for item_id, _ in sorted(als_norm.items(), key=lambda x: x[1], reverse=True)]
        content_ranked = [item_id for item_id, _ in sorted(content_norm.items(), key=lambda x: x[1], reverse=True)]

        als_ranks = {item_id: rank + 1 for rank, item_id in enumerate(als_ranked)}
        content_ranks = {item_id: rank + 1 for rank, item_id in enumerate(content_ranked)}

        for item_id in all_item_ids:
            rrf_als = als_weight / (rrf_k + als_ranks[item_id]) if item_id in als_ranks else 0.0
            rrf_content = content_weight / (rrf_k + content_ranks[item_id]) if item_id in content_ranks else 0.0
            fused_scores[item_id] = rrf_als + rrf_content

    else:
        raise ValueError(f"Unknown fusion strategy: '{fusion_strategy}'. Choose 'weighted_sum', 'max', or 'reciprocal_rank'.")

    sorted_items = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_items[:top_n]
