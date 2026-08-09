import { NavLink } from "react-router-dom";
import { BarChart3, Home, Layers3, Sparkles } from "lucide-react";

const links = [
  { to: "/", label: "Home", icon: Home },
  { to: "/recommendations", label: "Compare Models", icon: Layers3 },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-surface-border/80 bg-surface/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="group flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-violet-500 shadow-lg shadow-accent/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide text-white">
              Hybrid Rec Engine
            </p>
            <p className="text-xs text-slate-400">E-Commerce AI Dashboard</p>
          </div>
        </NavLink>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-accent/15 text-accent-glow"
                    : "text-slate-300 hover:bg-surface-raised hover:text-white",
                ].join(" ")
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>

      <nav className="flex gap-1 overflow-x-auto border-t border-surface-border/60 px-4 py-2 md:hidden">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [
                "flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium",
                isActive
                  ? "bg-accent/15 text-accent-glow"
                  : "text-slate-400 hover:text-white",
              ].join(" ")
            }
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
