import { useEffect, useCallback, useState } from "react";
import { motion } from "framer-motion";
import {
  Play,
  Pause,
  RotateCcw,
  RefreshCw,
} from "lucide-react";
import { useStore } from "../lib/store";
import { API_BASE, fetchHealth, fetchDeckStatus } from "../lib/api";
import MixxxConnectionPanel from "../components/MixxxConnectionPanel";
import OnboardingPanel from "../components/OnboardingPanel";
import FirstRunPanel from "../components/FirstRunPanel";

export default function Dashboard() {
  const backendStatus = useStore((s) => s.backendStatus);
  const setBackendStatus = useStore((s) => s.setBackendStatus);
  const decks = useStore((s) => s.decks);
  const crossfader = useStore((s) => s.crossfader);
  const setDecks = useStore((s) => s.setDecks);
  const setCrossfader = useStore((s) => s.setCrossfader);
  const [healthData, setHealthData] = useState<{
    server: string;
    version: string;
    uptime_seconds: number;
    tool_count: number;
  } | null>(null);
  const [restarting, setRestarting] = useState(false);
  const [mixxxOsc, setMixxxOsc] = useState(false);
  const [mixxxRunning, setMixxxRunning] = useState(false);
  const [forkData, setForkData] = useState<{ fork: string; features: Record<string, boolean> } | null>(null);

  const refresh = useCallback(async () => {
    try {
      const h = await fetchHealth();
      setHealthData(h);
      setMixxxOsc(Boolean(h.providers?.mixxx_osc));
      setMixxxRunning(Boolean(h.mixxx_process_running));
      setBackendStatus("connected");
      try {
        const [ds, fk] = await Promise.all([
          fetchDeckStatus(),
          fetch(`${API_BASE}/api/v1/fork`).then((r) => (r.ok ? r.json() : null)),
        ]);
        setDecks(ds.decks);
        setCrossfader(ds.crossfader);
        setForkData(fk);
      } catch {
        // deck/fork optional when OSC offline
      }
    } catch {
      setBackendStatus("error");
    }
  }, [setBackendStatus, setDecks, setCrossfader]);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    let delay = 1000;
    const poll = async () => {
      await refresh();
      delay = backendStatus === "error" ? Math.min(delay * 2, 16000) : 10000;
      timer = setTimeout(poll, delay);
    };
    poll();
    return () => clearTimeout(timer);
  }, [backendStatus, refresh]);

  const restartBackend = useCallback(async () => {
    setRestarting(true);
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("start_backend");
    } catch {
      // not in Tauri — HTTP poll will update
    }
    setRestarting(false);
  }, []);

  return (
    <div data-testid="dashboard" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-100">Overview</h2>
        <div className="flex items-center gap-3">
          <span
            data-testid="backend-dot"
            className={`w-2.5 h-2.5 rounded-full ${
              backendStatus === "connected"
                ? "bg-green-500"
                : backendStatus === "error"
                  ? "bg-red-500"
                  : "bg-gray-500 animate-pulse"
            }`}
          />
          <span className="text-sm text-slate-400">
            Backend{" "}
            {backendStatus === "connected"
              ? "online"
              : backendStatus === "error"
                ? "offline"
                : "connecting…"}
          </span>
          {backendStatus === "connected" && (
            <span className="text-xs text-slate-500">
              · Mixxx {mixxxRunning ? "running" : "stopped"} · OSC{" "}
              {mixxxOsc ? "ok" : "down"}
            </span>
          )}
          {backendStatus === "error" && (
            <button
              onClick={restartBackend}
              disabled={restarting}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors disabled:opacity-50"
            >
              <RefreshCw
                size={14}
                className={restarting ? "animate-spin" : ""}
              />
              Restart Backend
            </button>
          )}
        </div>
      </div>

      <FirstRunPanel />
      <OnboardingPanel />
      <MixxxConnectionPanel />

      {healthData && (
        <div className="grid grid-cols-3 gap-4">
          <div
            data-testid="kpi-server"
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"
          >
            <span className="text-xs text-slate-500 uppercase tracking-wider">
              Server
            </span>
            <p className="text-lg font-semibold text-slate-100 mt-1">
              {healthData.server}
            </p>
            <p className="text-xs text-slate-500">
              v{healthData.version}
            </p>
          </div>
          <div
            data-testid="kpi-tools"
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"
          >
            <span className="text-xs text-slate-500 uppercase tracking-wider">
              Tools
            </span>
            <p className="text-lg font-semibold text-amber-400 mt-1">
              {healthData.tool_count}
            </p>
            <p className="text-xs text-slate-500">registered</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <span className="text-xs text-slate-500 uppercase tracking-wider">
              Uptime
            </span>
            <p className="text-lg font-semibold text-slate-100 mt-1">
              {Math.floor(healthData.uptime_seconds / 60)}m{" "}
              {healthData.uptime_seconds % 60}s
            </p>
            <p className="text-xs text-slate-500">since last restart</p>
          </div>
          {forkData && (
            <div
              data-testid="kpi-mixx-status"
              className={`rounded-xl border p-4 col-span-3 ${
                forkData.fork === "mixxxxx"
                  ? "border-purple-800 bg-purple-900/20"
                  : "border-slate-800 bg-slate-900/50"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider">
                    DJ Engine
                  </span>
                  <p className="text-lg font-semibold text-slate-100 mt-1">
                    {forkData.fork === "mixxxxx" ? "Mixxxxx" : "Mixxx (vanilla)"}
                  </p>
                </div>
                {forkData.fork === "mixxxxx" && (
                  <span className="px-2 py-1 rounded text-xs font-mono bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    Video fork
                  </span>
                )}
                {forkData.fork === "mixxx" && (
                  <span className="px-2 py-1 rounded text-xs text-slate-500 bg-slate-800">
                    No video support
                  </span>
                )}
                {forkData.fork === "mixxxxx" && (
                  <p className="text-[10px] text-slate-500 mt-2">
                    Video plays in mixxxxx window (projector). Webapp shows butterchurn MilkDrop visuals.
                  </p>
                )}
              </div>
              {forkData.fork === "mixxxxx" && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(forkData.features).filter(([, v]) => v).map(([k]) => (
                    <span key={k} className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                      {k.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {decks.map((deck) => (
          <motion.div
            key={deck.id}
            data-testid={`kpi-deck-${deck.id}`}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-3"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: deck.id * 0.05 }}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Deck {deck.id}
              </span>
              <div className="flex items-center gap-1.5">
                {deck.playing ? (
                  <Play size={14} className="text-green-400" />
                ) : (
                  <Pause size={14} className="text-slate-500" />
                )}
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    deck.playing ? "bg-green-400 animate-pulse" : "bg-slate-600"
                  }`}
                />
              </div>
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
              <span className="flex items-center gap-1">
                <RotateCcw size={12} />
                {deck.bpm.toFixed(1)} BPM
              </span>
              <span>{deck.key}</span>
              {deck.sync_enabled && (
                <span className="text-amber-400 text-[10px] font-semibold uppercase">
                  Sync
                </span>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <span className="text-xs text-slate-500 uppercase tracking-wider">
          Crossfader
        </span>
        <div className="mt-3 relative h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="absolute top-0 h-full w-1 bg-amber-400 rounded-full transition-all duration-150"
            style={{
              left: `${((crossfader + 1) / 2) * 100}%`,
              transform: "translateX(-50%)",
            }}
          />
          <div
            className="h-full bg-amber-500/20 rounded-full transition-all duration-150"
            style={{
              width: `${Math.abs(crossfader) * 50}%`,
              marginLeft:
                crossfader < 0 ? `${((crossfader + 1) / 2) * 100}%` : "50%",
            }}
          />
        </div>
        <div className="flex justify-between mt-1 text-[10px] text-slate-600">
          <span>Deck 1/2</span>
          <span>Deck 3/4</span>
        </div>
      </div>
    </div>
  );
}
