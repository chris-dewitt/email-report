import { useState } from "react";
import { useBriefing } from "@/api/hooks";
import { CitationBadge } from "@/components/shared/CitationBadge";
import { Bot, Send, Loader2 } from "lucide-react";

const SUGGESTED_QUESTIONS = [
  "How has inflation language changed in recent statements?",
  "What is the Fed's current stance on employment?",
  "Summarize the most recent FOMC statement",
  "How has forward guidance evolved this year?",
  "What market reactions followed the last rate decision?",
];

export function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [docId, setDocId] = useState("");
  const briefingMutation = useBriefing();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() && !docId.trim()) return;
    briefingMutation.mutate({
      question: question.trim() || undefined,
      doc_id: docId.trim() || undefined,
    });
  };

  const handleSuggestion = (q: string) => {
    setQuestion(q);
    briefingMutation.mutate({ question: q });
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-fed-text">Copilot</h2>
        <p className="text-sm text-fed-muted mt-1">
          Ask questions about Fed communications — powered by RAG + local LLM
        </p>
      </div>

      {/* Suggested questions */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => handleSuggestion(q)}
            disabled={briefingMutation.isPending}
            className="rounded-full border border-fed-border bg-fed-surface px-3 py-1.5 text-xs text-fed-muted hover:text-fed-text hover:border-fed-accent/50 transition disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <Bot size={16} className="absolute left-3 top-3 text-fed-muted" />
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about Fed communications..."
            rows={3}
            className="w-full rounded-md border border-fed-border bg-fed-bg pl-10 pr-4 py-2 text-sm text-fed-text placeholder-fed-muted focus:border-fed-accent focus:outline-none resize-none"
          />
        </div>
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            placeholder="Optional: specific doc_id"
            className="rounded-md border border-fed-border bg-fed-bg px-3 py-2 text-sm text-fed-text placeholder-fed-muted focus:border-fed-accent focus:outline-none flex-1"
          />
          <button
            type="submit"
            disabled={briefingMutation.isPending || (!question.trim() && !docId.trim())}
            className="flex items-center gap-2 rounded-md bg-fed-accent px-4 py-2 text-sm font-medium text-white hover:bg-fed-accent/80 disabled:opacity-50"
          >
            {briefingMutation.isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Generating...</>
            ) : (
              <><Send size={16} /> Generate Briefing</>
            )}
          </button>
        </div>
      </form>

      {/* Error */}
      {briefingMutation.isError && (
        <div className="rounded-lg border border-fed-red/30 bg-fed-red/5 p-4">
          <p className="text-sm text-fed-red">
            {briefingMutation.error.message}
          </p>
        </div>
      )}

      {/* Response */}
      {briefingMutation.data && (
        <div className="rounded-lg border border-fed-border bg-fed-surface p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-fed-accent uppercase tracking-wider">
              Briefing
            </h3>
            <div className="flex items-center gap-3 text-xs text-fed-muted">
              <span>Confidence: {(briefingMutation.data.confidence * 100).toFixed(0)}%</span>
              <span>Steps: {briefingMutation.data.steps}</span>
              <span className={
                briefingMutation.data.approval_status === "approved"
                  ? "text-fed-green"
                  : briefingMutation.data.approval_status === "pending"
                  ? "text-fed-yellow"
                  : "text-fed-red"
              }>
                {briefingMutation.data.approval_status}
              </span>
            </div>
          </div>

          <div className="prose prose-invert prose-sm max-w-none">
            <p className="text-fed-text whitespace-pre-wrap leading-relaxed">
              {briefingMutation.data.briefing}
            </p>
          </div>

          {briefingMutation.data.citations.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-fed-muted uppercase tracking-wider mb-2">
                Citations
              </h4>
              <div className="space-y-2">
                {briefingMutation.data.citations.map((c, i) => (
                  <div key={i} className="flex items-start gap-2 rounded border border-fed-border bg-fed-bg/50 p-2">
                    <CitationBadge docId={c.doc_id} score={c.score} />
                    <p className="text-xs text-fed-muted line-clamp-2">{c.text_excerpt}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
