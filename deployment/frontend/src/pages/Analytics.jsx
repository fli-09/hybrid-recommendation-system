import { motion } from "framer-motion";
import { BarChart3, TrendingUp } from "lucide-react";

const metrics = [
    { label: "Precision@10", value: "0.0100", description: "Fraction of the top-10 recommendations that are relevant", accent: "text-emerald-300" },
    { label: "Recall@10", value: "0.1000", description: "Share of relevant items recovered in the top-10 slice", accent: "text-sky-300" },
    { label: "Hit Rate@10", value: "0.1000", description: "Users with at least one relevant result in the top 10", accent: "text-violet-300" },
    { label: "Catalog Coverage", value: "0.0016", description: "Fraction of the product catalog surfaced by recommendations", accent: "text-amber-300" },
];

export default function Analytics() {
    return (
        <div className="space-y-8">
            <motion.section
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel overflow-hidden p-6 sm:p-8"
            >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                    <div className="max-w-2xl">
                        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-accent/15 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-accent-glow">
                            <BarChart3 className="h-3.5 w-3.5" />
                            Recommendation Analytics
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                            Offline evaluation metrics for the recommendation stack
                        </h1>
                        <p className="mt-3 text-sm leading-6 text-slate-400 sm:text-base">
                            The dashboard uses the project’s existing evaluation metrics to present a realistic performance snapshot without introducing synthetic data.
                        </p>
                    </div>
                    <div className="flex items-center gap-2 rounded-2xl border border-surface-border bg-surface-raised px-4 py-3 text-sm text-slate-300">
                        <TrendingUp className="h-4 w-4 text-accent-glow" />
                        Offline snapshot • Verified from project metrics
                    </div>
                </div>
            </motion.section>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {metrics.map((metric) => (
                    <motion.div
                        key={metric.label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-panel p-6"
                    >
                        <p className="text-sm font-medium text-slate-400">{metric.label}</p>
                        <p className={`mt-3 text-3xl font-semibold ${metric.accent}`}>{metric.value}</p>
                        <p className="mt-2 text-sm text-slate-400">{metric.description}</p>
                    </motion.div>
                ))}
            </div>

            <div className="glass-panel p-6">
                <h2 className="text-xl font-semibold text-white">What the metrics indicate</h2>
                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                    <div className="rounded-2xl border border-surface-border bg-surface-raised/70 p-5 text-sm text-slate-300">
                        <p className="font-semibold text-white">Model quality</p>
                        <p className="mt-2">
                            The current offline metrics show that the hybrid system is still in a research-oriented stage, with relatively low precision and recall at the top-10 level.
                        </p>
                    </div>
                    <div className="rounded-2xl border border-surface-border bg-surface-raised/70 p-5 text-sm text-slate-300">
                        <p className="font-semibold text-white">Recommendation experience</p>
                        <p className="mt-2">
                            The UI now highlights the same evaluation values that the project documentation exposes, making the dashboard feel more like a production analytics workspace.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
