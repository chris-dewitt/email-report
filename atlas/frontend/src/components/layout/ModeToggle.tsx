import { useAtlasStore } from "@/store";
import type { UXMode } from "@/types";
import { cn } from "@/lib/utils";

const MODES: { value: UXMode; label: string }[] = [
  { value: "executive", label: "Executive" },
  { value: "analyst", label: "Analyst" },
  { value: "copilot", label: "Copilot" },
];

export function ModeToggle() {
  const mode = useAtlasStore((s) => s.mode);
  const setMode = useAtlasStore((s) => s.setMode);

  return (
    <div className="flex items-center gap-1 rounded-md border border-atlas-border bg-atlas-bg p-0.5">
      {MODES.map((m) => (
        <button
          key={m.value}
          onClick={() => setMode(m.value)}
          className={cn(
            "rounded px-3 py-1 text-xs font-medium transition",
            mode === m.value
              ? "bg-atlas-accent text-white"
              : "text-atlas-muted hover:text-atlas-text"
          )}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
