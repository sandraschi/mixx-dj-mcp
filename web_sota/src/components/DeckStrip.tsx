import { motion } from "framer-motion";
import { Play, Pause, Disc3 } from "lucide-react";
import { useStore } from "../lib/store";

export default function DeckStrip() {
  const decks = useStore((s) => s.decks);

  return (
    <div
      data-testid="deck-strip"
      className="grid grid-cols-4 gap-3"
    >
      {decks.map((deck, i) => (
        <motion.div
          key={deck.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04 }}
          className="rounded-xl border border-slate-800 bg-slate-900/50 p-3 hover:border-slate-700 transition-colors"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <Disc3 size={14} className="text-amber-400" />
              <span className="text-xs font-semibold text-slate-400">
                D{deck.id}
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              {deck.playing ? (
                <Play size={12} className="text-green-400" />
              ) : (
                <Pause size={12} className="text-slate-500" />
              )}
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  deck.playing ? "bg-green-400 animate-pulse" : "bg-slate-600"
                }`}
              />
            </div>
          </div>

          <p className="text-sm font-medium text-slate-100 truncate leading-tight">
            {deck.track_title}
          </p>
          {deck.track_artist && (
            <p className="text-[11px] text-slate-500 truncate mt-0.5">
              {deck.track_artist}
            </p>
          )}

          <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-500">
            <span className="font-mono text-amber-400/80">
              {deck.bpm.toFixed(1)}
            </span>
            <span className="text-slate-700">|</span>
            <span>{deck.key}</span>
            {deck.sync_enabled && (
              <>
                <span className="text-slate-700">|</span>
                <span className="text-amber-400/80 text-[10px] font-semibold uppercase">
                  Sync
                </span>
              </>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
