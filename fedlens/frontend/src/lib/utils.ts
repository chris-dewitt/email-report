import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatValue(value: number | null | undefined, decimals = 2): string {
  if (value == null) return "\u2014";
  return value.toFixed(decimals);
}

export function formatDate(d: string | null | undefined): string {
  if (!d) return "\u2014";
  return new Date(d).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function sentimentColor(score: number | null | undefined): string {
  if (score == null) return "text-fed-muted";
  if (score > 0.1) return "text-fed-hawkish";
  if (score < -0.1) return "text-fed-dovish";
  return "text-fed-muted";
}

export function sentimentLabel(score: number | null | undefined): string {
  if (score == null) return "Unknown";
  if (score > 0.1) return "Hawkish";
  if (score < -0.1) return "Dovish";
  return "Neutral";
}
