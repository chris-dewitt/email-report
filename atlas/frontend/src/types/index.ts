// ── Types mirroring backend Pydantic models ──

// Series
export interface SeriesMeta {
  series_id: string;
  name: string;
  source: string;
  frequency: string;
  theme: string;
  unit: string;
  description: string;
  last_updated: string | null;
  latest_value: number | null;
}

export interface SeriesPoint {
  date: string;
  value: number;
}

export interface SeriesStats {
  mean: number | null;
  std: number | null;
  min: number | null;
  max: number | null;
  latest: number | null;
  latest_z: number | null;
  change_1w: number | null;
  change_1m: number | null;
  pct_rank: number | null;
}

export interface SeriesHistoryResponse {
  series_id: string;
  meta: SeriesMeta;
  data: SeriesPoint[];
  stats: SeriesStats;
}

export interface SeriesListResponse {
  series: SeriesMeta[];
  count: number;
}

// Features
export interface FeatureMeta {
  feature_id: string;
  base_series: string;
  transform: string;
  latest_value: number | null;
  latest_z: number | null;
  change_1w: number | null;
}

export interface FeatureGroup {
  theme: string;
  features: FeatureMeta[];
  pca_factor_value: number | null;
}

export interface FeatureGroupResponse {
  groups: FeatureGroup[];
}

// Regime
export interface RegimeDriver {
  description: string;
  value: number | null;
  z_score: number | null;
}

export interface RegimeSnapshotResponse {
  regime: string;
  confidence: number;
  as_of: string;
  drivers: string[];
  all_scores: Record<string, number>;
}

// Health
export interface DataQualityReport {
  stale_series: string[];
  missing_series: string[];
  total_series: number;
  available_series: number;
}

export interface HealthResponse {
  status: "ok" | "degraded" | "error";
  last_pull: string | null;
  series_count: number;
  feature_count: number;
  data_quality: DataQualityReport;
}

// Copilot
export interface BriefingRequest {
  question?: string;
  lookback_days?: number;
}

export interface Citation {
  series_id: string;
  context: string;
}

export interface BriefingResponse {
  summary: string;
  citations: Citation[];
  model_used: string;
  prompt_tokens: number;
  response_tokens: number;
  generated_at: string | null;
}

// UX Modes
export type UXMode = "executive" | "analyst" | "copilot" | "research";

export const THEMES = [
  "inflation",
  "labor",
  "rates",
  "fincond",
  "growth",
  "fx_market",
] as const;

export type Theme = (typeof THEMES)[number];

export const THEME_LABELS: Record<Theme, string> = {
  inflation: "Inflation",
  labor: "Labor Market",
  rates: "Rates & Treasury",
  fincond: "Financial Conditions",
  growth: "Growth & Activity",
  fx_market: "FX & Market",
};

export const REGIME_COLORS: Record<string, string> = {
  expansion: "#10b981",
  overheating: "#f59e0b",
  slowdown: "#f97316",
  contraction: "#ef4444",
  financial_stress: "#8b5cf6",
};
