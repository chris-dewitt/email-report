import Plot from "react-plotly.js";
import type { DriftPoint } from "@/types";

const DARK_LAYOUT: Partial<Plotly.Layout> = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { color: "#e5e7eb", family: "Inter, sans-serif", size: 12 },
  margin: { t: 30, r: 20, b: 40, l: 50 },
  xaxis: { gridcolor: "#1f2937", linecolor: "#1f2937" },
  yaxis: { gridcolor: "#1f2937", linecolor: "#1f2937" },
  legend: { orientation: "h", y: -0.15 },
};

interface Props {
  data: DriftPoint[];
  title?: string;
}

export function DriftChart({ data, title = "Semantic Drift" }: Props) {
  if (!data.length) {
    return <div className="text-fed-muted text-sm py-8 text-center">No drift data available</div>;
  }

  const dates = data.map((d) => d.date);
  const similarity = data.map((d) => d.similarity);
  const rolling = data.filter((d) => d.rolling_avg != null);

  const traces: Plotly.Data[] = [
    {
      x: dates,
      y: similarity,
      type: "scatter",
      mode: "markers+lines",
      name: "Cosine Similarity",
      line: { color: "#6366f1", width: 1.5 },
      marker: { size: 5, color: "#6366f1" },
      hovertemplate: "%{x}<br>Similarity: %{y:.4f}<extra></extra>",
    },
  ];

  if (rolling.length > 0) {
    traces.push({
      x: rolling.map((d) => d.date),
      y: rolling.map((d) => d.rolling_avg!),
      type: "scatter",
      mode: "lines",
      name: "Rolling Avg",
      line: { color: "#f59e0b", width: 2, dash: "dot" },
    });
  }

  return (
    <Plot
      data={traces}
      layout={{
        ...DARK_LAYOUT,
        title: { text: title, font: { size: 14, color: "#e5e7eb" } },
        yaxis: { ...DARK_LAYOUT.yaxis, title: "Cosine Similarity", range: [0, 1] },
      }}
      config={{ displayModeBar: false, responsive: true }}
      className="w-full"
      style={{ width: "100%", height: 350 }}
    />
  );
}
