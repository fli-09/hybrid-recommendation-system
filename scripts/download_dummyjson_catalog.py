import csv
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

API_URL = "https://dummyjson.com/products?limit=194"
REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_PRODUCTS_DIR = REPO_ROOT / "deployment" / "frontend" / "public" / "products"
CATALOG_JSON_PATH = REPO_ROOT / "deployment" / "frontend" / "src" / "data" / "catalog.json"
METADATA_CSV_PATH = REPO_ROOT / "data" / "product_metadata.csv"

EXTENSION_PATTERN = re.compile(r"\.([a-zA-Z0-9]+)(?:\?.*)?$")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_file_extension(url: str) -> str:
    parsed = urlparse(url)
    match = EXTENSION_PATTERN.search(parsed.path)
    if match:
        return f".{match.group(1).lower()}"
    return ".jpg"


def download_image(url: str, output_path: Path) -> bool:
    try:
        request = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        })
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                print(f"ERROR: {url} returned {response.status}")
                return False
            content = response.read()
            output_path.write_bytes(content)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: failed to download {url}: {exc}")
        return False


def fetch_dummyjson_products() -> list[dict]:
    print(f"Fetching DummyJSON product catalog from {API_URL}")
    request = urllib.request.Request(API_URL, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected response status: {response.status}")
        payload = response.read().decode("utf-8")
        data = json.loads(payload)
    products = data.get("products")
    if not isinstance(products, list):
        raise RuntimeError("Invalid DummyJSON response format")
    if len(products) == 0:
        raise RuntimeError("No products returned from DummyJSON")
    print(f"Downloaded metadata for {len(products)} DummyJSON products")
    return products


def build_catalog_records(products: list[dict]) -> list[dict]:
    catalog = []
    for product in products:
        product_id = int(product["id"])
        thumbnail = str(product.get("thumbnail", ""))
        ext = get_file_extension(thumbnail)
        local_image_name = f"{product_id}{ext}"
        local_image_url = f"/products/{local_image_name}"
        catalog_item = {
            "id": product_id,
            "title": str(product.get("title", "")).strip(),
            "description": str(product.get("description", "")).strip(),
            "category": str(product.get("category", "")).strip(),
            "brand": str(product.get("brand", "")).strip(),
            "price": float(product.get("price", 0.0)),
            "rating": float(product.get("rating", 0.0)),
            "stock": int(product.get("stock", 0)),
            "image_url": local_image_url,
            "images": [local_image_url],
            "thumbnail": thumbnail,
        }
        catalog.append(catalog_item)
    return catalog


def save_catalog_json(catalog: list[dict]) -> None:
    ensure_dir(CATALOG_JSON_PATH.parent)
    with open(CATALOG_JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2)
    print(f"Saved frontend catalog to {CATALOG_JSON_PATH}")


def save_metadata_csv(catalog: list[dict]) -> None:
    ensure_dir(METADATA_CSV_PATH.parent)
    with open(METADATA_CSV_PATH, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item_id", "product_name", "category", "brand", "price", "rating", "stock", "description", "image_url"])
        for product in catalog:
            writer.writerow([
                product["id"],
                product["title"],
                product["category"],
                product["brand"],
                f"{product['price']:.2f}",
                f"{product['rating']:.2f}",
                product["stock"],
                product["description"],
                product["image_url"],
            ])
    print(f"Saved metadata CSV to {METADATA_CSV_PATH}")


def download_images(catalog: list[dict]) -> tuple[int, int]:
    ensure_dir(FRONTEND_PRODUCTS_DIR)
    success = 0
    failure = 0
    for product in catalog:
        local_path = FRONTEND_PRODUCTS_DIR / Path(product["image_url"]).name
        url = product["thumbnail"]
        print(f"Downloading thumbnail for product {product['id']} -> {local_path.name}")
        if local_path.exists():
            print(f"  Skipping existing file {local_path.name}")
            success += 1
            continue
        if download_image(url, local_path):
            success += 1
        else:
            failure += 1
    return success, failure


def main() -> int:
    try:
        products = fetch_dummyjson_products()
        catalog = build_catalog_records(products)
        success, failure = download_images(catalog)
        save_catalog_json(catalog)
        save_metadata_csv(catalog)
        print("\nDownload complete")
        print(f"Images downloaded or already existing: {success}")
        print(f"Images failed: {failure}")
        return 0 if failure == 0 else 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
