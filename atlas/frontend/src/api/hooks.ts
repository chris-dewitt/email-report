/**
 * TanStack Query hooks for all Atlas API endpoints.
 */

import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "./client";
import type { BriefingRequest } from "@/types";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30_000,
  });
}

export function useSeriesList(params?: { theme?: string; source?: string }) {
  return useQuery({
    queryKey: ["series", params],
    queryFn: () => api.listSeries(params),
  });
}

export function useSeriesHistory(
  seriesId: string | null,
  params?: { start?: string; end?: string }
) {
  return useQuery({
    queryKey: ["series-history", seriesId, params],
    queryFn: () => api.seriesHistory(seriesId!, params),
    enabled: !!seriesId,
  });
}

export function useFeatureGroups() {
  return useQuery({
    queryKey: ["feature-groups"],
    queryFn: api.featureGroups,
  });
}

export function useRegimeSnapshot() {
  return useQuery({
    queryKey: ["regime-snapshot"],
    queryFn: api.regimeSnapshot,
  });
}

export function useBriefing() {
  return useMutation({
    mutationFn: (req: BriefingRequest) => api.briefing(req),
  });
}
