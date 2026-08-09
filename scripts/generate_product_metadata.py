import argparse
import csv
import logging
import pickle
import random
from pathlib import Path
from typing import List, Set, Tuple

from src.inference.recommend import InferenceEngine
from src.utils.config import get_project_root

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


PRODUCT_SEED_DATA = [
    ("Electronics", "Samsung", "Wireless Noise Cancelling Headphones", 199.99, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80"),
    ("Electronics", "Apple", "iPhone 15 Pro Max", 1299.99, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80"),
    ("Electronics", "Sony", "4K Smart LED TV", 799.99, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80"),
    ("Fashion", "Nike", "Air Running Shoes", 129.99, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80"),
    ("Fashion", "Adidas", "Training Sports Jacket", 89.99, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80"),
    ("Fashion", "Zara", "Tailored Linen Shirt", 59.99, "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80"),
    ("Home & Kitchen", "Philips", "Air Fryer", 119.99, "https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=800&q=80"),
    ("Home & Kitchen", "Dyson", "Cordless Vacuum", 349.99, "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=800&q=80"),
    ("Home & Kitchen", "Nespresso", "Coffee Maker", 179.99, "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80"),
    ("Beauty", "L'Oréal", "Hydrating Face Cream", 29.99, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80"),
    ("Beauty", "The Body Shop", "Botanical Hair Serum", 24.99, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80"),
    ("Sports", "Under Armour", "Training Backpack", 74.99, "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=800&q=80"),
    ("Sports", "Nike", "Performance Yoga Mat", 39.99, "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80"),
    ("Accessories", "Boat", "Bluetooth Earbuds", 49.99, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80"),
    ("Accessories", "Samsung", "Wireless Charger", 39.99, "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=800&q=80"),
]


def build_product_record(item_id: int, index: int) -> Tuple[int, str, str, str, float, str, str]:
    seed = PRODUCT_SEED_DATA[index % len(PRODUCT_SEED_DATA)]
    category, brand, base_name, base_price, image_url = seed
    suffix = ["Lite", "Pro", "Max", "Plus", "Ultra"][index % 5]
    product_name = f"{brand} {base_name} {suffix}"
    price = round(base_price + (index % 7) * 12.5, 2)
    description = f"{product_name} designed for everyday use with premium craftsmanship and reliable performance."
    return item_id, product_name, category, brand, price, image_url, description


def load_real_user_ids(mapping_path: Path | None = None) -> List[int]:
    project_root = get_project_root()
    mapping_file = mapping_path or Path(project_root) / "data" / "processed" / "mappings" / "user_mapping.pkl"
    with mapping_file.open("rb") as handle:
        mapping = pickle.load(handle)

    if isinstance(mapping, dict):
        return [int(user_id) for user_id in mapping.keys()]
    return [int(user_id) for user_id in mapping]


def collect_recommended_item_ids(user_limit: int = 500, max_products: int = 10000) -> List[int]:
    engine = InferenceEngine()
    real_user_ids = load_real_user_ids()
    valid_user_ids: List[int] = []
    item_ids: Set[int] = set()

    for fallback_item in engine.popular_items:
        item_ids.add(int(fallback_item["item_id"]))

    total_users_checked = len(real_user_ids)
    skipped_users = 0

    for user_id in real_user_ids:
        normalized_user_id = int(user_id)
        if normalized_user_id <= 0 or normalized_user_id == -999999:
            skipped_users += 1
            continue
        valid_user_ids.append(normalized_user_id)

    logger.info("Loading users...")
    logger.info("Total available users: %d", total_users_checked)

    if not valid_user_ids:
        logger.warning("No valid users found in user mapping; using popular fallback items only.")
        return sorted(item_ids)

    sample_size = min(user_limit, len(valid_user_ids))
    sampled_users = random.sample(valid_user_ids, sample_size)
    logger.info("Selected users: %d", sample_size)

    for index, user_id in enumerate(sampled_users, start=1):
        if len(item_ids) >= max_products:
            break

        logger.info("Processing user %d/%d", index, sample_size)
        for source_name in ["hybrid", "als", "content"]:
            try:
                if source_name == "hybrid":
                    results = engine.recommend_hybrid(user_id=user_id, top_n=10)
                elif source_name == "als":
                    results = engine.recommend_als(user_id=user_id, top_n=10)
                else:
                    results = engine.recommend_content_user(user_id=user_id, top_n=10)
            except Exception:
                continue

            for item in results:
                if isinstance(item, tuple):
                    item_id = int(item[0])
                else:
                    item_id = int(item.get("item_id"))
                item_ids.add(item_id)
                if len(item_ids) >= max_products:
                    break
            if len(item_ids) >= max_products:
                break

        logger.info("Unique item IDs collected: %d", len(item_ids))

    logger.info(
        "Metadata generation summary: total users checked=%d, valid users used=%d, unique item_ids collected=%d",
        total_users_checked,
        len(sampled_users),
        len(item_ids),
    )
    logger.info("Skipped %d invalid users before recommendation generation.", skipped_users)
    return sorted(item_ids)


def generate_metadata(output_path: Path, user_limit: int = 500, target_count: int = 10000) -> Path:
    project_root = get_project_root()
    output_path = output_path or project_root / "data" / "product_metadata.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    recommended_ids = collect_recommended_item_ids(user_limit=user_limit, max_products=target_count)
    item_ids = list(recommended_ids)[:target_count]

    random.seed(42)
    random.shuffle(item_ids)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item_id", "product_name", "category", "brand", "price", "image_url", "description"])
        for idx, item_id in enumerate(item_ids):
            writer.writerow(build_product_record(int(item_id), idx))

    logger.info("Generated metadata successfully.")
    logger.info("Products created: %d", len(item_ids))
    logger.info("Saved: %s", output_path)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate product metadata from sampled recommendation outputs.")
    parser.add_argument("--users", type=int, default=500, help="Number of valid users to sample for metadata generation")
    parser.add_argument("--max-products", type=int, default=10000, help="Maximum number of unique products to generate")
    parser.add_argument("--output", type=Path, default=Path(get_project_root()) / "data" / "product_metadata.csv", help="Path to the output CSV")
    args = parser.parse_args()

    output = generate_metadata(output_path=args.output, user_limit=args.users, target_count=args.max_products)
    print(f"Generated metadata catalog at {output}")
