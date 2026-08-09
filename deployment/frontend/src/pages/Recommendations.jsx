import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Layers3, RefreshCw, UserRound } from "lucide-react";
import {
    ApiError,
    getAlsRecommendations,
    getContentRecommendations,
    getHybridRecommendations,
} from "../api/recommendationApi.js";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";

const DEFAULT_USER_ID = 1150086;

const modelProfiles = {
    Hybrid: {
        algorithm: "Hybrid fusion",
        strength: "Balances collaborative behavior with product similarity.",
        weakness: "Can be less sharp for sparse cold-start behavior.",
    },
    ALS: {
        algorithm: "ALS collaborative filtering",
        strength: "Captures user-item interaction patterns effectively.",
        weakness: "Needs richer interaction history for strong personalization.",
    },
    Content: {
        algorithm: "TF-IDF content similarity",
        strength: "Handles product metadata and item similarity well.",
        weakness: "Less aware of hidden behavioral trends than ALS.",
    },
};

function Section({ title, subtitle, recommendations, accentClass, profile }) {
    if (!recommendations.length) {
        return null;
    }

    const avgScore = useMemo(() => {
        if (!recommendations.length) return "—";
        const total = recommendations.reduce((sum, item) => sum + Number(item.score || 0), 0);
        return (total / recommendations.length).toFixed(3);
    }, [recommendations]);

    return (
        <section className="glass-panel p-6">
            <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                    <h2 className="text-xl font-semibold text-white">{title}</h2>
                    <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
                </div>
                <div className={`rounded-full px-3 py-1 text-xs font-semibold ${accentClass}`}>
                    {recommendations.length} items
                </div>
            </div>

            <div className="mb-6 grid gap-4 rounded-2xl border border-surface-border bg-surface-raised/70 p-4 lg:grid-cols-3">
                <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Algorithm</p>
                    <p className="mt-1 font-semibold text-white">{profile.algorithm}</p>
                </div>
                <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Strength</p>
                    <p className="mt-1 text-sm text-slate-300">{profile.strength}</p>
                </div>
                <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Recommendation Score</p>
                    <p className="mt-1 font-semibold text-accent-glow">{avgScore}</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {recommendations.map((recommendation, index) => (
                    <RecommendationCard
                        key={`${recommendation.item_id}-${index}`}
                        recommendation={recommendation}
                        index={index}
                    />
                ))}
            </div>
        </section>
    );
}

export default function Recommendations() {
    const [userId, setUserId] = useState(String(DEFAULT_USER_ID));
    const [topN, setTopN] = useState(8);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [hybridRecommendations, setHybridRecommendations] = useState([]);
    const [alsRecommendations, setAlsRecommendations] = useState([]);
    const [contentRecommendations, setContentRecommendations] = useState([]);

    const loadAll = async (selectedUserId = userId, selectedTopN = topN) => {
        setLoading(true);
        setError(null);

        try {
            const [hybrid, als, content] = await Promise.all([
                getHybridRecommendations(Number(selectedUserId), selectedTopN),
                getAlsRecommendations(Number(selectedUserId), selectedTopN),
                getContentRecommendations(Number(selectedUserId), selectedTopN),
            ]);

            setHybridRecommendations(hybrid.recommendations);
            setAlsRecommendations(als.recommendations);
            setContentRecommendations(content.recommendations);
        } catch (err) {
            setHybridRecommendations([]);
            setAlsRecommendations([]);
            setContentRecommendations([]);
            setError(err instanceof ApiError ? err.message : "Unable to load comparison feed.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAll();
    }, []);

    return (
        <div className="space-y-8">
            <motion.section
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel overflow-hidden p-6 sm:p-8"
            >
                <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
                    <div className="max-w-2xl">
                        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-accent/15 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-accent-glow">
                            <Layers3 className="h-3.5 w-3.5" />
                            Model Comparison
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                            Compare the hybrid, ALS, and content models side by side
                        </h1>
                        <p className="mt-3 text-sm leading-6 text-slate-400 sm:text-base">
                            The dashboard compares the three recommendation endpoints using the live backend payload and highlights each model’s qualitative strengths.
                        </p>
                    </div>

                    <div className="grid w-full max-w-xl gap-3 sm:grid-cols-[1fr_auto_auto]">
                        <label className="block">
                            <span className="mb-1 flex items-center gap-2 text-xs font-medium text-slate-400">
                                <UserRound className="h-3.5 w-3.5" />
                                User ID
                            </span>
                            <input
                                type="number"
                                value={userId}
                                onChange={(event) => setUserId(event.target.value)}
                                className="w-full rounded-xl border border-surface-border bg-surface px-3 py-2.5 text-sm text-white outline-none ring-accent/30 focus:ring-2"
                            />
                        </label>
                        <label className="block">
                            <span className="mb-1 block text-xs font-medium text-slate-400">Top N</span>
                            <input
                                type="number"
                                min={1}
                                max={50}
                                value={topN}
                                onChange={(event) => setTopN(Number(event.target.value))}
                                className="w-full rounded-xl border border-surface-border bg-surface px-3 py-2.5 text-sm text-white outline-none ring-accent/30 focus:ring-2"
                            />
                        </label>
                        <button
                            type="button"
                            onClick={() => loadAll()}
                            className="mt-5 inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-muted sm:mt-auto"
                        >
                            <RefreshCw className="h-4 w-4" />
                            Refresh
                        </button>
                    </div>
                </div>
            </motion.section>

            {error && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                    {error}
                </div>
            )}

            {loading ? (
                <LoadingSkeleton count={6} />
            ) : (
                <>
                    <Section
                        title="Hybrid Recommendations"
                        subtitle="Weighted fusion of ALS and content-based signals"
                        recommendations={hybridRecommendations}
                        accentClass="bg-indigo-500/15 text-indigo-300"
                        profile={modelProfiles.Hybrid}
                    />
                    <Section
                        title="ALS Recommendations"
                        subtitle="Behavioral recommendations from the collaborative model"
                        recommendations={alsRecommendations}
                        accentClass="bg-sky-500/15 text-sky-300"
                        profile={modelProfiles.ALS}
                    />
                    <Section
                        title="Content Recommendations"
                        subtitle="Similarity-based matches from the product metadata model"
                        recommendations={contentRecommendations}
                        accentClass="bg-emerald-500/15 text-emerald-300"
                        profile={modelProfiles.Content}
                    />
                </>
            )}
        </div>
    );
}
