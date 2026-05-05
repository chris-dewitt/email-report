/**
 * Zustand store — global FedLens UX state.
 */

import { create } from "zustand";

interface FedLensStore {
  selectedDocType: string;
  setDocType: (dt: string) => void;

  sidebarOpen: boolean;
  toggleSidebar: () => void;

  selectedDocId: string | null;
  selectDoc: (id: string | null) => void;
}

export const useFedLensStore = create<FedLensStore>((set) => ({
  selectedDocType: "statement",
  setDocType: (dt) => set({ selectedDocType: dt }),

  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  selectedDocId: null,
  selectDoc: (id) => set({ selectedDocId: id }),
}));
