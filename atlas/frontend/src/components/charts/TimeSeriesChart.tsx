import Plot from "react-plotly.js";
import type { SeriesPoint } from "@/types";

interface TimeSeriesChartProps {
  data: SeriesPoint[];
  title: string;
  unit?: string;
  height?: number;
}

export function TimeSeriesChart({
  data,
  title,
  unit = "",
  height = 360,
}: TimeSeriesChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-atlas-border bg-atlas-surface text-atlas-muted text-sm"
        style={{ height }}
      >
        No data available
      </div>
    );
  }

  const dates = data.map((d) => d.date);
  const values = data.map((d) => d.value);

  return (
    <div className="rounded-lg border border-atlas-border bg-atlas-surface p-2">
      <Plot
        data={[
          {
            x: dates,
            y: values,
            type: "scatter",
            mode: "lines",
            line: { color: "#3b82f6", width: 1.5 },
            fill: "tozeroy",
            fillcolor: "rgba(59, 130, 246, 0.05)",
            hovertemplate: `%{x|%b %d, %Y}<br><b>%{y:.4f}</b> ${unit}<extra></extra>`,
          },
        ]}
        layout={{
          title: { text: title, font: { color: "#e5e7eb", size: 14 } },
          height,
          margin: { l: 60, r: 20, t: 40, b: 40 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          xaxis: {
            gridcolor: "#1f2937",
            tickfont: { color: "#6b7280", size: 10 },
            linecolor: "#1f2937",
          },
          yaxis: {
            title: { text: unit, font: { color: "#6b7280", size: 11 } },
            gridcolor: "#1f2937",
            tickfont: { color: "#6b7280", size: 10 },
            linecolor: "#1f2937",
          },
          hovermode: "x unified",
          showlegend: false,
        }}
        config={{
          displayModeBar: false,
          responsive: true,
        }}
        className="w-full"
      />
    </div>
  );
}
