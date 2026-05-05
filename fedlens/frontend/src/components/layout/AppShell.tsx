import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { useFedLensStore } from "@/store";

interface Props {
  children: ReactNode;
}

export function AppShell({ children }: Props) {
  const sidebarOpen = useFedLensStore((s) => s.sidebarOpen);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div
        className={`flex flex-1 flex-col overflow-hidden transition-all duration-200 ${
          sidebarOpen ? "ml-56" : "ml-16"
        }`}
      >
        <header className="flex h-12 items-center justify-between border-b border-fed-border bg-fed-surface px-4">
          <h1 className="text-sm font-semibold tracking-wide text-fed-muted uppercase">
            FedLens — Fed Communication Intelligence
          </h1>
          <span className="text-xs text-fed-muted">v0.1.0</span>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
