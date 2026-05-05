import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  TrendingDown,
  BarChart3,
  Bot,
  ClipboardCheck,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { useFedLensStore } from "@/store";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/drift", icon: TrendingDown, label: "Drift & Sentiment" },
  { to: "/event-study", icon: BarChart3, label: "Event Study" },
  { to: "/copilot", icon: Bot, label: "Copilot" },
  { to: "/reviews", icon: ClipboardCheck, label: "Reviews" },
  { to: "/settings", icon: Settings, label: "Settings" },
] as const;

export function Sidebar() {
  const open = useFedLensStore((s) => s.sidebarOpen);
  const toggle = useFedLensStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 flex flex-col border-r border-fed-border bg-fed-surface transition-all duration-200",
        open ? "w-56" : "w-16"
      )}
    >
      <div className="flex h-12 items-center justify-between border-b border-fed-border px-3">
        {open && (
          <span className="text-lg font-bold text-fed-accent tracking-tight">
            FEDLENS
          </span>
        )}
        <button
          onClick={toggle}
          className="rounded p-1 text-fed-muted hover:text-fed-text hover:bg-fed-border transition"
        >
          {open ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
        </button>
      </div>

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
                  ? "bg-fed-accent/10 text-fed-accent"
                  : "text-fed-muted hover:text-fed-text hover:bg-fed-border/50"
              )
            }
          >
            <Icon size={18} />
            {open && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-fed-border p-3">
        {open && (
          <p className="text-xs text-fed-muted">
            v0.1.0 — Local Mode
          </p>
        )}
      </div>
    </aside>
  );
}
