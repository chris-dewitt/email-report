import { useState } from "react";
import { useFeatureGroups } from "@/api/hooks";
import { FeatureTable } from "@/components/tables/FeatureTable";
import { THEME_LABELS, type Theme } from "@/types";
import { ChevronDown, ChevronRight } from "lucide-react";

export function FeatureExplorer() {
  const { data, isLoading, error } = useFeatureGroups();
  const [expandedThemes, setExpandedThemes] = useState<Set<string>>(new Set());

  const toggleTheme = (theme: string) => {
    setExpandedThemes((prev) => {
      const next = new Set(prev);
      if (next.has(theme)) {
        next.delete(theme);
      } else {
        next.add(theme);
      }
      return next;
    });
  };

  const expandAll = () => {
    if (data) {
      setExpandedThemes(new Set(data.groups.map((g) => g.theme)));
    }
  };

  const collapseAll = () => setExpandedThemes(new Set());

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-atlas-text">Feature Explorer</h2>
          <p className="text-sm text-atlas-muted">
            Browse themed feature groups with z-scores and transforms
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            className="rounded border border-atlas-border px-2.5 py-1 text-xs text-atlas-muted hover:text-atlas-text transition"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="rounded border border-atlas-border px-2.5 py-1 text-xs text-atlas-muted hover:text-atlas-text transition"
          >
            Collapse All
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4"
            >
              <div className="h-6 w-40 rounded bg-atlas-border" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-900/30 bg-red-950/20 p-4 text-sm text-red-400">
          Failed to load features: {String(error)}
        </div>
      )}

      {data && (
        <div className="space-y-2">
          {data.groups.map((group) => {
            const expanded = expandedThemes.has(group.theme);
            const label =
              THEME_LABELS[group.theme as Theme] ?? group.theme;

            return (
              <div
                key={group.theme}
                className="rounded-lg border border-atlas-border bg-atlas-surface overflow-hidden"
              >
                <button
                  onClick={() => toggleTheme(group.theme)}
                  className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-atlas-accent/5 transition"
                >
                  <div className="flex items-center gap-2">
                    {expanded ? (
                      <ChevronDown size={16} className="text-atlas-muted" />
                    ) : (
                      <ChevronRight size={16} className="text-atlas-muted" />
                    )}
                    <span className="font-semibold text-atlas-text">
                      {label}
                    </span>
                    <span className="rounded-full bg-atlas-border px-2 py-0.5 text-[10px] text-atlas-muted">
                      {group.features.length} features
                    </span>
                  </div>
                  {group.pca_factor_value != null && (
                    <span className="text-xs font-mono text-atlas-muted">
                      PCA: {group.pca_factor_value.toFixed(3)}
                    </span>
                  )}
                </button>

                {expanded && (
                  <div className="border-t border-atlas-border">
                    <FeatureTable features={group.features} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
