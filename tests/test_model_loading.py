import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.load_models import ModelRegistry


def test_model_loading():

    registry = ModelRegistry()

    als = registry.get_als_artifacts()

    content = registry.get_content_artifacts()

    print("ALS user factors:", als.user_factors.shape)
    print("ALS item factors:", als.item_factors.shape)

    print("TF-IDF matrix:", content.tfidf_matrix.shape)


if __name__ == "__main__":
    test_model_loading()