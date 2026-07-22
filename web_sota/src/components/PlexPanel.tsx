import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Film, Loader2, ExternalLink, AlertCircle } from "lucide-react";
import type { PlexMediaItem } from "../lib/types";

const PLEX_API = "http://127.0.0.1:10740";

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

export default function PlexPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PlexMediaItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(null);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setLoading(false);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `${PLEX_API}/api/library/search?query=${encodeURIComponent(q)}`,
        { headers: { Accept: "application/json" } },
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const items: PlexMediaItem[] = (data.results || data.media || []).map(
        (item: Record<string, unknown>) => ({
          id: String(item.id ?? item.rating_key ?? ""),
          title: String(item.title ?? "Untitled"),
          year: Number(item.year ?? 0),
          duration: Number(item.duration ?? 0),
          type: item.type as PlexMediaItem["type"],
        }),
      );
      setResults(items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(query), 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, doSearch]);

  const handleExtract = useCallback(async (item: PlexMediaItem) => {
    try {
      await fetch(`${PLEX_API}/api/media/${item.id}/extract`, {
        method: "POST",
      });
    } catch {
      // silently fail — Plex may not support this endpoint
    }
  }, []);

  return (
    <div
      data-testid="plex-panel"
      className="rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col h-full"
    >
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
        <Film size={16} className="text-amber-400 shrink-0" />
        <span className="text-sm font-semibold text-slate-200">
          Plex Search
        </span>
      </div>

      <div className="p-3">
        <div className="relative">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Plex library..."
            className="w-full pl-9 pr-3 py-2 text-sm rounded-lg bg-slate-800/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1.5 min-h-0">
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={20} className="text-slate-500 animate-spin" />
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 py-4 px-3 text-xs text-red-400 bg-red-500/10 rounded-lg">
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && results.length === 0 && query && (
          <p className="text-xs text-slate-500 text-center py-8">
            No results found
          </p>
        )}

        {!loading && !error && results.length === 0 && !query && (
          <p className="text-xs text-slate-600 text-center py-8">
            Search your Plex media library
          </p>
        )}

        <AnimatePresence initial={false}>
          {results.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-slate-800/30 hover:bg-slate-800/60 transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-200 truncate">
                  {item.title}
                </p>
                <p className="text-[11px] text-slate-500">
                  {item.year} &middot; {item.type}
                  {item.duration > 0 && ` \u00b7 ${formatDuration(item.duration)}`}
                </p>
              </div>
              <button
                onClick={() => handleExtract(item)}
                title="Extract audio"
                className="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium rounded-md bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors opacity-0 group-hover:opacity-100 shrink-0"
              >
                <ExternalLink size={12} />
                Extract
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
