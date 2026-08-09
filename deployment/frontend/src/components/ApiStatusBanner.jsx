import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { checkHealth, ApiError } from "../api/recommendationApi.js";

export default function ApiStatusBanner() {
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("Checking API health...");

  useEffect(() => {
    let active = true;

    async function loadHealth() {
      try {
        const health = await checkHealth();
        if (!active) return;

        if (health.isHealthy) {
          setStatus("healthy");
          setMessage("Backend connected — models loaded and ready.");
        } else {
          setStatus("warning");
          setMessage("Backend reachable but models are not fully loaded.");
        }
      } catch (error) {
        if (!active) return;
        setStatus("error");
        setMessage(
          error instanceof ApiError
            ? error.message
            : "Unexpected error while checking API health."
        );
      }
    }

    loadHealth();
    const interval = setInterval(loadHealth, 30000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const styles = {
    loading: "border-surface-border bg-surface-raised text-slate-300",
    healthy: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    warning: "border-amber-500/30 bg-amber-500/10 text-amber-200",
    error: "border-rose-500/30 bg-rose-500/10 text-rose-200",
  };

  const icons = {
    loading: <Loader2 className="h-4 w-4 animate-spin" />,
    healthy: <CheckCircle2 className="h-4 w-4" />,
    warning: <AlertTriangle className="h-4 w-4" />,
    error: <AlertTriangle className="h-4 w-4" />,
  };

  return (
    <div className="mx-auto max-w-7xl px-4 pt-4 sm:px-6 lg:px-8">
      <div
        className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm ${styles[status]}`}
      >
        {icons[status]}
        <span>{message}</span>
      </div>
    </div>
  );
}
