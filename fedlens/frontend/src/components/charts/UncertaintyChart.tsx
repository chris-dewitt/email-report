import Plot from "react-plotly.js";
import type { UncertaintyPoint } from "@/types";

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
  data: UncertaintyPoint[];
  title?: string;
}

export function UncertaintyChart({ data, title = "Uncertainty Index" }: Props) {
  if (!data.length) {
    return <div className="text-fed-muted text-sm py-8 text-center">No uncertainty data available</div>;
  }

  const dates = data.map((d) => d.date);

  return (
    <Plot
      data={[
        {
          x: dates,
          y: data.map((d) => d.uncertainty_score),
          type: "scatter",
          mode: "lines",
          name: "Uncertainty",
          line: { color: "#f59e0b", width: 2 },
          fill: "tozeroy",
          fillcolor: "rgba(245, 158, 11, 0.1)",
        },
        {
          x: dates,
          y: data.map((d) => d.hedging_score),
          type: "scatter",
          mode: "lines",
          name: "Hedging",
          line: { color: "#8b5cf6", width: 1.5 },
        },
      ]}
      layout={{
        ...DARK_LAYOUT,
        title: { text: title, font: { size: 14, color: "#e5e7eb" } },
        yaxis: { ...DARK_LAYOUT.yaxis, title: "Score" },
      }}
      config={{ displayModeBar: false, responsive: true }}
      className="w-full"
      style={{ width: "100%", height: 350 }}
    />
  );
}
