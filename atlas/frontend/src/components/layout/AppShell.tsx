import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { ModeToggle } from "./ModeToggle";
import { useAtlasStore } from "@/store";

interface Props {
  children: ReactNode;
}

export function AppShell({ children }: Props) {
  const sidebarOpen = useAtlasStore((s) => s.sidebarOpen);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div
        className={`flex flex-1 flex-col overflow-hidden transition-all duration-200 ${
          sidebarOpen ? "ml-56" : "ml-16"
        }`}
      >
        {/* Top bar */}
        <header className="flex h-12 items-center justify-between border-b border-atlas-border bg-atlas-surface px-4">
          <h1 className="text-sm font-semibold tracking-wide text-atlas-muted uppercase">
            Atlas — Macro Intelligence
          </h1>
          <ModeToggle />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
