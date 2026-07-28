import { useCallback, useEffect, useState } from "react";
import {
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Loader2,
  Sparkles,
  X,
} from "lucide-react";
import {
  fetchAppSettings,
  fetchMixxxDetect,
  fetchOscPortStatus,
  launchMixxx,
  probeMixxxOsc,
  saveAppSettings,
  type MixxxInstallation,
  type OscPortStatus,
} from "../lib/api";

const STORAGE_KEY = "mixx-dj-onboarding-v1";

export function isOnboardingComplete(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "done";
  } catch {
    return true;
  }
}

export function markOnboardingComplete(): void {
  try {
    localStorage.setItem(STORAGE_KEY, "done");
  } catch {
    /* ignore */
  }
}

type Step = 0 | 1 | 2 | 3;

interface OnboardingPanelProps {
  onComplete?: () => void;
}

export default function OnboardingPanel({ onComplete }: OnboardingPanelProps) {
  const [visible, setVisible] = useState(!isOnboardingComplete());
  const [step, setStep] = useState<Step>(0);
  const [engine, setEngine] = useState<"mixxxxx" | "mixxx">("mixxxxx");
  const [exePath, setExePath] = useState("");
  const [installations, setInstallations] = useState<MixxxInstallation[]>([]);
  const [host, setHost] = useState("127.0.0.1");
  const [oscIn, setOscIn] = useState(11119);
  const [oscOut, setOscOut] = useState(11118);
  const [portStatus, setPortStatus] = useState<OscPortStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [oscOk, setOscOk] = useState(false);

  const refreshPorts = useCallback(async () => {
    try {
      const st = await fetchOscPortStatus({
        host,
        send_port: oscIn,
        listen_port: oscOut,
      });
      setPortStatus(st);
    } catch {
      setPortStatus(null);
    }
  }, [host, oscIn, oscOut]);

  useEffect(() => {
    if (!visible) return;
    fetchAppSettings()
      .then((s) => {
        setHost(s.mixx_host);
        setOscIn(s.osc_in_port);
        setOscOut(s.osc_out_port);
      })
      .catch(() => undefined);
    fetchMixxxDetect()
      .then((d) => {
        setInstallations(d.installations);
        const pref =
          d.installations.find((i) => i.engine === "mixxxxx" && i.exists) ||
          d.installations.find((i) => i.exists);
        if (pref) setExePath(pref.path);
      })
      .catch(() => undefined);
  }, [visible]);

  useEffect(() => {
    if (step === 2) refreshPorts();
  }, [step, refreshPorts]);

  const dismiss = () => {
    markOnboardingComplete();
    setVisible(false);
    onComplete?.();
  };

  const saveOscSettings = async () => {
    const r = await saveAppSettings({
      mixx_host: host,
      osc_in_port: oscIn,
      osc_out_port: oscOut,
    });
    return r;
  };

  const onNextFromOsc = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const r = await saveOscSettings();
      setMessage(r.message);
      setStep(3);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Failed to save settings");
    }
    setBusy(false);
  };

  const onLaunchAndProbe = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const launch = await launchMixxx({
        engine,
        path: exePath || undefined,
        osc_port_in: oscIn,
        osc_port_out: oscOut,
        osc_host_out: host,
      });
      setMessage(launch.message);
      if (launch.success && !launch.already_running) {
        await new Promise((r) => setTimeout(r, 4000));
      }
      const probe = await probeMixxxOsc();
      setOscOk(probe.osc_connected);
      setMessage(probe.message);
      if (probe.osc_connected) {
        markOnboardingComplete();
        setTimeout(() => {
          setVisible(false);
          onComplete?.();
        }, 1500);
      }
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Launch failed");
    }
    setBusy(false);
  };

  if (!visible) return null;

  const steps = ["Welcome", "Engine", "OSC ports", "Connect"];

  return (
    <div
      data-testid="onboarding-panel"
      className="rounded-xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/40 to-slate-900/80 p-5 space-y-4 relative"
    >
      <button
        type="button"
        onClick={dismiss}
        className="absolute top-3 right-3 text-slate-500 hover:text-slate-300"
        aria-label="Skip onboarding"
      >
        <X size={16} />
      </button>

      <div className="flex items-center gap-2">
        <Sparkles size={18} className="text-indigo-400" />
        <h3 className="text-sm font-semibold text-slate-100">First-time setup</h3>
        <span className="text-xs text-slate-500 ml-auto mr-8">
          Step {step + 1} / {steps.length}: {steps[step]}
        </span>
      </div>

      {step === 0 && (
        <div className="space-y-3 text-sm text-slate-300">
          <p>
            mixx-dj-mcp talks to Mixxx over OSC. Defaults: Mixxx listens on{" "}
            <strong className="text-slate-100">11119</strong>, sends feedback to MCP on{" "}
            <strong className="text-slate-100">11118</strong>.
          </p>
          <p className="text-xs text-slate-500">
            mixxxxx applies these via CLI on launch. Vanilla Mixxx uses Preferences →
            Controllers → OSC.
          </p>
        </div>
      )}

      {step === 1 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
              Engine
            </label>
            <select
              value={engine}
              onChange={(e) => {
                const eng = e.target.value as "mixxx" | "mixxxxx";
                setEngine(eng);
                const match = installations.find((i) => i.engine === eng && i.exists);
                if (match) setExePath(match.path);
              }}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm"
            >
              <option value="mixxxxx">mixxxxx (recommended)</option>
              <option value="mixxx">Mixxx vanilla</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
              Executable
            </label>
            <select
              value={exePath}
              onChange={(e) => setExePath(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-xs"
            >
              <option value="">— select —</option>
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
      )}

      {step === 2 && (
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-[10px] uppercase text-slate-500 block mb-1">
                Host (Mixxx out)
              </label>
              <input
                type="text"
                value={host}
                onChange={(e) => setHost(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase text-slate-500 block mb-1">
                OSC in (Mixxx listen)
              </label>
              <input
                type="number"
                value={oscIn}
                onChange={(e) => setOscIn(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase text-slate-500 block mb-1">
                OSC out (MCP listen)
              </label>
              <input
                type="number"
                value={oscOut}
                onChange={(e) => setOscOut(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono"
              />
            </div>
          </div>
          <button
            type="button"
            onClick={refreshPorts}
            className="text-xs text-indigo-400 hover:underline"
          >
            Re-check port availability
          </button>
          {portStatus && (
            <p
              className={`text-xs rounded-lg p-2 ${
                portStatus.ready
                  ? "text-green-400 bg-green-500/10"
                  : "text-amber-300 bg-amber-500/10"
              }`}
            >
              {portStatus.ready
                ? "Ports look free — good to go."
                : portStatus.clash_hint}
            </p>
          )}
          {engine === "mixxxxx" && (
            <p className="text-[10px] text-slate-500">
              mixxxxx will receive{" "}
              <code className="text-slate-400">--osc-port-in={oscIn}</code> and{" "}
              <code className="text-slate-400">--osc-port-out={oscOut}</code> on launch.
            </p>
          )}
        </div>
      )}

      {step === 3 && (
        <div className="space-y-2 text-sm text-slate-300">
          <p>
            Launch <strong>{engine}</strong>
            {exePath ? ` from ${exePath.split("\\").pop()}` : ""} and probe OSC.
          </p>
          {oscOk && (
            <p className="flex items-center gap-2 text-green-400 text-xs">
              <CheckCircle2 size={14} /> Connected — onboarding complete.
            </p>
          )}
        </div>
      )}

      {message && (
        <p className="text-xs text-slate-400 bg-slate-950/50 rounded p-2">{message}</p>
      )}

      <div className="flex justify-between pt-1">
        <button
          type="button"
          disabled={step === 0 || busy}
          onClick={() => setStep((s) => (s > 0 ? ((s - 1) as Step) : s))}
          className="flex items-center gap-1 text-xs text-slate-400 disabled:opacity-40"
        >
          <ChevronLeft size={14} /> Back
        </button>
        <div className="flex gap-2">
          {step < 2 && (
            <button
              type="button"
              onClick={() => setStep((s) => (s + 1) as Step)}
              disabled={step === 1 && !exePath}
              className="flex items-center gap-1 px-4 py-2 rounded-lg bg-indigo-500/20 text-indigo-300 text-sm disabled:opacity-50"
            >
              Next <ChevronRight size={14} />
            </button>
          )}
          {step === 2 && (
            <button
              type="button"
              onClick={onNextFromOsc}
              disabled={busy}
              className="flex items-center gap-1 px-4 py-2 rounded-lg bg-indigo-500/20 text-indigo-300 text-sm disabled:opacity-50"
            >
              {busy ? <Loader2 size={14} className="animate-spin" /> : null}
              Save & continue
            </button>
          )}
          {step === 3 && (
            <button
              type="button"
              onClick={onLaunchAndProbe}
              disabled={busy || !exePath}
              className="flex items-center gap-1 px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 text-sm disabled:opacity-50"
            >
              {busy ? <Loader2 size={14} className="animate-spin" /> : null}
              Launch & probe
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
