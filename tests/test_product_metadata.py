import csv
import tempfile
from pathlib import Path

from src.services.product_metadata import ProductMetadataService


def test_product_metadata_service_enriches_recommendations():
    with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False) as handle:
        writer = csv.writer(handle)
        writer.writerow(["item_id", "product_name", "category", "brand", "price", "image_url", "description"])
        writer.writerow([143866, "Nike Air Running Shoes", "Sports", "Nike", 129.99, "https://example.com/shoes.jpg", "Lightweight running shoes"])
        temp_path = Path(handle.name)

    try:
        service = ProductMetadataService(metadata_path=str(temp_path))
        product = service.get_product(143866)
        enriched = service.enrich_recommendations([{"item_id": 143866, "score": 0.5}])

        assert product["product_name"] == "Nike Air Running Shoes"
        assert product["brand"] == "Nike"
        assert enriched[0]["product_name"] == "Nike Air Running Shoes"
        assert enriched[0]["score"] == 0.5
    finally:
        temp_path.unlink(missing_ok=True)
