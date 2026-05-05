import { cn } from "@/lib/utils";

interface Props {
  docId: string;
  score?: number;
  className?: string;
}

export function CitationBadge({ docId, score, className }: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-fed-accent/10 px-2 py-0.5 text-xs font-medium text-fed-accent",
        className
      )}
    >
      {docId}
      {score != null && (
        <span className="text-fed-muted">({(score * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
}
