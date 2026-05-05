/**
 * Zustand store — global UX state.
 */

import { create } from "zustand";
import type { UXMode } from "@/types";

interface AtlasStore {
  mode: UXMode;
  setMode: (mode: UXMode) => void;

  selectedSeriesId: string | null;
  selectSeries: (id: string | null) => void;

  sidebarOpen: boolean;
  toggleSidebar: () => void;

  selectedTheme: string | null;
  setSelectedTheme: (theme: string | null) => void;
}

export const useAtlasStore = create<AtlasStore>((set) => ({
  mode: "executive",
  setMode: (mode) => set({ mode }),

  selectedSeriesId: null,
  selectSeries: (id) => set({ selectedSeriesId: id }),

  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  selectedTheme: null,
  setSelectedTheme: (theme) => set({ selectedTheme: theme }),
}));
