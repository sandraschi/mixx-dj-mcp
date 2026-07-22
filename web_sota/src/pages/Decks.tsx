import { motion } from "framer-motion";
import {
  Play,
  Square,
  SkipBack,
  Repeat,
  Lock,
  Waves,
  Disc3,
} from "lucide-react";
import { useStore } from "../lib/store";

const hotCues = [1, 2, 3, 4, 5, 6, 7, 8];

export default function Decks() {
  const decks = useStore((s) => s.decks);

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
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Disc3 size={16} className="text-amber-400" />
                <span className="font-semibold text-sm text-slate-200">
                  Deck {deck.id}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    deck.playing
                      ? "bg-green-500/20 text-green-400"
                      : "bg-slate-800 text-slate-500"
                  }`}
                >
                  {deck.playing ? "PLAYING" : "STOPPED"}
                </span>
              </div>
            </div>

            <div className="p-4 space-y-4">
              <div className="h-16 rounded-lg bg-slate-800/50 flex items-center justify-center">
                <Waves size={24} className="text-slate-600" />
                <span className="text-xs text-slate-600 ml-2">Waveform</span>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-100 truncate">
                  {deck.track_title}
                </p>
                {deck.track_artist && (
                  <p className="text-xs text-slate-500 truncate">
                    {deck.track_artist}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="font-mono text-amber-400">
                  {deck.bpm.toFixed(1)}
                </span>
                <span className="text-slate-600">|</span>
                <span>{deck.key}</span>
              </div>

              <div className="flex items-center gap-2">
                <button className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors">
                  <Play size={16} />
                </button>
                <button className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors">
                  <Square size={16} />
                </button>
                <button className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 transition-colors">
                  <SkipBack size={16} />
                </button>
                <button
                  className={`p-2 rounded-lg transition-colors ${
                    deck.sync_enabled
                      ? "bg-amber-500/20 text-amber-400"
                      : "bg-slate-800 text-slate-500 hover:bg-slate-700"
                  }`}
                >
                  <Repeat size={16} />
                </button>
                <button className="p-2 rounded-lg bg-slate-800 text-slate-500 hover:bg-slate-700 transition-colors">
                  <Lock size={16} />
                </button>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                  Hot Cues
                </span>
                <div className="grid grid-cols-8 gap-1 mt-1">
                  {hotCues.map((cue) => (
                    <button
                      key={cue}
                      className="aspect-square rounded bg-slate-800 text-[10px] text-slate-500 hover:bg-slate-700 hover:text-slate-300 transition-colors font-mono"
                    >
                      {cue}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                    Volume
                  </span>
                  <div className="mt-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all"
                      style={{ width: `${deck.volume * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                    Gain
                  </span>
                  <div className="mt-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full transition-all"
                      style={{ width: `${(deck.gain / 2) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
