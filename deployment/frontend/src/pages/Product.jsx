import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { AlertCircle, ArrowLeft, Sparkles, Star } from "lucide-react";
import { resolveProduct } from "../utils/resolveProduct.js";

export default function Product() {
    const { id } = useParams();
    const location = useLocation();
    const itemId = Number(id);
    const [product, setProduct] = useState(location.state?.product ?? null);
    const [similarProducts, setSimilarProducts] = useState([]);

    useEffect(() => {
        if (location.state?.product) {
            setProduct(location.state.product);
            setSimilarProducts([]);
            return;
        }

        const resolved = resolveProduct(itemId);
        if (resolved) {
            setProduct({
                ...resolved,
                recommendationSource: location.state?.source || "Unknown",
                recommendationScore: location.state?.score ?? null,
            });
        } else {
            setProduct({
                item_id: itemId,
                product_name: `Product ${itemId}`,
                category: "General",
                brand: "Unknown",
                price: 0,
                image_url: "",
                description: "Product metadata will appear when this item is opened from a recommendation response.",
            });
        }
        setSimilarProducts([]);
    }, [itemId, location.state]);

    const productSummary = useMemo(() => {
        if (!product) return null;
        return [
            { label: "Category", value: product.category || product.product?.category || "General" },
            { label: "Price", value: `$${Number(product.price ?? product.product?.price ?? 0).toFixed(2)}` },
            { label: "Rating", value: `${Number(product.rating ?? product.product?.rating ?? 0).toFixed(1)} ⭐` },
            { label: "Reviews", value: `${Number(product.reviewCount ?? product.product?.reviewCount ?? 0).toLocaleString()} reviews` },
            { label: "Item ID", value: product.item_id },
        ];
    }, [product]);

    if (!product) {
        return (
            <div className="glass-panel flex min-h-[40vh] items-center justify-center p-10 text-center">
                <p className="text-slate-300">Loading product details…</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <Link
                to="/"
                className="inline-flex items-center gap-2 text-sm font-medium text-slate-300 transition hover:text-white"
            >
                <ArrowLeft className="h-4 w-4" />
                Back to recommendations
            </Link>

            <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
                <div className="glass-panel overflow-hidden">
                    <img
                        src={
                            product.image_url ||
                            product.image ||
                            product.images?.[0] ||
                            product.product?.image_url ||
                            product.product?.image ||
                            "/products/electronics.jpg"
                        }
                        alt={product.title || product.product_name || product.name || `Product ${itemId}`}
                        className="h-[360px] w-full object-cover"
                        onError={(event) => {
                            event.currentTarget.src = "/products/electronics.jpg";
                        }}
                    />
                    <div className="p-6">
                        <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/15 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-accent-glow">
                            <Sparkles className="h-3.5 w-3.5" />
                            Product Detail
                        </div>
                        <h1 className="text-3xl font-bold text-white">{product.title || product.product_name || product.name || `Product ${itemId}`}</h1>
                        <p className="mt-3 text-sm leading-6 text-slate-400">{product.description || product.product?.description || ""}</p>
                        {product.recommendationSource && (
                            <div className="mt-4 rounded-2xl border border-surface-border bg-surface-raised/80 p-4 text-sm text-slate-300">
                                <p className="text-xs uppercase tracking-wide text-slate-500">Why this recommendation</p>
                                <p className="mt-2 text-sm text-slate-100">
                                    Recommended because {product.recommendationSource === "ALS" ? "it matches items you have interacted with" : product.recommendationSource === "Content" ? "it is similar to products you viewed" : product.recommendationSource === "Popular" ? "it's a trending pick for new users" : "it matches your recent activity"}.
                                </p>
                                {product.recommendationScore !== null && (
                                    <p className="mt-2 text-xs text-slate-500">Score: {Number(product.recommendationScore).toFixed(3)}</p>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="glass-panel p-6">
                        <div className="flex items-center justify-between gap-4">
                            <div>
                                <p className="text-sm font-medium text-slate-400">Current price</p>
                                <p className="mt-1 text-3xl font-bold text-white">${Number(product.price ?? product.product?.price ?? 0).toFixed(2)}</p>
                            </div>
                            <div className="rounded-2xl bg-amber-500/15 p-3 text-amber-300">
                                <Star className="h-6 w-6 fill-current" />
                            </div>
                        </div>

                        <div className="mt-6 grid gap-3 sm:grid-cols-3">
                            {productSummary.map((item) => (
                                <div key={item.label} className="rounded-xl border border-surface-border bg-surface-raised/70 p-3">
                                    <p className="text-xs uppercase tracking-wide text-slate-500">{item.label}</p>
                                    <p className="mt-1 text-sm font-semibold text-white">{item.value}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="glass-panel p-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-semibold text-white">Similar products</h2>
                            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-300">
                                Pending backend route
                            </span>
                        </div>
                        <div className="mt-4 rounded-2xl border border-dashed border-surface-border bg-surface-raised/60 p-5 text-sm text-slate-400">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="mt-0.5 h-4 w-4 text-amber-300" />
                                <p>
                                    The backend currently exposes recommendation logic but does not yet provide a dedicated similar-items API route. This placeholder is shown until the backend adds it.
                                </p>
                            </div>
                        </div>
                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                            {similarProducts.map((entry) => (
                                <Link
                                    key={entry.item_id}
                                    to={`/product/${entry.item_id}`}
                                    className="rounded-xl border border-surface-border bg-surface-raised/70 p-3 transition hover:border-accent/40"
                                >
                                    <p className="text-sm font-semibold text-white">{entry.name}</p>
                                    <p className="mt-1 text-xs text-slate-400">{entry.category}</p>
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
