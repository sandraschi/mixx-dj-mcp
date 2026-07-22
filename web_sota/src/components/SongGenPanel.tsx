import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Music, Loader2, Wand2 } from "lucide-react";
import { API_BASE } from "../lib/api";

const SONG_API = "http://127.0.0.1:10885";

export default function SongGenPanel() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ file?: string; duration?: number } | null>(null);
  const [error, setError] = useState("");

  const generate = useCallback(async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${SONG_API}/api/v1/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt.trim(), duration: 30 }),
        signal: AbortSignal.timeout(120000),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed");
    }
    setLoading(false);
  }, [prompt]);

  const loadToDeck = useCallback(async (deck: number) => {
    if (!result?.file) return;
    try {
      await fetch(`${API_BASE}/api/v1/deck/${deck}/load`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ track_path: result.file }),
      });
    } catch {}
  }, [result]);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4" data-testid="songgen-panel">
      <div className="flex items-center gap-2 mb-3">
        <Music size={14} className="text-purple-400" />
        <h3 className="text-sm font-medium text-slate-300">AI Music Gen</h3>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Motörhead-style fast rock riff, 140 BPM..."
          className="flex-1 px-3 py-1.5 text-xs rounded-lg bg-slate-800/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
        />
        <button
          onClick={generate}
          disabled={loading || !prompt.trim()}
          className="px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 text-xs font-medium transition-colors disabled:opacity-50"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Wand2 size={14} />}
        </button>
      </div>

      {error && (
        <p className="mt-2 text-[10px] text-red-400">{error}</p>
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 p-3 rounded-lg bg-slate-800/40 border border-slate-700"
        >
          <p className="text-xs text-slate-300 mb-2">Generated</p>
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((d) => (
              <button
                key={d}
                onClick={() => loadToDeck(d)}
                className="flex-1 py-1.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors"
              >
                Load D{d}
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
