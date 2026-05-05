// ── Types mirroring FedLens backend API responses ──

// Documents
export interface DocumentMeta {
  doc_id: string;
  doc_type: string;
  date: string;
  title: string;
  chunk_count: number;
  sentiment_score?: number | null;
  sentiment_label?: string | null;
}

export interface DocumentChunk {
  chunk_id: string;
  doc_id: string;
  section: string;
  text: string;
  token_count: number;
}

export interface DocumentDetail {
  doc_id: string;
  doc_type: string;
  date: string;
  title: string;
  chunks: DocumentChunk[];
}

export interface DocumentListResponse {
  documents: DocumentMeta[];
  total: number;
}

// Search
export interface SearchHit {
  chunk_id: string;
  doc_id: string;
  doc_type: string;
  date: string;
  section: string;
  text: string;
  score: number;
}

export interface SearchResponse {
  results: SearchHit[];
  total: number;
  query: string;
}

// Sentiment
export interface SentimentPoint {
  date: string;
  doc_id: string;
  net_score: number;
  hawkish_count: number;
  dovish_count: number;
  label: string;
}

export interface SentimentResponse {
  data: SentimentPoint[];
  total: number;
}

// Drift
export interface DriftPoint {
  date: string;
  doc_id: string;
  similarity: number;
  drift: number;
  rolling_avg?: number | null;
}

export interface DriftResponse {
  data: DriftPoint[];
  total: number;
}

// Uncertainty
export interface UncertaintyPoint {
  date: string;
  doc_id: string;
  uncertainty_score: number;
  hedging_score: number;
  certainty_score: number;
}

export interface UncertaintyResponse {
  data: UncertaintyPoint[];
  total: number;
}

// Event Study
export interface EventStudyResult {
  doc_id: string;
  event_date: string;
  series_id: string;
  car: number;
  t_stat: number;
  p_value: number;
  significant: boolean;
  ar_series?: number[];
  window_pre: number;
  window_post: number;
}

export interface EventStudyListResponse {
  results: EventStudyResult[];
  total: number;
}

// Briefing
export interface BriefingRequest {
  question?: string;
  doc_id?: string;
}

export interface BriefingCitation {
  doc_id: string;
  text_excerpt: string;
  score: number;
}

export interface BriefingResponse {
  briefing: string;
  citations: BriefingCitation[];
  confidence: number;
  approval_status: string;
  steps: number;
}

// Reviews (HITL)
export interface ReviewItem {
  review_id: string;
  agent_name: string;
  submitted_at: string;
  reviewed_at: string | null;
  status: string;
  reviewer_comment: string | null;
  confidence: number;
  output_preview: string;
}

export interface ReviewListResponse {
  reviews: ReviewItem[];
  total: number;
}

// Health
export interface HealthResponse {
  status: string;
  total_documents: number;
  documents: Record<string, number>;
  index_built: boolean;
  ollama_available: boolean;
  gold_layers: Record<string, number>;
}

// Doc types
export const DOC_TYPES = [
  "statement",
  "minutes",
  "speech",
  "pressconf",
] as const;

export type DocType = (typeof DOC_TYPES)[number];

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  statement: "Statements",
  minutes: "Minutes",
  speech: "Speeches",
  pressconf: "Press Conferences",
};

export const SENTIMENT_COLORS = {
  hawkish: "#ef4444",
  dovish: "#3b82f6",
  neutral: "#6b7280",
} as const;
