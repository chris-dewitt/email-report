import { useState } from "react";
import { useBriefing } from "@/api/hooks";
import type { BriefingResponse } from "@/types";
import { Bot, Send, Clock } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: { series_id: string; context: string }[];
  model?: string;
  timestamp: Date;
}

const QUICK_QUESTIONS = [
  "What are the key macro developments this week?",
  "Is the labor market showing signs of softening?",
  "How are inflation expectations trending?",
  "What do credit spreads and financial conditions suggest?",
  "Summarize the current yield curve dynamics",
];

export function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const { mutateAsync, isPending } = useBriefing();

  const sendMessage = async (question: string) => {
    if (!question.trim() || isPending) return;

    const userMsg: ChatMessage = {
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const result: BriefingResponse = await mutateAsync({
        question,
        lookback_days: 7,
      });

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: result.summary,
        citations: result.citations,
        model: result.model_used,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: ChatMessage = {
        role: "assistant",
        content: `Error: ${String(err)}. Make sure Ollama is running.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-atlas-text">Macro Copilot</h2>
        <p className="text-sm text-atlas-muted">
          Ask questions about the macro environment — powered by your local LLM
        </p>
      </div>

      {/* Quick questions */}
      {messages.length === 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-medium text-atlas-muted uppercase tracking-wider">
            Quick Questions
          </p>
          <div className="flex flex-wrap gap-2">
            {QUICK_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="rounded-full border border-atlas-border bg-atlas-surface px-3 py-1.5 text-xs text-atlas-muted hover:text-atlas-text hover:border-atlas-accent/40 transition"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat area */}
      <div className="flex-1 space-y-4 overflow-auto pb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
          >
            {msg.role === "assistant" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-atlas-purple/10">
                <Bot size={16} className="text-atlas-purple" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-lg p-3 ${
                msg.role === "user"
                  ? "bg-atlas-accent/10 text-atlas-text"
                  : "border border-atlas-border bg-atlas-surface"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.content}
              </p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {msg.citations.map((c, j) => (
                    <span
                      key={j}
                      className="rounded bg-atlas-purple/10 px-2 py-0.5 text-xs font-mono text-atlas-purple"
                      title={c.context}
                    >
                      {c.series_id}
                    </span>
                  ))}
                </div>
              )}
              <div className="mt-1 flex items-center gap-2 text-[10px] text-atlas-muted">
                <Clock size={10} />
                {msg.timestamp.toLocaleTimeString()}
                {msg.model && <span>• {msg.model}</span>}
              </div>
            </div>
          </div>
        ))}

        {isPending && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-atlas-purple/10">
              <Bot size={16} className="text-atlas-purple animate-pulse" />
            </div>
            <div className="rounded-lg border border-atlas-border bg-atlas-surface p-3">
              <div className="flex items-center gap-2 text-sm text-atlas-muted">
                <div className="flex gap-1">
                  <div className="h-1.5 w-1.5 rounded-full bg-atlas-purple animate-bounce" />
                  <div className="h-1.5 w-1.5 rounded-full bg-atlas-purple animate-bounce [animation-delay:0.2s]" />
                  <div className="h-1.5 w-1.5 rounded-full bg-atlas-purple animate-bounce [animation-delay:0.4s]" />
                </div>
                Analyzing macro data...
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-atlas-border pt-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the macro environment..."
            disabled={isPending}
            className="flex-1 rounded-md border border-atlas-border bg-atlas-bg px-3 py-2 text-sm text-atlas-text placeholder:text-atlas-muted focus:border-atlas-accent focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isPending || !input.trim()}
            className="rounded-md bg-atlas-accent px-3 py-2 text-sm font-medium text-white hover:bg-atlas-accent/80 transition disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
