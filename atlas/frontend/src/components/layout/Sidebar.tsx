import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  LineChart,
  Layers,
  Bot,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { useAtlasStore } from "@/store";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/series", icon: LineChart, label: "Series Explorer" },
  { to: "/features", icon: Layers, label: "Features" },
  { to: "/copilot", icon: Bot, label: "Copilot" },
  { to: "/settings", icon: Settings, label: "Settings" },
] as const;

export function Sidebar() {
  const open = useAtlasStore((s) => s.sidebarOpen);
  const toggle = useAtlasStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 flex flex-col border-r border-atlas-border bg-atlas-surface transition-all duration-200",
        open ? "w-56" : "w-16"
      )}
    >
      {/* Logo area */}
      <div className="flex h-12 items-center justify-between border-b border-atlas-border px-3">
        {open && (
          <span className="text-lg font-bold text-atlas-accent tracking-tight">
            ATLAS
          </span>
        )}
        <button
          onClick={toggle}
          className="rounded p-1 text-atlas-muted hover:text-atlas-text hover:bg-atlas-border transition"
        >
          {open ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2 py-3">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition",
                isActive
                  ? "bg-atlas-accent/10 text-atlas-accent"
                  : "text-atlas-muted hover:text-atlas-text hover:bg-atlas-border/50"
              )
            }
          >
            <Icon size={18} />
            {open && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Status footer */}
      <div className="border-t border-atlas-border p-3">
        {open && (
          <p className="text-xs text-atlas-muted">
            v0.1.0 — Local Mode
          </p>
        )}
      </div>
    </aside>
  );
}
