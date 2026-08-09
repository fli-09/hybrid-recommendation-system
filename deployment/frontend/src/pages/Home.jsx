import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  BadgeCheck,
  Compass,
  Heart,
  LayoutGrid,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  UserRound,
} from "lucide-react";
import {
  getUserRecommendations,
  getContentRecommendations,
  ApiError,
} from "../api/recommendationApi.js";
import { searchCatalog } from "../utils/resolveProduct.js";
import RecommendationCard from "../components/RecommendationCard.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";

const DEFAULT_USER_ID = 1150086;
const COLD_START_USER_ID = -999999;

function Section({ title, subtitle, recommendations = [], accentClass }) {
  if (!recommendations.length) return null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6"
    >
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
        </div>
        <div className={`rounded-full px-3 py-1 text-xs font-semibold ${accentClass}`}>
          {recommendations.length} items
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
    </motion.section>
  );
}

export default function Home() {
  const [userId, setUserId] = useState(String(DEFAULT_USER_ID));
  const [topN, setTopN] = useState(10);
  const [searchQuery, setSearchQuery] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [similarRecommendations, setSimilarRecommendations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [feedSource, setFeedSource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState(null);
  const searchDebounce = useRef(null);

  const loadFeed = useCallback(async (selectedUserId = userId, selectedTopN = topN) => {
    setLoading(true);
    setError(null);

    try {
      const [personalizedResponse, contentResponse] = await Promise.all([
        getUserRecommendations(Number(selectedUserId), selectedTopN),
        getContentRecommendations(Number(selectedUserId), selectedTopN),
      ]);

      setRecommendations(personalizedResponse.recommendations);
      setSimilarRecommendations(contentResponse.recommendations);
      setFeedSource(
        personalizedResponse.recommendations.some((item) => item.source === "Popular") ? "Popular" : "Hybrid"
      );
    } catch (err) {
      setRecommendations([]);
      setSimilarRecommendations([]);
      setFeedSource(null);
      setError(
        err instanceof ApiError
          ? err.message
          : "Failed to load personalized recommendations."
      );
    } finally {
      setLoading(false);
    }
  }, [userId, topN]);

  useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  const handleSearch = (event) => {
    event.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    setSearchLoading(true);
    setError(null);

    if (searchDebounce.current) {
      clearTimeout(searchDebounce.current);
    }

    searchDebounce.current = setTimeout(() => {
      try {
        const results = searchCatalog(query, 8);
        setSearchResults(results);
      } catch (err) {
        setSearchResults([]);
        setError("Search failed due to an internal catalog error.");
      } finally {
        setSearchLoading(false);
      }
    }, 300);
  };

  const popularItems = recommendations.filter((item) => item.source === "Popular");
  const personalizedItems = recommendations.filter((item) => item.source !== "Popular");
  const userType = userId === String(COLD_START_USER_ID) ? "Cold Start User" : "Existing User";

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
              <Sparkles className="h-3.5 w-3.5" />
              Intelligence Layer
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              AI-Powered Product Discovery
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-400 sm:text-base">
              Hybrid recommendation engine combining collaborative filtering and product intelligence.
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
                max={100}
                value={topN}
                onChange={(event) => setTopN(Number(event.target.value))}
                className="w-full rounded-xl border border-surface-border bg-surface px-3 py-2.5 text-sm text-white outline-none ring-accent/30 focus:ring-2"
              />
            </label>
            <button
              type="button"
              onClick={() => loadFeed()}
              className="mt-5 inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-muted sm:mt-auto"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => {
              setUserId(String(DEFAULT_USER_ID));
              loadFeed(DEFAULT_USER_ID, topN);
            }}
            className="rounded-full border border-surface-border px-3 py-1.5 text-xs text-slate-300 transition hover:border-accent/40 hover:text-white"
          >
            Known user: {DEFAULT_USER_ID}
          </button>
          <button
            type="button"
            onClick={() => {
              setUserId(String(COLD_START_USER_ID));
              loadFeed(COLD_START_USER_ID, topN);
            }}
            className="rounded-full border border-surface-border px-3 py-1.5 text-xs text-slate-300 transition hover:border-accent/40 hover:text-white"
          >
            Cold start: {COLD_START_USER_ID}
          </button>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-surface-border bg-surface-raised/70 p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <LayoutGrid className="h-4 w-4 text-accent-glow" />
              Recommendation Overview
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-surface-border bg-surface/70 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Feed source</p>
                <p className="mt-1 font-semibold text-white">{feedSource || "Hybrid"}</p>
              </div>
              <div className="rounded-xl border border-surface-border bg-surface/70 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Recommendations</p>
                <p className="mt-1 font-semibold text-white">{recommendations.length}</p>
              </div>
              <div className="rounded-xl border border-surface-border bg-surface/70 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Similar items</p>
                <p className="mt-1 font-semibold text-white">{similarRecommendations.length}</p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-surface-border bg-surface-raised/70 p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <BadgeCheck className="h-4 w-4 text-accent-glow" />
              User Profile
            </div>
            <div className="mt-4 space-y-3 text-sm text-slate-300">
              <div className="flex items-center justify-between rounded-xl border border-surface-border bg-surface/70 px-3 py-2">
                <span>User ID</span>
                <span className="font-semibold text-white">{userId}</span>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-surface-border bg-surface/70 px-3 py-2">
                <span>User Type</span>
                <span className="font-semibold text-white">{userType}</span>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-surface-border bg-surface/70 px-3 py-2">
                <span>Model Used</span>
                <span className="font-semibold text-white">ALS + Content Hybrid</span>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      <section className="glass-panel p-6">
        <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder='Try "phone", "shirt", or "coffee maker"'
              className="w-full rounded-xl border border-surface-border bg-surface py-3 pl-10 pr-4 text-sm text-white outline-none ring-accent/30 focus:ring-2"
            />
          </div>
          <button
            type="submit"
            disabled={searchLoading}
            className="rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-500 disabled:opacity-60"
          >
            {searchLoading ? "Searching..." : "Search Catalog"}
          </button>
        </form>
      </section>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      {loading ? (
        <LoadingSkeleton count={6} />
      ) : recommendations.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-surface-border bg-surface-raised p-10 text-center">
          <p className="text-lg font-medium text-white">No recommendations available</p>
          <p className="mt-2 text-sm text-slate-400">
            Try another user ID or confirm the backend is running.
          </p>
        </div>
      ) : (
        <>
          <Section
            title="Personalized Recommendations"
            subtitle="AI-ranked products based on your browsing and interaction history"
            recommendations={personalizedItems}
            accentClass="bg-indigo-500/15 text-indigo-300"
          />
          <Section
            title="Trending Products"
            subtitle="Popular products selected using popularity-based ranking"
            recommendations={popularItems}
            accentClass="bg-amber-500/15 text-amber-300"
          />
          <Section
            title="Similar Products"
            subtitle="Content similarity recommendations"
            recommendations={similarRecommendations}
            accentClass="bg-emerald-500/15 text-emerald-300"
          />
        </>
      )}

      {searchResults.length > 0 && (
        <section className="glass-panel p-6">
          <div className="mb-5 flex items-center gap-2 text-xl font-semibold text-white">
            <Compass className="h-5 w-5 text-accent-glow" />
            Search Results
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {searchResults.map((recommendation, index) => (
              <RecommendationCard
                key={`${recommendation.item_id}-${index}`}
                recommendation={recommendation}
                index={index}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
