/**
 * Atlas API client — thin wrapper over fetch.
 * Vite dev server proxies /api to localhost:8000.
 */

const BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

// ── Endpoints ──

import type {
  SeriesListResponse,
  SeriesHistoryResponse,
  FeatureGroupResponse,
  RegimeSnapshotResponse,
  HealthResponse,
  BriefingRequest,
  BriefingResponse,
} from "@/types";

export const api = {
  health: () => request<HealthResponse>("/health"),

  listSeries: (params?: { theme?: string; source?: string }) => {
    const qs = new URLSearchParams();
    if (params?.theme) qs.set("theme", params.theme);
    if (params?.source) qs.set("source", params.source);
    const q = qs.toString();
    return request<SeriesListResponse>(`/series${q ? `?${q}` : ""}`);
  },

  seriesHistory: (
    seriesId: string,
    params?: { start?: string; end?: string }
  ) => {
    const qs = new URLSearchParams();
    if (params?.start) qs.set("start", params.start);
    if (params?.end) qs.set("end", params.end);
    const q = qs.toString();
    return request<SeriesHistoryResponse>(
      `/series/${encodeURIComponent(seriesId)}/history${q ? `?${q}` : ""}`
    );
  },

  featureGroups: () => request<FeatureGroupResponse>("/feature-groups"),

  regimeSnapshot: () => request<RegimeSnapshotResponse>("/regime-snapshot"),

  briefing: (req: BriefingRequest) =>
    request<BriefingResponse>("/copilot/briefing", {
      method: "POST",
      body: JSON.stringify(req),
    }),
};
