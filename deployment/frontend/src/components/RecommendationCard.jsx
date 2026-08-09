import { useMemo } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowUpRight, Star } from "lucide-react";
import { resolveProduct } from "../utils/resolveProduct.js";

const sourceStyles = {
  Hybrid: "bg-indigo-500/15 text-indigo-300",
  Popular: "bg-amber-500/15 text-amber-300",
  ALS: "bg-sky-500/15 text-sky-300",
  Content: "bg-emerald-500/15 text-emerald-300",
  Search: "bg-violet-500/15 text-violet-300",
};

const sourceReasonMap = {
  Hybrid: "Combined collaborative and content signals",
  ALS: "Because you interacted with similar items",
  Content: "Similar to items you've viewed",
  Popular: "Trending pick for new users",
  Search: "Search match from product catalog",
};

export default function RecommendationCard({ recommendation, index = 0 }) {
  const {
    item_id,
    score,
    source,
    product_name,
    category,
    brand,
    price,
    description,
    product,
  } = recommendation;

  const resolvedProduct = resolveProduct(item_id);
  const badgeClass = sourceStyles[source] || "bg-slate-500/15 text-slate-300";
  const displayName = resolvedProduct?.title || product_name || product?.name || `Product ${item_id}`;
  const displayCategory = resolvedProduct?.category || category || product?.category || "General";
  const displayBrand = resolvedProduct?.brand || brand || product?.brand || "Unknown";
  const displayPrice = resolvedProduct?.price ?? price ?? product?.price ?? 0;
  const displayDescription = resolvedProduct?.description || description || product?.description || "";
  const displayImages =
    resolvedProduct?.images ||
    product?.images ||
    [product?.image_url || product?.image].filter(Boolean);
  const displayRating = Number(resolvedProduct?.rating ?? product?.rating ?? product?.product?.rating ?? 0).toFixed(1);
  const displayReviewCount = Number(resolvedProduct?.reviewCount ?? product?.reviewCount ?? product?.product?.reviewCount ?? 0).toLocaleString();
  const algorithmScore = score !== null && score !== undefined ? Number(score).toFixed(3) : null;
  const reasonText = sourceReasonMap[source] || "Recommended based on your recent activity";
  const categoryPlaceholder = useMemo(() => {
    const normalizedCategory = (displayCategory || "").toLowerCase();
    if (normalizedCategory.includes("beaut")) return "/products/beauty.jpg";
    if (normalizedCategory.includes("fashion") || normalizedCategory.includes("cloth") || normalizedCategory.includes("wear")) return "/products/fashion.jpg";
    if (normalizedCategory.includes("sport")) return "/products/sports.jpg";
    if (normalizedCategory.includes("accessor")) return "/products/accessories.jpg";
    if (normalizedCategory.includes("home") || normalizedCategory.includes("kitchen")) return "/products/home.jpg";
    if (normalizedCategory.includes("book") || normalizedCategory.includes("read")) return "/products/home.jpg";
    if (normalizedCategory.includes("grocery") || normalizedCategory.includes("food")) return "/products/home.jpg";
    if (normalizedCategory.includes("toy") || normalizedCategory.includes("game")) return "/products/home.jpg";
    return "/products/electronics.jpg";
  }, [displayCategory]);

  const imageSrc = displayImages && displayImages.length ? displayImages[0] : categoryPlaceholder;
  const imageFallback = imageSrc || categoryPlaceholder;

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.35 }}
      className="group flex h-full flex-col overflow-hidden rounded-2xl border border-surface-border bg-surface-card shadow-lg shadow-black/20 transition hover:-translate-y-1 hover:border-accent/40"
    >
      <div className="relative h-[220px] shrink-0 overflow-hidden bg-surface-raised">
        <img
          src={imageFallback}
          alt={displayName}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(event) => {
            if (event.currentTarget.src !== categoryPlaceholder) {
              event.currentTarget.src = categoryPlaceholder;
            }
          }}
        />
        {source && (
          <span
            className={`absolute left-3 top-3 rounded-full px-2.5 py-1 text-xs font-semibold ${badgeClass}`}
          >
            {source}
          </span>
        )}
        <div className="absolute right-3 bottom-3 rounded-2xl bg-black/60 px-3 py-2 text-xs text-slate-100 backdrop-blur-sm">
          <div>{reasonText}</div>
          {algorithmScore && (
            <div className="mt-1 text-[11px] text-slate-300">
              {source || "Hybrid"} score: {algorithmScore}
            </div>
          )}
        </div>
      </div>
      <div className="flex flex-1 flex-col space-y-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              {displayCategory}
            </p>
            <h3 className="mt-1 line-clamp-2 overflow-hidden text-ellipsis text-sm font-semibold text-white">
              {displayName}
            </h3>
          </div>
          <Link
            to={`/product/${item_id}`}
            state={{ product: resolvedProduct, source, score }}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-surface-raised hover:text-accent-glow"
            aria-label={`View product ${item_id}`}
          >
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-sm text-slate-400">Brand</p>
            <p className="truncate text-sm font-semibold text-white">{displayBrand}</p>
          </div>
          <div className="relative flex shrink-0 items-center gap-2">
            <Star className="h-4 w-4 fill-current text-amber-300" />
            <span className="text-sm font-semibold text-white">{displayRating}</span>
            <span className="text-xs text-slate-400">({displayReviewCount} reviews)</span>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <p className="text-lg font-bold text-white">
            {displayPrice === null ? "Price unavailable" : `$${displayPrice.toFixed(2)}`}
          </p>
          <p className="shrink-0 text-xs uppercase tracking-wide text-slate-500">Item {item_id}</p>
        </div>

        <p className="line-clamp-3 min-h-[3.75rem] text-xs leading-5 text-slate-400">
          {displayDescription || "No description available."}
        </p>
      </div>
    </motion.article>
  );
}
