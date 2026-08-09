import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import RecommendationCard from "./RecommendationCard.jsx";

export default function ProductCarousel({ title, subtitle, recommendations = [] }) {
  const trackRef = useRef(null);

  const scroll = (direction) => {
    if (!trackRef.current) return;
    const amount = direction === "left" ? -320 : 320;
    trackRef.current.scrollBy({ left: amount, behavior: "smooth" });
  };

  if (!recommendations.length) {
    return null;
  }

  return (
    <section className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-white sm:text-2xl">{title}</h2>
          {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
        </div>
        <div className="hidden gap-2 sm:flex">
          <button
            type="button"
            onClick={() => scroll("left")}
            className="rounded-xl border border-surface-border bg-surface-raised p-2 text-slate-300 transition hover:text-white"
            aria-label="Scroll left"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => scroll("right")}
            className="rounded-xl border border-surface-border bg-surface-raised p-2 text-slate-300 transition hover:text-white"
            aria-label="Scroll right"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div
        ref={trackRef}
        className="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {recommendations.map((recommendation, index) => (
          <div
            key={`${recommendation.item_id}-${index}`}
            className="w-[280px] shrink-0 snap-start sm:w-[300px]"
          >
            <RecommendationCard recommendation={recommendation} index={index} />
          </div>
        ))}
      </div>
    </section>
  );
}
