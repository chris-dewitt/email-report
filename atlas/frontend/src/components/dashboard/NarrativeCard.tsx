import { useState } from "react";
import { useBriefing } from "@/api/hooks";
import { Bot, RefreshCw } from "lucide-react";

export function NarrativeCard() {
  const { mutate, data, isPending, error } = useBriefing();
  const [hasRequested, setHasRequested] = useState(false);

  const handleGenerate = () => {
    setHasRequested(true);
    mutate({ question: "What are the key macro developments this week?" });
  };

  return (
    <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot size={16} className="text-atlas-purple" />
          <h3 className="text-sm font-semibold text-atlas-text">AI Macro Briefing</h3>
        </div>
        <button
          onClick={handleGenerate}
          disabled={isPending}
          className="flex items-center gap-1.5 rounded-md border border-atlas-border px-2.5 py-1 text-xs font-medium text-atlas-muted hover:text-atlas-text hover:border-atlas-accent/40 transition disabled:opacity-50"
        >
          <RefreshCw size={12} className={isPending ? "animate-spin" : ""} />
          {isPending ? "Generating..." : "Generate"}
        </button>
      </div>

      <div className="mt-3 min-h-[80px]">
        {!hasRequested && (
          <p className="text-sm text-atlas-muted italic">
            Click Generate to get an AI-powered macro summary from your local LLM.
          </p>
        )}

        {isPending && (
          <div className="flex items-center gap-2 text-sm text-atlas-muted">
            <div className="h-2 w-2 rounded-full bg-atlas-purple animate-pulse" />
            Thinking...
          </div>
        )}

        {error && (
          <p className="text-sm text-red-400">
            Copilot unavailable — is Ollama running? ({String(error)})
          </p>
        )}

        {data && !isPending && (
          <div>
            <p className="text-sm text-atlas-text leading-relaxed whitespace-pre-wrap">
              {data.summary}
            </p>
            {data.citations.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {data.citations.map((c, i) => (
                  <span
                    key={i}
                    className="rounded bg-atlas-purple/10 px-2 py-0.5 text-xs font-mono text-atlas-purple"
                  >
                    {c.series_id}
                  </span>
                ))}
              </div>
            )}
            {data.model_used && (
              <p className="mt-2 text-[10px] text-atlas-muted">
                Model: {data.model_used}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
