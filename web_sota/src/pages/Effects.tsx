import { useCallback, useState } from "react";
import { Sparkles, Sliders, Loader2, Check, AlertCircle } from "lucide-react";
import { callEffects } from "../lib/api";
import { useStore } from "../lib/store";
import FeatureGate, { FeatureNotice } from "../components/FeatureGate";
import { featureEnabled } from "../lib/capabilities";

const QUICK_ACTIONS = [
  {
    label: "Chain 1: Reverb",
    payload: { operation: "chain_load", rack: 1, unit: 1, effect: "Reverb" },
  },
  {
    label: "Chain 2: Flanger",
    payload: { operation: "chain_load", rack: 1, unit: 2, effect: "Flanger" },
  },
  {
    label: "Clear Chain 1",
    payload: { operation: "chain_clear", rack: 1, unit: 1 },
  },
  {
    label: "Enable Rack 1 Unit 1",
    payload: { operation: "effect_enable", rack: 1, unit: 1, enable: true },
  },
] as const;

const EFFECT_PRESETS = [
  "Reverb",
  "Echo",
  "Flanger",
  "Filter",
  "Distortion",
  "Phaser",
] as const;

export default function Effects() {
  const engineCaps = useStore((s) => s.engineCaps);
  const oscOk = featureEnabled(engineCaps, "effects_racks");
  const [rack, setRack] = useState(1);
  const [unit, setUnit] = useState(1);
  const [effectName, setEffectName] = useState("Reverb");
  const [meta, setMeta] = useState(0.5);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<{ ok: boolean; text: string } | null>(null);

  const runEffect = useCallback(async (payload: Record<string, unknown>) => {
    setBusy(true);
    setStatus(null);
    try {
      const result = await callEffects(payload);
      if (result.success === false) {
        setStatus({ ok: false, text: result.message || "Effect command failed" });
      } else {
        setStatus({
          ok: true,
          text: result.message || "Effect command sent via OSC",
        });
      }
    } catch (err) {
      setStatus({
        ok: false,
        text: err instanceof Error ? err.message : "Backend request failed",
      });
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <div className="space-y-6" data-testid="effects-page">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-semibold text-slate-100">Effects</h2>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>Rack</span>
          {[1, 2, 3, 4].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setRack(n)}
              className={`w-7 h-7 rounded text-xs font-mono transition-colors ${
                rack === n
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  : "bg-slate-800 text-slate-400 border border-slate-700"
              }`}
            >
              {n}
            </button>
          ))}
          <span className="ml-2">Unit</span>
          {[1, 2, 3, 4].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setUnit(n)}
              className={`w-7 h-7 rounded text-xs font-mono transition-colors ${
                unit === n
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  : "bg-slate-800 text-slate-400 border border-slate-700"
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      <FeatureNotice caps={engineCaps} feature="effects_racks" />

      <FeatureGate caps={engineCaps} feature="effects_racks">
      {status && (
        <div
          className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
            status.ok
              ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
              : "border-red-500/30 bg-red-500/10 text-red-300"
          }`}
        >
          {status.ok ? <Check size={14} /> : <AlertCircle size={14} />}
          <span>{status.text}</span>
        </div>
      )}

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={18} className="text-amber-400" />
          <h3 className="text-base font-medium text-slate-200">Quick actions</h3>
        </div>
        <p className="text-sm text-slate-400 mb-4">
          Sends OSC to Mixxx effect racks via <code className="text-amber-400">/api/v1/effects</code>.
          Mixxx must be running with OSC enabled.
        </p>
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map((item) => (
            <button
              key={item.label}
              type="button"
              disabled={busy || !oscOk}
              onClick={() => runEffect(item.payload)}
              className="px-3 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:text-slate-100 hover:bg-slate-700 transition-colors border border-slate-700 disabled:opacity-50"
            >
              {busy ? <Loader2 size={14} className="animate-spin inline" /> : item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Sliders size={16} className="text-amber-400" />
          <h3 className="text-base font-medium text-slate-200">
            Rack {rack} · Unit {unit}
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="block text-sm text-slate-400">
            Effect chain
            <select
              value={effectName}
              onChange={(e) => setEffectName(e.target.value)}
              className="mt-1 w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-slate-200"
            >
              {EFFECT_PRESETS.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm text-slate-400">
            Meta knob ({meta.toFixed(2)})
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={meta}
              onChange={(e) => setMeta(Number(e.target.value))}
              className="mt-2 w-full"
            />
          </label>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy || !oscOk}
            onClick={() =>
              runEffect({
                operation: "chain_load",
                rack,
                unit,
                effect: effectName,
              })
            }
            className="px-4 py-2 text-sm rounded-lg bg-amber-500/15 text-amber-300 border border-amber-500/30 hover:bg-amber-500/25 disabled:opacity-50"
          >
            Load effect
          </button>
          <button
            type="button"
            disabled={busy || !oscOk}
            onClick={() => runEffect({ operation: "chain_clear", rack, unit })}
            className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 disabled:opacity-50"
          >
            Clear chain
          </button>
          <button
            type="button"
            disabled={busy || !oscOk}
            onClick={() =>
              runEffect({ operation: "meta_set", rack, unit, value: meta })
            }
            className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 disabled:opacity-50"
          >
            Set meta
          </button>
          <button
            type="button"
            disabled={busy || !oscOk}
            onClick={() =>
              runEffect({ operation: "effect_enable", rack, unit, enable: true })
            }
            className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 disabled:opacity-50"
          >
            Enable unit
          </button>
          <button
            type="button"
            disabled={busy || !oscOk}
            onClick={() =>
              runEffect({ operation: "effect_enable", rack, unit, enable: false })
            }
            className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 disabled:opacity-50"
          >
            Disable unit
          </button>
        </div>
      </div>
      </FeatureGate>
    </div>
  );
}
