import catalogData from "../data/catalog.json";

const catalog = Array.isArray(catalogData) ? catalogData : [];
const cache = new Map();
const CATALOG_SIZE = catalog.length;

function stableHash(itemId) {
  const text = String(itemId).trim();
  if (!text) {
    return 0;
  }

  const numericValue = Number(text);
  if (Number.isFinite(numericValue)) {
    const normalized = Math.abs(Math.trunc(numericValue));
    if (normalized >= 1 && normalized <= CATALOG_SIZE) {
      return normalized - 1;
    }
    return normalized;
  }

  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function normalizeImageUrl(url) {
  if (!url || typeof url !== "string") {
    return "";
  }

  const normalized = url.trim();
  if (normalized.startsWith("/images/products/")) {
    return normalized;
  }
  if (normalized.startsWith("images/products/")) {
    return `/${normalized}`;
  }
  if (normalized.startsWith("/products/")) {
    return normalized;
  }
  if (normalized.startsWith("products/")) {
    return `/${normalized}`;
  }
  return normalized;
}

const SEARCH_SYNONYMS = {
  coffee: ["coffee", "coffee maker", "espresso", "latte", "beverage", "drink", "groceries"],
  phone: ["phone", "smartphone", "mobile", "cellphone", "android", "iphone", "smartphones", "mobile-accessories"],
  shirt: ["shirt", "tshirt", "t-shirt", "top", "tops", "mens-shirts", "womens-shirts", "apparel", "clothing"],
  laptop: ["laptop", "notebook", "macbook", "ultrabook", "computer", "laptops"],
  shoe: ["shoe", "sneaker", "boots", "footwear", "mens-shoes", "womens-shoes"],
  watch: ["watch", "smartwatch", "timepiece", "wristwatch"],
};

function tokenize(text) {
  if (!text || typeof text !== "string") {
    return [];
  }
  return text
    .toLowerCase()
    .match(/\b[\w&'-]+\b/g)
    ?.map((token) => token.trim())
    .filter(Boolean) || [];
}

function buildSearchTerms(query) {
  const baseTerms = tokenize(query);
  const expanded = new Set(baseTerms);
  baseTerms.forEach((term) => {
    const synonyms = SEARCH_SYNONYMS[term];
    if (Array.isArray(synonyms)) {
      synonyms.forEach((synonym) => expanded.add(synonym));
    }
  });
  return Array.from(expanded);
}

function scoreCatalogItem(item, terms) {
  const fullText = [item.title, item.brand, item.category, item.subcategory, item.description]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  const tokens = tokenize(fullText);
  let score = 0;

  terms.forEach((term) => {
    if (!term) return;
    const normalizedTerm = term.toLowerCase();
    const termTokens = tokenize(normalizedTerm);

    if (termTokens.every((token) => tokens.includes(token))) {
      score += 20;
    } else if (fullText.includes(normalizedTerm)) {
      score += 10;
    }

    if (item.category && item.category.toLowerCase() === normalizedTerm) {
      score += 15;
    }
    if (item.subcategory && item.subcategory.toLowerCase() === normalizedTerm) {
      score += 10;
    }
  });

  if (item.title && item.title.toLowerCase().startsWith(terms[0])) {
    score += 8;
  }
  return score;
}

export function resolveProduct(itemId) {
  const key = String(itemId);
  if (cache.has(key)) {
    return cache.get(key);
  }

  if (!CATALOG_SIZE) {
    return undefined;
  }

  const index = stableHash(key) % CATALOG_SIZE;
  const product = catalog[index];
  if (!product) {
    cache.set(key, undefined);
    return undefined;
  }

  const images = Array.isArray(product.images)
    ? product.images.map(normalizeImageUrl).filter(Boolean)
    : [];
  const firstImage = images.length ? images[0] : "";

  const resolved = {
    ...product,
    item_id: Number(itemId),
    catalogIndex: index,
    images,
    image_url: firstImage,
    image: firstImage,
  };
  cache.set(key, resolved);
  return resolved;
}

export function getCatalogItemIdForIndex(index) {
  const idx = Number(index);
  if (!Number.isFinite(idx) || CATALOG_SIZE === 0) {
    return undefined;
  }
  return idx + 1;
}

export function searchCatalog(query, maxResults = 10) {
  const normalizedQuery = String(query || "").trim();
  if (!normalizedQuery) {
    return [];
  }

  const terms = buildSearchTerms(normalizedQuery);
  const scored = catalog
    .map((item, index) => ({
      item,
      index,
      score: scoreCatalogItem(item, terms),
    }))
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title))
    .slice(0, maxResults)
    .map(({ item, index, score }) => ({
      item_id: getCatalogItemIdForIndex(index),
      score,
      source: "Search",
    }));

  if (scored.length === 0) {
    return catalog.slice(0, maxResults).map((item, index) => ({
      item_id: getCatalogItemIdForIndex(index),
      score: 0,
      source: "Search",
    }));
  }

  return scored;
}

export function getAllCatalogProducts() {
  return catalog;
}
