import Plot from "react-plotly.js";
import type { EventStudyResult } from "@/types";

const DARK_LAYOUT: Partial<Plotly.Layout> = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { color: "#e5e7eb", family: "Inter, sans-serif", size: 12 },
  margin: { t: 30, r: 20, b: 60, l: 50 },
  xaxis: { gridcolor: "#1f2937", linecolor: "#1f2937" },
  yaxis: { gridcolor: "#1f2937", linecolor: "#1f2937", zeroline: true, zerolinecolor: "#374151" },
};

interface Props {
  data: EventStudyResult[];
  title?: string;
}

export function CARBarChart({ data, title = "Cumulative Abnormal Returns" }: Props) {
  if (!data.length) {
    return <div className="text-fed-muted text-sm py-8 text-center">No event study data available</div>;
  }

  const sorted = [...data].sort((a, b) => new Date(a.event_date).getTime() - new Date(b.event_date).getTime());
  const labels = sorted.map((d) => d.event_date);
  const cars = sorted.map((d) => d.car * 100);
  const colors = cars.map((c) => (c >= 0 ? "#10b981" : "#ef4444"));
  const borders = sorted.map((d) => (d.significant ? "#f59e0b" : "transparent"));

  return (
    <Plot
      data={[
        {
          x: labels,
          y: cars,
          type: "bar",
          marker: {
            color: colors,
            line: { color: borders, width: 2 },
          },
          hovertemplate: "%{x}<br>CAR: %{y:.2f} bps<br><extra></extra>",
        },
      ]}
      layout={{
        ...DARK_LAYOUT,
        title: { text: title, font: { size: 14, color: "#e5e7eb" } },
        yaxis: { ...DARK_LAYOUT.yaxis, title: "CAR (bps)" },
        xaxis: { ...DARK_LAYOUT.xaxis, tickangle: -45 },
        showlegend: false,
      }}
      config={{ displayModeBar: false, responsive: true }}
      className="w-full"
      style={{ width: "100%", height: 400 }}
    />
  );
}
