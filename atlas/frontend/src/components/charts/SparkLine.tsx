import type { SeriesPoint } from "@/types";

interface SparkLineProps {
  data: SeriesPoint[];
  color?: string;
  height?: number;
}

/**
 * Lightweight SVG sparkline — no Plotly overhead.
 */
export function SparkLine({ data, color = "#3b82f6", height = 32 }: SparkLineProps) {
  if (data.length < 2) return null;

  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const width = 120;
  const padding = 2;

  const points = values
    .map((v, i) => {
      const x = padding + (i / (values.length - 1)) * (width - 2 * padding);
      const y = padding + (1 - (v - min) / range) * (height - 2 * padding);
      return `${x},${y}`;
    })
    .join(" ");

  // Determine trend color
  const trendColor =
    values[values.length - 1] >= values[0] ? "#10b981" : "#ef4444";

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full"
      style={{ height }}
      preserveAspectRatio="none"
    >
      <polyline
        points={points}
        fill="none"
        stroke={trendColor}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
