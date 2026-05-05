/**
 * FedLens API client — thin wrapper over fetch.
 * Vite dev server proxies /api to localhost:8001.
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
  HealthResponse,
  DocumentListResponse,
  DocumentDetail,
  SearchResponse,
  SentimentResponse,
  DriftResponse,
  UncertaintyResponse,
  EventStudyListResponse,
  BriefingRequest,
  BriefingResponse,
  ReviewListResponse,
} from "@/types";

export const api = {
  health: () => request<HealthResponse>("/health"),

  listDocuments: (params?: { doc_type?: string }) => {
    const qs = new URLSearchParams();
    if (params?.doc_type) qs.set("doc_type", params.doc_type);
    const q = qs.toString();
    return request<DocumentListResponse>(`/documents${q ? `?${q}` : ""}`);
  },

  getDocument: (docId: string) =>
    request<DocumentDetail>(`/documents/${encodeURIComponent(docId)}`),

  search: (query: string, params?: { k?: number; doc_type?: string }) =>
    request<SearchResponse>("/search", {
      method: "POST",
      body: JSON.stringify({ query, k: params?.k ?? 10, doc_type: params?.doc_type }),
    }),

  sentiment: (docType = "statement") =>
    request<SentimentResponse>(`/sentiment?doc_type=${docType}`),

  drift: (docType = "statement") =>
    request<DriftResponse>(`/drift?doc_type=${docType}`),

  uncertainty: (docType = "statement") =>
    request<UncertaintyResponse>(`/uncertainty?doc_type=${docType}`),

  eventStudies: (params?: { doc_type?: string; series_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.doc_type) qs.set("doc_type", params.doc_type);
    if (params?.series_id) qs.set("series_id", params.series_id);
    const q = qs.toString();
    return request<EventStudyListResponse>(`/event-study${q ? `?${q}` : ""}`);
  },

  eventStudyDetail: (docId: string) =>
    request<{ doc_id: string; results: unknown[] }>(`/event-study/${encodeURIComponent(docId)}`),

  briefing: (req: BriefingRequest) =>
    request<BriefingResponse>("/briefing", {
      method: "POST",
      body: JSON.stringify(req),
    }),

  listReviews: (status?: string) => {
    const qs = status ? `?status=${status}` : "";
    return request<ReviewListResponse>(`/reviews${qs}`);
  },

  approveReview: (reviewId: string, comment = "") =>
    request<{ status: string; review_id: string }>(`/reviews/${reviewId}/approve`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),

  rejectReview: (reviewId: string, comment = "") =>
    request<{ status: string; review_id: string }>(`/reviews/${reviewId}/reject`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),
};
