import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const frontendRoot = path.resolve(path.dirname(__filename), "..");
const catalogPath = path.join(frontendRoot, "src", "data", "catalog.json");
const outputDir = path.join(frontendRoot, "public", "images", "products");

const categoryQueries = {
  Electronics: "electronics gadget",
  Apparel: "fashion clothing",
  "Home & Kitchen": "home kitchen appliances",
  Beauty: "beauty skincare product",
  "Sports & Outdoors": "sports outdoors gear",
  Books: "book stack reading",
  Toys: "children toys play",
  Grocery: "grocery food packaging",
};

const MAX_IMAGES_PER_PRODUCT = 2;
const USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)";

function ensureDirectory(directory) {
  if (!fs.existsSync(directory)) {
    fs.mkdirSync(directory, { recursive: true });
  }
}

async function downloadImage(url, filePath) {
  const response = await fetch(url, {
    headers: {
      "User-Agent": USER_AGENT,
      Accept: "image/jpeg,image/png,image/*;q=0.8,*/;q=0.5",
    },
  });

  if (!response.ok || !response.body) {
    throw new Error(`Image request failed with status ${response.status}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(filePath, buffer);
}

function createPlaceholderImage(filePath, category, catalogId, index) {
  const content = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1f2937" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
  </defs>
  <rect width="800" height="800" fill="url(#g)" />
  <text x="50%" y="42%" dominant-baseline="middle" text-anchor="middle" font-family="Inter, sans-serif" font-size="48" fill="#f8fafc" font-weight="700">${category}</text>
  <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle" font-family="Inter, sans-serif" font-size="28" fill="#94a3b8">${catalogId} • Image ${index}</text>
</svg>`;
  fs.writeFileSync(filePath, content, "utf8");
}

function sampleImageUrl(query, seed) {
  const encodedQuery = encodeURIComponent(query);
  return `https://source.unsplash.com/featured/800x800?${encodedQuery}&sig=${seed}`;
}

async function fetchProductImages(catalog) {
  ensureDirectory(outputDir);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < catalog.length; i += 1) {
    const product = catalog[i];
    const query = categoryQueries[product.category] || product.category || "product";

    for (let imageIndex = 1; imageIndex <= MAX_IMAGES_PER_PRODUCT; imageIndex += 1) {
      const fileName = `${product.catalogId}_${imageIndex}.jpg`;
      const filePath = path.join(outputDir, fileName);
      if (fs.existsSync(filePath)) {
        successCount += 1;
        continue;
      }

      const seed = i * MAX_IMAGES_PER_PRODUCT + imageIndex;
      const imageUrl = sampleImageUrl(query, seed);

      try {
        console.log(`Downloading ${fileName} from ${imageUrl}`);
        await downloadImage(imageUrl, filePath);
        console.log(`Saved ${fileName}`);
        successCount += 1;
      } catch (error) {
        console.warn(`Failed to fetch ${fileName}: ${error.message}. Falling back to placeholder.`);
        failureCount += 1;
        const svgFilePath = filePath.replace(/\.jpg$/, ".svg");
        createPlaceholderImage(svgFilePath, product.category, product.catalogId, imageIndex);
      }
    }
  }

  console.log(`Catalog image fetch complete. ${successCount} images downloaded, ${failureCount} fallbacks created.`);
}

function loadCatalog() {
  if (!fs.existsSync(catalogPath)) {
    throw new Error(`Catalog file not found at ${catalogPath}`);
  }
  const source = fs.readFileSync(catalogPath, "utf8");
  return JSON.parse(source);
}

async function main() {
  const catalog = loadCatalog();
  console.log(`Preparing to download images for ${catalog.length} catalog products.`);
  await fetchProductImages(catalog);
  console.log("Catalog image fetch process complete.");
}

main().catch((error) => {
  console.error("Failed to complete catalog image fetch:", error);
  process.exit(1);
});
