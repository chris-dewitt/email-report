import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a number to a compact display string. */
export function formatValue(value: number | null | undefined, decimals = 2): string {
  if (value == null) return "—";
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toFixed(decimals);
}

/** Format a z-score with color hint. */
export function zScoreColor(z: number | null | undefined): string {
  if (z == null) return "text-atlas-muted";
  if (z > 1.5) return "text-red-400";
  if (z > 0.5) return "text-yellow-400";
  if (z < -1.5) return "text-blue-400";
  if (z < -0.5) return "text-cyan-400";
  return "text-atlas-text";
}

/** Format a date string for display. */
export function formatDate(d: string | null | undefined): string {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
