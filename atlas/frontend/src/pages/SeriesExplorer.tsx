import { useState, useMemo } from "react";
import { useSeriesList, useSeriesHistory } from "@/api/hooks";
import { SeriesTable } from "@/components/tables/SeriesTable";
import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { useAtlasStore } from "@/store";
import { THEMES, THEME_LABELS, type Theme } from "@/types";
import { formatValue, formatDate } from "@/lib/utils";

export function SeriesExplorer() {
  const selectedSeriesId = useAtlasStore((s) => s.selectedSeriesId);
  const selectSeries = useAtlasStore((s) => s.selectSeries);
  const [themeFilter, setThemeFilter] = useState<string | undefined>();
  const [search, setSearch] = useState("");

  const { data: seriesData, isLoading: seriesLoading } = useSeriesList(
    themeFilter ? { theme: themeFilter } : undefined
  );

  const { data: historyData, isLoading: historyLoading } =
    useSeriesHistory(selectedSeriesId);

  // Filter by search text
  const filteredSeries = useMemo(() => {
    if (!seriesData) return [];
    if (!search) return seriesData.series;
    const q = search.toLowerCase();
    return seriesData.series.filter(
      (s) =>
        s.series_id.toLowerCase().includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q)
    );
  }, [seriesData, search]);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-atlas-text">Series Explorer</h2>
        <p className="text-sm text-atlas-muted">
          Browse and drill into individual macro time series
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search series..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-md border border-atlas-border bg-atlas-bg px-3 py-1.5 text-sm text-atlas-text placeholder:text-atlas-muted focus:border-atlas-accent focus:outline-none w-64"
        />
        <select
          value={themeFilter ?? ""}
          onChange={(e) => setThemeFilter(e.target.value || undefined)}
          className="rounded-md border border-atlas-border bg-atlas-bg px-3 py-1.5 text-sm text-atlas-text focus:border-atlas-accent focus:outline-none"
        >
          <option value="">All Themes</option>
          {THEMES.map((t) => (
            <option key={t} value={t}>
              {THEME_LABELS[t]}
            </option>
          ))}
        </select>
        <span className="text-xs text-atlas-muted">
          {filteredSeries.length} series
        </span>
      </div>

      {/* Split: table left, chart right */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="max-h-[600px] overflow-auto">
          {seriesLoading ? (
            <div className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4">
              <div className="space-y-2">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="h-8 rounded bg-atlas-border" />
                ))}
              </div>
            </div>
          ) : (
            <SeriesTable
              series={filteredSeries}
              onSelect={selectSeries}
              selectedId={selectedSeriesId}
            />
          )}
        </div>

        <div className="space-y-4">
          {selectedSeriesId ? (
            historyLoading ? (
              <div className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4" style={{ height: 360 }}>
                <div className="h-full rounded bg-atlas-border" />
              </div>
            ) : historyData ? (
              <>
                <TimeSeriesChart
                  data={historyData.data}
                  title={`${historyData.meta.name} (${historyData.series_id})`}
                  unit={historyData.meta.unit}
                />
                {/* Stats card */}
                <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
                  <h3 className="mb-2 text-sm font-semibold text-atlas-text">
                    Statistics
                  </h3>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    {[
                      { label: "Latest", value: historyData.stats.latest },
                      { label: "Mean", value: historyData.stats.mean },
                      { label: "Std Dev", value: historyData.stats.std },
                      { label: "Min", value: historyData.stats.min },
                      { label: "Max", value: historyData.stats.max },
                      {
                        label: "Data Points",
                        value: historyData.data.length,
                      },
                    ].map(({ label, value }) => (
                      <div key={label}>
                        <p className="text-xs text-atlas-muted">{label}</p>
                        <p className="font-mono font-medium text-atlas-text">
                          {typeof value === "number" ? formatValue(value, 4) : "—"}
                        </p>
                      </div>
                    ))}
                  </div>
                  <p className="mt-2 text-xs text-atlas-muted">
                    Last updated: {formatDate(historyData.meta.last_updated)}
                  </p>
                </div>
              </>
            ) : null
          ) : (
            <div className="flex h-[360px] items-center justify-center rounded-lg border border-dashed border-atlas-border text-sm text-atlas-muted">
              Select a series from the table to view its chart
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
