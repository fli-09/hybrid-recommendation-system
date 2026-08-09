import csv
import hashlib
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from ..utils.config import get_project_root


class ProductMetadataService:
    """Loads and enriches recommendation results with product metadata."""

    def __init__(self, metadata_path: Optional[str] = None):
        self.metadata_path = metadata_path or self._default_metadata_path()
        self._catalog: Dict[int, Dict[str, Any]] = {}
        self.load_metadata()

    def _default_metadata_path(self) -> str:
        project_root = get_project_root()
        return os.path.join(project_root, "data", "product_metadata.csv")

    def load_metadata(self) -> None:
        self._catalog = {}
        if not os.path.exists(self.metadata_path):
            return

        with open(self.metadata_path, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                item_id = int(row["item_id"])
                self._catalog[item_id] = {
                    "item_id": item_id,
                    "product_name": row.get("product_name", f"Product {item_id}"),
                    "category": row.get("category", "General"),
                    "brand": row.get("brand", "Unknown"),
                    "price": float(row.get("price", 0.0)),
                    "image_url": row.get("image_url", ""),
                    "description": row.get("description", ""),
                }

    def _generate_fallback_product(self, item_id: int) -> Dict[str, Any]:
        seed = hashlib.md5(str(item_id).encode("utf-8")).hexdigest()
        categories = ["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Sports", "Accessories"]
        brands = ["Samsung", "Sony", "Nike", "Adidas", "Apple", "Philips", "Boat", "Dyson", "L'Oréal", "Under Armour"]
        category = categories[int(seed[:2], 16) % len(categories)]
        brand = brands[int(seed[2:4], 16) % len(brands)]
        price = 29.99 + (int(seed[4:8], 16) % 300) + (item_id % 7) * 5
        variant = ["Lite", "Plus", "Pro", "Max", "Ultra"][int(seed[8:10], 16) % 5]
        product_name = f"{brand} {category} {variant}"
        image_url = f"https://images.unsplash.com/photo-1495555961984-6d4421d7f7c0?auto=format&fit=crop&w=800&q=80"
        description = f"{product_name} designed for everyday shoppers and dependable performance."

        return {
            "item_id": item_id,
            "product_name": product_name,
            "category": category,
            "brand": brand,
            "price": round(price, 2),
            "image_url": image_url,
            "description": description,
        }

    def get_product(self, item_id: Any) -> Dict[str, Any]:
        item_key = int(item_id)
        product = self._catalog.get(item_key)
        if product:
            return product

        return self._generate_fallback_product(item_key)

    def enrich_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched: List[Dict[str, Any]] = []
        for recommendation in recommendations:
            item_id = int(recommendation["item_id"])
            product = self.get_product(item_id)
            enriched_item = dict(recommendation)
            enriched_item.update(product)
            enriched.append(enriched_item)
        return enriched


@lru_cache(maxsize=1)
def get_product_metadata_service() -> ProductMetadataService:
    return ProductMetadataService()
