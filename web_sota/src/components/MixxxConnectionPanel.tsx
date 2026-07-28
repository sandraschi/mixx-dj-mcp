import { useCallback, useEffect, useState } from "react";
import {
  Play,
  Radio,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import {
  fetchMixxxDetect,
  fetchMixxxStatus,
  fetchEngineCapabilities,
  fetchAppSettings,
  launchMixxx,
  probeMixxxOsc,
  type MixxxInstallation,
  type MixxxStatusResponse,
} from "../lib/api";
import { useStore } from "../lib/store";

export default function MixxxConnectionPanel() {
  const setEngineCaps = useStore((s) => s.setEngineCaps);
  const [status, setStatus] = useState<MixxxStatusResponse | null>(null);
  const [installations, setInstallations] = useState<MixxxInstallation[]>([]);
  const [engine, setEngine] = useState<"mixxxxx" | "mixxx">("mixxxxx");
  const [exePath, setExePath] = useState("");
  const [oscHost, setOscHost] = useState("127.0.0.1");
  const [oscIn, setOscIn] = useState(11119);
  const [oscOut, setOscOut] = useState(11118);
  const [busy, setBusy] = useState<"launch" | "probe" | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [st, det, settings] = await Promise.all([
        fetchMixxxStatus(),
        fetchMixxxDetect(),
        fetchAppSettings().catch(() => null),
      ]);
      setStatus(st);
      setInstallations(det.installations);
      if (settings) {
        setOscHost(settings.mixx_host);
        setOscIn(settings.osc_in_port);
        setOscOut(settings.osc_out_port);
      }
      try {
        const caps = await fetchEngineCapabilities();
        setEngineCaps(caps);
      } catch {
        /* optional */
      }
      if (!exePath && det.installations.length > 0) {
        const preferred =
          det.installations.find((i) => i.engine === engine && i.exists) ||
          det.installations.find((i) => i.exists);
        if (preferred) setExePath(preferred.path);
      }
    } catch {
      setStatus(null);
    }
  }, [engine, exePath]);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 8000);
    return () => clearInterval(t);
  }, [refresh]);

  useEffect(() => {
    const match = installations.find((i) => i.engine === engine && i.exists);
    if (match) setExePath(match.path);
  }, [engine, installations]);

  const onLaunch = async () => {
    setBusy("launch");
    setMessage(null);
    try {
      const r = await launchMixxx({
        engine,
        path: exePath || undefined,
        osc_port_in: oscIn,
        osc_port_out: oscOut,
        osc_host_out: oscHost,
      });
      setMessage(r.message);
      await refresh();
      if (r.success && !r.already_running) {
        setTimeout(() => probeMixxxOsc().then(refresh), 4000);
      }
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Launch failed");
    }
    setBusy(null);
  };

  const onProbe = async () => {
    setBusy("probe");
    setMessage(null);
    try {
      const r = await probeMixxxOsc();
      setMessage(r.message);
      await refresh();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Probe failed");
    }
    setBusy(null);
  };

  const procRunning = status?.process.running ?? false;
  const oscConnected = status?.osc.connected ?? false;

  return (
    <div
      data-testid="mixxx-connection-panel"
      className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-4"
    >
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Radio size={16} className="text-amber-400" />
            DJ Engine (Mixxx / mixxxxx)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            MCP backend does not start Mixxx — launch and connect OSC here.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5">
            {procRunning ? (
              <CheckCircle2 size={14} className="text-green-400" />
            ) : (
              <AlertCircle size={14} className="text-red-400" />
            )}
            App {procRunning ? "running" : "stopped"}
          </span>
          <span className="flex items-center gap-1.5">
            {oscConnected ? (
              <CheckCircle2 size={14} className="text-green-400" />
            ) : (
              <AlertCircle size={14} className="text-amber-400" />
            )}
            OSC {oscConnected ? "connected" : "offline"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            Engine
          </label>
          <select
            data-testid="mixxx-engine-select"
            value={engine}
            onChange={(e) => setEngine(e.target.value as "mixxx" | "mixxxxx")}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          >
            <option value="mixxxxx">mixxxxx (video fork)</option>
            <option value="mixxx">Mixxx (vanilla)</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            Executable
          </label>
          <select
            data-testid="mixxx-exe-select"
            value={exePath}
            onChange={(e) => setExePath(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono text-xs"
          >
            <option value="">— select detected install —</option>
            {installations
              .filter((i) => i.exists)
              .map((i) => (
                <option key={i.path} value={i.path}>
                  [{i.engine}] {i.path}
                </option>
              ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            OSC host out
          </label>
          <input
            type="text"
            value={oscHost}
            onChange={(e) => setOscHost(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-xs"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            Mixxx listen (in)
          </label>
          <input
            type="number"
            value={oscIn}
            onChange={(e) => setOscIn(Number(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-xs"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            MCP listen (out)
          </label>
          <input
            type="number"
            value={oscOut}
            onChange={(e) => setOscOut(Number(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-xs"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          data-testid="mixxx-launch-btn"
          onClick={onLaunch}
          disabled={busy !== null || !exePath}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/15 text-emerald-400 text-sm font-medium hover:bg-emerald-500/25 disabled:opacity-50"
        >
          {busy === "launch" ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Play size={14} />
          )}
          Launch
        </button>
        <button
          type="button"
          data-testid="mixxx-probe-btn"
          onClick={onProbe}
          disabled={busy !== null}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/10 text-amber-400 text-sm font-medium hover:bg-amber-500/20 disabled:opacity-50"
        >
          {busy === "probe" ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <RefreshCw size={14} />
          )}
          Probe OSC
        </button>
      </div>

      {status?.osc.setup_hint && !oscConnected && (
        <p className="text-xs text-slate-500 border border-slate-800 rounded-lg p-3 bg-slate-950/50">
          {status.osc.setup_hint}
        </p>
      )}

      {message && (
        <p
          className={`text-xs rounded-lg p-2 ${
            message.toLowerCase().includes("connected") ||
            message.toLowerCase().includes("started") ||
            message.toLowerCase().includes("already running")
              ? "text-green-400 bg-green-500/10"
              : "text-amber-300 bg-amber-500/10"
          }`}
        >
          {message}
        </p>
      )}

      {status?.fork?.summary && (
        <p className="text-xs text-slate-500">{status.fork.summary}</p>
      )}

      {status?.capabilities?.is_vanilla && (
        <p className="text-xs text-amber-400/90 border border-amber-500/20 rounded-lg px-3 py-2 bg-amber-500/5">
          Vanilla Mixxx — video, stems, NDI, and video skins are disabled in this webapp.
          Launch <strong>mixxxxx</strong> for the full AV stack.
        </p>
      )}

      {status?.fork?.is_mixxxxx && status?.osc?.connected && (
        <p className="text-[10px] text-purple-400">
          mixxxxx — deck video, stems, and NDI available when enabled in-app.
        </p>
      )}
    </div>
  );
}
