import type { DocumentMeta } from "@/types";
import { formatDate, sentimentColor, sentimentLabel } from "@/lib/utils";
import { DOC_TYPE_LABELS, type DocType } from "@/types";

interface Props {
  documents: DocumentMeta[];
}

export function RecentDocs({ documents }: Props) {
  if (!documents.length) {
    return <p className="text-sm text-fed-muted">No documents ingested yet.</p>;
  }

  const recent = documents.slice(0, 10);

  return (
    <div className="space-y-2">
      {recent.map((doc) => (
        <div
          key={doc.doc_id}
          className="flex items-center justify-between rounded-md border border-fed-border bg-fed-bg/50 px-3 py-2"
        >
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-fed-text">{doc.title || doc.doc_id}</p>
            <p className="text-xs text-fed-muted">
              {DOC_TYPE_LABELS[doc.doc_type as DocType] ?? doc.doc_type} &middot; {formatDate(doc.date)} &middot; {doc.chunk_count} chunks
            </p>
          </div>
          {doc.sentiment_score != null && (
            <span className={`text-xs font-medium ${sentimentColor(doc.sentiment_score)}`}>
              {sentimentLabel(doc.sentiment_score)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
