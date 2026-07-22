import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Volume2, Download, Loader2, AlertCircle, Music } from "lucide-react";
import type { SFXSound } from "../lib/types";

const SFX_API = "http://127.0.0.1:11120";

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}m ${s}s`;
}

export default function SFXPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SFXSound[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState<number | null>(null);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `${SFX_API}/api/sounds/search?q=${encodeURIComponent(q)}`,
        { headers: { Accept: "application/json" } },
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const items: SFXSound[] = (data.results || data.sounds || []).map(
        (item: Record<string, unknown>) => ({
          id: Number(item.id ?? 0),
          name: String(item.name ?? item.title ?? "Untitled"),
          duration: Number(item.duration ?? 0),
          tags: Array.isArray(item.tags) ? (item.tags as string[]) : [],
          preview_url: String(item.preview_url ?? item.url ?? ""),
          license: String(item.license ?? "Unknown"),
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

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") doSearch(query);
    },
    [query, doSearch],
  );

  const handlePlay = useCallback(
    (sound: SFXSound) => {
      if (playing === sound.id) {
        setPlaying(null);
        return;
      }
      setPlaying(sound.id);
      if (sound.preview_url) {
        const audio = new Audio(sound.preview_url);
        audio.onended = () => setPlaying(null);
        audio.play().catch(() => setPlaying(null));
      }
    },
    [playing],
  );

  const handleDownload = useCallback(async (sound: SFXSound) => {
    if (!sound.preview_url) return;
    try {
      const r = await fetch(sound.preview_url);
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${sound.name.replace(/[^a-zA-Z0-9_-]/g, "_")}.wav`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // download failed silently
    }
  }, []);

  return (
    <div
      data-testid="sfx-panel"
      className="rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col h-full"
    >
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
        <Music size={16} className="text-amber-400 shrink-0" />
        <span className="text-sm font-semibold text-slate-200">
          SFX Browser
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
            onKeyDown={handleKeyDown}
            placeholder="Search sound effects..."
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
            No sounds found
          </p>
        )}

        {!loading && !error && results.length === 0 && !query && (
          <p className="text-xs text-slate-600 text-center py-8">
            Search for sound effects
          </p>
        )}

        <AnimatePresence initial={false}>
          {results.map((sound) => (
            <motion.div
              key={sound.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-slate-800/30 hover:bg-slate-800/60 transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-200 truncate">
                  {sound.name}
                </p>
                <p className="text-[11px] text-slate-500">
                  {sound.license}
                  {sound.duration > 0 && ` \u00b7 ${formatDuration(sound.duration)}`}
                </p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {sound.preview_url && (
                  <button
                    onClick={() => handlePlay(sound)}
                    title={playing === sound.id ? "Stop" : "Preview"}
                    className={`p-1.5 rounded-md transition-colors ${
                      playing === sound.id
                        ? "bg-green-500/20 text-green-400"
                        : "text-slate-500 hover:text-slate-200 hover:bg-slate-700/50 opacity-0 group-hover:opacity-100"
                    }`}
                  >
                    <Volume2 size={14} />
                  </button>
                )}
                {sound.preview_url && (
                  <button
                    onClick={() => handleDownload(sound)}
                    title="Download"
                    className="p-1.5 rounded-md text-slate-500 hover:text-amber-400 hover:bg-slate-700/50 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <Download size={14} />
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
