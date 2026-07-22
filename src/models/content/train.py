import logging

logger = logging.getLogger(__name__)


def train_content_model(*args, **kwargs):
    """
    Wrapper function preserving training interface contract.
    Per project rules, model retraining is disabled and pre-trained TF-IDF & similarity artifacts are reused.
    """
    logger.info("Retraining is disabled per configuration. Using existing pre-trained Content artifacts.")
    raise NotImplementedError(
        "Model retraining is disabled. Re-use existing tfidf_vectorizer.pkl, tfidf_matrix.pkl, and similarity_model.pkl."
    )
