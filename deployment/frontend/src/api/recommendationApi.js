const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  constructor(message, status = null, detail = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  let response;

  try {
    response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch {
    throw new ApiError(
      "Unable to reach the recommendation API. Ensure the backend is running on port 8000.",
      null
    );
  }

  let payload = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    payload = await response.json();
  }

  if (!response.ok) {
    const detail =
      payload?.detail ||
      payload?.message ||
      `Request failed with status ${response.status}`;
    throw new ApiError(
      typeof detail === "string" ? detail : JSON.stringify(detail),
      response.status,
      detail
    );
  }

  return payload;
}

function normalizeRecommendations(items = [], defaultSource = null) {
  return items.map((item) => {
    const itemId = Number(item.item_id);
    const price = Number(item.price ?? item.product?.price ?? 0);
    const productName = item.product_name || item.product?.product_name || item.name || item.product?.name || `Product ${itemId}`;
    const category = item.category || item.product?.category || "General";
    const brand = item.brand || item.product?.brand || "Unknown";
    const imageUrl = item.image_url || item.image || item.product?.image_url || item.product?.image || "";
    const description = item.description || item.product?.description || "";

    return {
      item_id: itemId,
      score: Number(item.score),
      source: item.source || defaultSource,
      product_name: productName,
      category,
      brand,
      price,
      image_url: imageUrl,
      description,
      product: {
        item_id: itemId,
        name: productName,
        category,
        brand,
        price,
        image_url: imageUrl,
        description,
      },
    };
  });
}

export async function checkHealth() {
  const data = await request("/health");
  return {
    status: data.status,
    modelsLoaded: Boolean(data.models_loaded),
    isHealthy: data.status === "healthy" && data.models_loaded === true,
  };
}

export async function getUserRecommendations(userId, topN = 10) {
  const data = await request(
    `/recommend/${encodeURIComponent(userId)}?top_n=${topN}`
  );

  return {
    userId: data.user_id,
    modelUsed: "HybridFeed",
    recommendations: normalizeRecommendations(data.recommendations),
  };
}

export async function getHybridRecommendations(userId, topN = 10, weights = null) {
  const body = { user_id: userId, top_n: topN };
  if (weights) {
    body.weights = weights;
  }

  const data = await request("/recommend/hybrid", {
    method: "POST",
    body: JSON.stringify(body),
  });

  return {
    userId: data.user_id,
    modelUsed: data.model_used,
    recommendations: normalizeRecommendations(data.recommendations, "Hybrid"),
    metadata: data.metadata ?? null,
  };
}

export async function getAlsRecommendations(userId, topN = 10) {
  const data = await request("/recommend/als", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, top_n: topN }),
  });

  return {
    userId: data.user_id,
    modelUsed: data.model_used,
    recommendations: normalizeRecommendations(data.recommendations, "ALS"),
    metadata: data.metadata ?? null,
  };
}

export async function getContentRecommendations(userId, topN = 10) {
  const data = await request("/recommend/content", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, top_n: topN }),
  });

  return {
    userId: data.user_id,
    modelUsed: data.model_used,
    recommendations: normalizeRecommendations(data.recommendations, "Content"),
    metadata: data.metadata ?? null,
  };
}

export async function searchProducts(query, topN = 10) {
  const data = await request("/recommend/search", {
    method: "POST",
    body: JSON.stringify({ query, top_n: topN }),
  });

  return {
    modelUsed: data.model_used,
    recommendations: normalizeRecommendations(data.recommendations, "Search"),
    metadata: data.metadata ?? null,
  };
}

export { API_BASE_URL };
