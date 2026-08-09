export default function LoadingSkeleton({ count = 6 }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="animate-pulse overflow-hidden rounded-2xl border border-surface-border bg-surface-card"
        >
          <div className="aspect-[4/3] bg-surface-border/60" />
          <div className="space-y-3 p-4">
            <div className="h-4 w-3/4 rounded bg-surface-border/80" />
            <div className="h-3 w-1/2 rounded bg-surface-border/60" />
            <div className="h-8 w-full rounded-lg bg-surface-border/50" />
          </div>
        </div>
      ))}
    </div>
  );
}
