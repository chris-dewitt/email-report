/**
 * TanStack Query hooks for all FedLens API endpoints.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { BriefingRequest } from "@/types";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30_000,
  });
}

export function useDocuments(docType?: string) {
  return useQuery({
    queryKey: ["documents", docType],
    queryFn: () => api.listDocuments(docType ? { doc_type: docType } : undefined),
  });
}

export function useDocument(docId: string | null) {
  return useQuery({
    queryKey: ["document", docId],
    queryFn: () => api.getDocument(docId!),
    enabled: !!docId,
  });
}

export function useSearch() {
  return useMutation({
    mutationFn: ({ query, doc_type }: { query: string; doc_type?: string }) =>
      api.search(query, { doc_type }),
  });
}

export function useSentiment(docType = "statement") {
  return useQuery({
    queryKey: ["sentiment", docType],
    queryFn: () => api.sentiment(docType),
  });
}

export function useDrift(docType = "statement") {
  return useQuery({
    queryKey: ["drift", docType],
    queryFn: () => api.drift(docType),
  });
}

export function useUncertainty(docType = "statement") {
  return useQuery({
    queryKey: ["uncertainty", docType],
    queryFn: () => api.uncertainty(docType),
  });
}

export function useEventStudies(params?: { doc_type?: string; series_id?: string }) {
  return useQuery({
    queryKey: ["event-studies", params],
    queryFn: () => api.eventStudies(params),
  });
}

export function useBriefing() {
  return useMutation({
    mutationFn: (req: BriefingRequest) => api.briefing(req),
  });
}

export function useReviews(status?: string) {
  return useQuery({
    queryKey: ["reviews", status],
    queryFn: () => api.listReviews(status),
  });
}

export function useApproveReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ reviewId, comment }: { reviewId: string; comment?: string }) =>
      api.approveReview(reviewId, comment),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reviews"] }),
  });
}

export function useRejectReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ reviewId, comment }: { reviewId: string; comment?: string }) =>
      api.rejectReview(reviewId, comment),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reviews"] }),
  });
}
