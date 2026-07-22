import logging
from typing import Optional, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def filter_interactions(
    df: pd.DataFrame,
    min_user_interactions: int = 1,
    min_item_interactions: int = 1,
    event_type_col: Optional[str] = None,
    event_types: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Filters interaction data by minimum interaction thresholds and event types.

    Args:
        df: Raw interactions DataFrame (expects 'visitorid' and 'itemid' columns).
        min_user_interactions: Minimum interactions per user to retain.
        min_item_interactions: Minimum interactions per item to retain.
        event_type_col: Column name for event type filtering.
        event_types: List of event types to keep (e.g., ['view', 'addtocart', 'transaction']).

    Returns:
        Filtered DataFrame.
    """
    result = df.copy()

    # Filter by event types if specified
    if event_type_col and event_types:
        result = result[result[event_type_col].isin(event_types)]
        logger.info(f"After event type filter ({event_types}): {len(result)} rows")

    # Filter by minimum user interactions
    if min_user_interactions > 1 and "visitorid" in result.columns:
        user_counts = result["visitorid"].value_counts()
        valid_users = user_counts[user_counts >= min_user_interactions].index
        result = result[result["visitorid"].isin(valid_users)]
        logger.info(f"After min user interactions ({min_user_interactions}): {len(result)} rows")

    # Filter by minimum item interactions
    if min_item_interactions > 1 and "itemid" in result.columns:
        item_counts = result["itemid"].value_counts()
        valid_items = item_counts[item_counts >= min_item_interactions].index
        result = result[result["itemid"].isin(valid_items)]
        logger.info(f"After min item interactions ({min_item_interactions}): {len(result)} rows")

    return result.reset_index(drop=True)


def build_interaction_matrix_inputs(
    df: pd.DataFrame,
    user_col: str = "visitorid",
    item_col: str = "itemid",
    value_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Prepares interaction data for sparse matrix construction by assigning contiguous integer
    indices to users and items.

    Args:
        df: Filtered interactions DataFrame.
        user_col: Column name for user identifiers.
        item_col: Column name for item identifiers.
        value_col: Optional column for interaction strength/weight. Defaults to implicit 1.

    Returns:
        DataFrame with 'user_idx', 'item_idx', and 'value' columns.
    """
    users = df[user_col].unique()
    items = df[item_col].unique()

    user_map = {uid: idx for idx, uid in enumerate(users)}
    item_map = {iid: idx for idx, iid in enumerate(items)}

    result = pd.DataFrame({
        "user_idx": df[user_col].map(user_map),
        "item_idx": df[item_col].map(item_map),
        "value": df[value_col] if value_col and value_col in df.columns else 1.0,
    })

    logger.info(f"Built matrix inputs: {len(users)} users x {len(items)} items, {len(result)} interactions")
    return result


def assign_confidence_weights(
    df: pd.DataFrame,
    event_type_col: str = "event",
    weight_map: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Assigns implicit confidence weights to interactions based on event type.

    Args:
        df: Interactions DataFrame.
        event_type_col: Column name for event type.
        weight_map: Dict mapping event types to numeric weights.
            Defaults to {'view': 1.0, 'addtocart': 3.0, 'transaction': 5.0}.

    Returns:
        DataFrame with an added 'confidence' column.
    """
    if weight_map is None:
        weight_map = {"view": 1.0, "addtocart": 3.0, "transaction": 5.0}

    result = df.copy()
    result["confidence"] = result[event_type_col].map(weight_map).fillna(1.0)
    return result
