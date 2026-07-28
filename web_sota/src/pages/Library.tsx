import { useState, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Disc3, Loader2, Check, Filter } from "lucide-react";
import {
  API_BASE,
  fetchLibrarySearch,
  fetchPlexLibraries,
  libraryArtworkUrl,
  type LibraryItem,
  type LibrarySearchFilters,
  type PlexLibrary,
} from "../lib/api";
import { useStore } from "../lib/store";
import { FeatureNotice } from "../components/FeatureGate";
import { featureEnabled } from "../lib/capabilities";

const MODES = [
  { id: "auto", label: "Auto" },
  { id: "plex", label: "Plex" },
  { id: "semantic", label: "Semantic" },
  { id: "mixxx", label: "Mixxx only" },
] as const;

export default function Library() {
  const engineCaps = useStore((s) => s.engineCaps);
  const canLoadDeck = featureEnabled(engineCaps, "deck_load");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<(LibraryItem & { loading?: boolean })[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [targetDeck, setTargetDeck] = useState(1);
  const [loadedTrack, setLoadedTrack] = useState<string | null>(null);
  const [searchNote, setSearchNote] = useState<string | null>(null);
  const [engine, setEngine] = useState<string | null>(null);
  const [plexAvailable, setPlexAvailable] = useState(false);
  const [libraries, setLibraries] = useState<PlexLibrary[]>([]);
  const [showFilters, setShowFilters] = useState(true);
  const [filters, setFilters] = useState<LibrarySearchFilters>({
    mode: "auto",
    include_mixxx: true,
    media_type: "track",
  });

  useEffect(() => {
    fetchPlexLibraries()
      .then((r) => {
        setPlexAvailable(r.plex_available);
        setLibraries(
          (r.libraries || []).map((lib) => ({
            id: String(lib.id),
            title: String(lib.title || lib.id),
            type: String(lib.type || ""),
          }))
        );
      })
      .catch(() => setPlexAvailable(false));
  }, []);

  const search = useCallback(async () => {
    const q = query.trim();
    if (!q && !filters.genre && !filters.year && !filters.library_id) {
      setResults([]);
      setTotal(0);
      return;
    }
    setLoading(true);
    setSearchNote(null);
    try {
      const r = await fetchLibrarySearch({
        ...filters,
        query: q,
        limit: 50,
      });
      setResults(r.results);
      setTotal(r.total);
      setEngine(r.engine || null);
      setPlexAvailable(Boolean(r.plex_available));
      if (r.message) {
        setSearchNote(r.message);
      }
    } catch (err) {
      setResults([]);
      setTotal(0);
      setSearchNote(err instanceof Error ? err.message : "Search failed");
    }
    setLoading(false);
  }, [query, filters]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    search();
  };

  const loadToDeck = useCallback(
    async (track: LibraryItem) => {
      setResults((prev) =>
        prev.map((t) => (t.id === track.id ? { ...t, loading: true } : t))
      );
      try {
        let trackPath = track.id;
        if (track.id.startsWith("plex:")) {
          const resolve = await fetch(`${API_BASE}/api/library/resolve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ track_ref: track.id }),
          });
          if (resolve.ok) {
            const body = await resolve.json();
            trackPath = body.path || track.id;
          }
        }
        const r = await fetch(`${API_BASE}/api/v1/deck/${targetDeck}/load`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ track_path: trackPath }),
        });
        if (r.ok) {
          setLoadedTrack(track.id);
          setTimeout(() => setLoadedTrack(null), 2000);
        }
      } catch {
        // silent
      }
      setResults((prev) =>
        prev.map((t) => (t.id === track.id ? { ...t, loading: false } : t))
      );
    },
    [targetDeck]
  );

  return (
    <div data-testid="library-page" className="space-y-6">
      <FeatureNotice caps={engineCaps} feature="deck_load" />
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Library</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Plex intelligent search {plexAvailable ? "(connected)" : "(offline — Mixxx fallback)"}
            {engine ? ` · ${engine}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>Load to deck:</span>
          {[1, 2, 3, 4].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => setTargetDeck(d)}
              className={`w-7 h-7 rounded text-xs font-mono transition-colors ${
                targetDeck === d
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  : "bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600"
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Plex + Mixxx — e.g. 128 bpm tech house, or tracks like Daft Punk"
              className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors"
              data-testid="library-search"
            />
          </div>
          <button
            type="button"
            onClick={() => setShowFilters((v) => !v)}
            className="px-3 py-2 rounded-lg border border-slate-700 text-slate-400 hover:text-slate-200"
            title="Toggle filters"
          >
            <Filter size={16} />
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-amber-500/10 text-amber-400 rounded-lg text-sm font-medium hover:bg-amber-500/20 transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : "Search"}
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3 rounded-lg border border-slate-800 bg-slate-900/40">
            <label className="text-sm text-slate-400">
              Mode
              <select
                value={filters.mode || "auto"}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    mode: e.target.value as LibrarySearchFilters["mode"],
                  }))
                }
                className="mt-1 w-full rounded bg-slate-900 border border-slate-700 px-2 py-1.5 text-sm text-slate-200"
              >
                {MODES.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-400">
              Plex library
              <select
                value={filters.library_id || ""}
                onChange={(e) =>
                  setFilters((f) => ({ ...f, library_id: e.target.value || undefined }))
                }
                className="mt-1 w-full rounded bg-slate-900 border border-slate-700 px-2 py-1.5 text-sm text-slate-200"
              >
                <option value="">All libraries</option>
                {libraries.map((lib) => (
                  <option key={lib.id} value={lib.id}>
                    {lib.title} ({lib.type})
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-400">
              Genre / tag
              <input
                value={filters.genre || ""}
                onChange={(e) => setFilters((f) => ({ ...f, genre: e.target.value || undefined }))}
                placeholder="Tech House"
                className="mt-1 w-full rounded bg-slate-900 border border-slate-700 px-2 py-1.5 text-sm text-slate-200"
              />
            </label>
            <label className="text-sm text-slate-400">
              Year
              <input
                type="number"
                value={filters.year ?? ""}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    year: e.target.value ? Number(e.target.value) : undefined,
                  }))
                }
                className="mt-1 w-full rounded bg-slate-900 border border-slate-700 px-2 py-1.5 text-sm text-slate-200"
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-400 col-span-2">
              <input
                type="checkbox"
                checked={filters.include_mixxx !== false}
                onChange={(e) => setFilters((f) => ({ ...f, include_mixxx: e.target.checked }))}
              />
              Include local Mixxx library fallback
            </label>
          </div>
        )}
      </form>

      {searchNote && <p className="text-sm text-amber-400/90">{searchNote}</p>}

      {total > 0 && (
        <p className="text-sm text-slate-500">
          {total} result(s) · Deck {targetDeck}
        </p>
      )}

      <div className="space-y-1">
        {results.map((track) => {
          const art = libraryArtworkUrl(track);
          return (
          <motion.div
            key={`${track.source || "x"}-${track.id}`}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors group"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {art ? (
              <img
                src={art}
                alt=""
                className="w-10 h-10 rounded object-cover shrink-0 bg-slate-800 border border-slate-700"
                loading="lazy"
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }}
              />
            ) : (
              <Disc3 size={16} className="text-slate-600 shrink-0" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 truncate">{track.title}</p>
              <p className="text-sm text-slate-400 truncate">{track.artist}</p>
              {(track.genres?.length || track.tags?.length) ? (
                <p className="text-xs text-slate-500 truncate mt-0.5">
                  {[...(track.genres || []), ...(track.tags || [])].slice(0, 4).join(" · ")}
                </p>
              ) : null}
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400 shrink-0">
              {track.source && (
                <span className="text-xs uppercase tracking-wide text-slate-500">{track.source}</span>
              )}
              {track.bpm > 0 && (
                <span className="font-mono text-amber-400/80">{track.bpm.toFixed(1)}</span>
              )}
              {track.year ? <span>{track.year}</span> : null}
              <span>{track.length}</span>
            </div>
            <button
              type="button"
              onClick={() => loadToDeck(track)}
              disabled={track.loading || !canLoadDeck}
              className="px-3 py-1 text-sm font-medium rounded bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-all disabled:opacity-50"
            >
              {track.loading ? (
                <Loader2 size={12} className="animate-spin" />
              ) : loadedTrack === track.id ? (
                <Check size={12} />
              ) : (
                `Load ${targetDeck}`
              )}
            </button>
          </motion.div>
          );
        })}
      </div>
    </div>
  );
}
