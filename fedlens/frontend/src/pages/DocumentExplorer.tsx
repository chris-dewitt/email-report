import { useState } from "react";
import { useDocuments, useDocument, useSearch } from "@/api/hooks";
import { useFedLensStore } from "@/store";
import { formatDate, sentimentColor, sentimentLabel } from "@/lib/utils";
import { DOC_TYPES, DOC_TYPE_LABELS, type DocType } from "@/types";
import { Search, FileText, X } from "lucide-react";

export function DocumentExplorer() {
  const selectedDocType = useFedLensStore((s) => s.selectedDocType);
  const setDocType = useFedLensStore((s) => s.setDocType);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: docs, isLoading } = useDocuments(selectedDocType === "all" ? undefined : selectedDocType);
  const { data: detail } = useDocument(selectedDocId);
  const searchMutation = useSearch();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchMutation.mutate({
        query: searchQuery,
        doc_type: selectedDocType === "all" ? undefined : selectedDocType,
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-fed-text">Document Explorer</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setDocType("all")}
            className={`rounded px-3 py-1 text-xs font-medium transition ${
              selectedDocType === "all" ? "bg-fed-accent text-white" : "text-fed-muted hover:text-fed-text"
            }`}
          >
            All
          </button>
          {DOC_TYPES.map((dt) => (
            <button
              key={dt}
              onClick={() => setDocType(dt)}
              className={`rounded px-3 py-1 text-xs font-medium transition ${
                selectedDocType === dt ? "bg-fed-accent text-white" : "text-fed-muted hover:text-fed-text"
              }`}
            >
              {DOC_TYPE_LABELS[dt]}
            </button>
          ))}
        </div>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-fed-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Semantic search across documents..."
            className="w-full rounded-md border border-fed-border bg-fed-bg pl-10 pr-4 py-2 text-sm text-fed-text placeholder-fed-muted focus:border-fed-accent focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={searchMutation.isPending}
          className="rounded-md bg-fed-accent px-4 py-2 text-sm font-medium text-white hover:bg-fed-accent/80 disabled:opacity-50"
        >
          {searchMutation.isPending ? "Searching..." : "Search"}
        </button>
      </form>

      {/* Search results */}
      {searchMutation.data && (
        <div className="rounded-lg border border-fed-accent/30 bg-fed-surface p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-fed-accent">
              Search Results ({searchMutation.data.total})
            </h3>
            <button onClick={() => searchMutation.reset()} className="text-fed-muted hover:text-fed-text">
              <X size={16} />
            </button>
          </div>
          <div className="space-y-2 max-h-80 overflow-auto">
            {searchMutation.data.results.map((hit) => (
              <div
                key={hit.chunk_id}
                className="rounded border border-fed-border bg-fed-bg/50 p-3 cursor-pointer hover:border-fed-accent/50"
                onClick={() => setSelectedDocId(hit.doc_id)}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-fed-accent">{hit.doc_type}</span>
                  <span className="text-xs text-fed-muted">{formatDate(hit.date)}</span>
                  <span className="text-xs text-fed-muted">Score: {hit.score.toFixed(3)}</span>
                </div>
                <p className="text-sm text-fed-text line-clamp-2">{hit.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Document list */}
        <div className="lg:col-span-1 rounded-lg border border-fed-border bg-fed-surface p-4 max-h-[600px] overflow-auto">
          <h3 className="mb-3 text-sm font-semibold text-fed-muted uppercase tracking-wider">
            Documents ({docs?.total ?? 0})
          </h3>
          {isLoading ? (
            <p className="text-sm text-fed-muted">Loading...</p>
          ) : (
            <div className="space-y-1">
              {docs?.documents.map((doc) => (
                <button
                  key={doc.doc_id}
                  onClick={() => setSelectedDocId(doc.doc_id)}
                  className={`w-full text-left rounded-md px-3 py-2 text-sm transition ${
                    selectedDocId === doc.doc_id
                      ? "bg-fed-accent/10 text-fed-accent"
                      : "text-fed-text hover:bg-fed-border/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate font-medium">{doc.title || doc.doc_id}</span>
                    {doc.sentiment_score != null && (
                      <span className={`text-xs ${sentimentColor(doc.sentiment_score)}`}>
                        {sentimentLabel(doc.sentiment_score)}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-fed-muted mt-0.5">
                    {formatDate(doc.date)} &middot; {doc.chunk_count} chunks
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Document detail */}
        <div className="lg:col-span-2 rounded-lg border border-fed-border bg-fed-surface p-4 max-h-[600px] overflow-auto">
          {selectedDocId && detail ? (
            <div>
              <div className="mb-4">
                <h3 className="text-lg font-bold text-fed-text">{detail.doc_id}</h3>
                <p className="text-sm text-fed-muted">
                  {detail.doc_type} &middot; {formatDate(detail.date)} &middot; {detail.chunks.length} chunks
                </p>
              </div>
              <div className="space-y-3">
                {detail.chunks.map((chunk) => (
                  <div key={chunk.chunk_id} className="rounded border border-fed-border bg-fed-bg/50 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-fed-accent">{chunk.section}</span>
                      <span className="text-xs text-fed-muted">{chunk.token_count} tokens</span>
                    </div>
                    <p className="text-sm text-fed-text whitespace-pre-wrap">{chunk.text}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="text-center text-fed-muted">
                <FileText size={48} className="mx-auto mb-2 opacity-30" />
                <p className="text-sm">Select a document to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
