import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Search, Disc3, Loader2 } from "lucide-react";
import { fetchLibraryQuery, type LibraryItem } from "../lib/api";

export default function Library() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LibraryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const search = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }
    setLoading(true);
    try {
      const r = await fetchLibraryQuery(q);
      setResults(r.results);
      setTotal(r.total);
    } catch {
      setResults([]);
      setTotal(0);
    }
    setLoading(false);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    search(query);
  };

  return (
    <div data-testid="library-page" className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-100">Library</h2>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search tracks..."
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors"
            data-testid="library-search"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-4 py-2 bg-amber-500/10 text-amber-400 rounded-lg text-sm font-medium hover:bg-amber-500/20 transition-colors disabled:opacity-50"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : "Search"}
        </button>
      </form>

      {total > 0 && (
        <p className="text-xs text-slate-500">{total} result(s)</p>
      )}

      <div className="space-y-1">
        {results.map((track) => (
          <motion.div
            key={track.id}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors group"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Disc3 size={16} className="text-slate-600 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 truncate">{track.title}</p>
              <p className="text-xs text-slate-500 truncate">
                {track.artist}
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-500 shrink-0">
              <span className="font-mono text-amber-400/80">
                {track.bpm.toFixed(1)}
              </span>
              <span>{track.key}</span>
              <span>{track.length}</span>
            </div>
            <button className="px-3 py-1 text-xs font-medium rounded bg-amber-500/10 text-amber-400 opacity-0 group-hover:opacity-100 hover:bg-amber-500/20 transition-all">
              Load
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
