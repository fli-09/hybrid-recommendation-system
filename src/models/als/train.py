import logging

logger = logging.getLogger(__name__)


def train_als_model(*args, **kwargs):
    """
    Wrapper function preserving training interface contract.
    Per project rules, model retraining is disabled and pre-trained factor matrices are reused.
    """
    logger.info("Retraining is disabled per configuration. Using existing pre-trained ALS embeddings.")
    raise NotImplementedError(
        "Model retraining is disabled. Re-use pre-trained user_factors.npy and item_factors.npy."
    )
