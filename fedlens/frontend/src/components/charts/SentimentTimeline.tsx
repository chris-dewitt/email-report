import Plot from "react-plotly.js";
import type { SentimentPoint } from "@/types";

const DARK_LAYOUT: Partial<Plotly.Layout> = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { color: "#e5e7eb", family: "Inter, sans-serif", size: 12 },
  margin: { t: 30, r: 20, b: 40, l: 50 },
  xaxis: { gridcolor: "#1f2937", linecolor: "#1f2937" },
  yaxis: { gridcolor: "#1f2937", linecolor: "#1f2937", zeroline: true, zerolinecolor: "#374151" },
  legend: { orientation: "h", y: -0.15 },
};

interface Props {
  data: SentimentPoint[];
  title?: string;
}

export function SentimentTimeline({ data, title = "Sentiment Over Time" }: Props) {
  if (!data.length) {
    return <div className="text-fed-muted text-sm py-8 text-center">No sentiment data available</div>;
  }

  const dates = data.map((d) => d.date);
  const scores = data.map((d) => d.net_score);
  const colors = scores.map((s) => (s > 0 ? "#ef4444" : "#3b82f6"));

  return (
    <Plot
      data={[
        {
          x: dates,
          y: scores,
          type: "bar",
          marker: { color: colors },
          name: "Net Sentiment",
          hovertemplate: "%{x}<br>Score: %{y:.3f}<extra></extra>",
        },
      ]}
      layout={{
        ...DARK_LAYOUT,
        title: { text: title, font: { size: 14, color: "#e5e7eb" } },
        yaxis: { ...DARK_LAYOUT.yaxis, title: "Hawkish (+) / Dovish (-)" },
      }}
      config={{ displayModeBar: false, responsive: true }}
      className="w-full"
      style={{ width: "100%", height: 350 }}
    />
  );
}
