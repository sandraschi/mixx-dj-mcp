import { useCallback, useState } from "react";
import { motion } from "framer-motion";
import { Play, SkipBack, Lock, Disc3, Loader2 } from "lucide-react";
import { useStore } from "../lib/store";
import { API_BASE } from "../lib/api";

const hotCues = [1, 2, 3, 4, 5, 6, 7, 8];

export default function Decks() {
  const decks = useStore((s) => s.decks);
  const [loadingDeck, setLoadingDeck] = useState<number | null>(null);

  const deckAction = useCallback(async (deck: number, action: string, body?: object) => {
    setLoadingDeck(deck);
    try {
      await fetch(`${API_BASE}/api/v1/deck/${deck}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch {}
    setLoadingDeck(null);
  }, []);

  const pulseClass = (playing: boolean) =>
    playing ? "bg-green-400 animate-pulse" : "bg-slate-600";

  return (
    <div className="space-y-6" data-testid="decks-page">
      <h2 className="text-xl font-semibold text-slate-100">Deck Control</h2>
      <div className="grid grid-cols-2 gap-4">
        {decks.map((deck, i) => (
          <motion.div
            key={deck.id}
            className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Disc3 size={16} className="text-amber-400" />
                <span className="text-sm font-medium text-slate-200">
                  Deck {deck.id}
                </span>
                <span className={`w-2 h-2 rounded-full ${pulseClass(deck.playing)}`} />
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span className="font-mono text-amber-400/80">{deck.bpm.toFixed(1)}</span>
                <span>BPM</span>
                <span className="ml-1">{deck.key}</span>
              </div>
            </div>

            {/* Track info */}
            <div className="px-4 py-2 border-b border-slate-800/50">
              <p className="text-sm text-slate-200 truncate">{deck.track_title}</p>
              <p className="text-xs text-slate-500 truncate">{deck.track_artist}</p>
            </div>

            {/* Transport buttons */}
            <div className="flex gap-1 px-4 py-3 border-b border-slate-800/50">
              <button
                onClick={() => deckAction(deck.id, "play_pause")}
                disabled={loadingDeck === deck.id}
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 text-xs font-medium transition-colors disabled:opacity-50"
              >
                {loadingDeck === deck.id ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                {deck.playing ? "Pause" : "Play"}
              </button>
              <button
                onClick={() => deckAction(deck.id, "cue")}
                className="flex-1 py-2 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 text-xs font-medium transition-colors"
              >
                <SkipBack size={14} className="mx-auto" />
                Cue
              </button>
              <button
                onClick={() => deckAction(deck.id, "sync")}
                className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${
                  deck.sync_enabled
                    ? "bg-amber-500/20 text-amber-400"
                    : "bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700"
                }`}
              >
                <Lock size={14} className="mx-auto" />
                Sync
              </button>
            </div>

            {/* Hotcues */}
            <div className="px-4 py-2">
              <div className="grid grid-cols-8 gap-1">
                {hotCues.map((cue) => (
                  <button
                    key={cue}
                    className="aspect-square rounded-md bg-slate-800 hover:bg-slate-700 text-[9px] text-slate-500 hover:text-slate-300 font-mono transition-colors"
                    title={`Hotcue ${cue}`}
                  >
                    {cue}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
