import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, Rocket } from "lucide-react";
import { fetchMixxxSetup, type FirstRunStatus } from "../lib/api";

export default function FirstRunPanel() {
  const [status, setStatus] = useState<FirstRunStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const st = await fetchMixxxSetup();
      setStatus(st);
    } catch {
      setStatus(null);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
  }, [refresh]);

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 flex items-center gap-2 text-sm text-slate-500">
        <Loader2 size={16} className="animate-spin" /> Checking setup…
      </div>
    );
  }

  if (!status || status.ready) {
    return null;
  }

  return (
    <div
      data-testid="first-run-panel"
      className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 space-y-3"
    >
      <div className="flex items-center gap-2">
        <Rocket size={18} className="text-amber-400" />
        <h3 className="text-sm font-semibold text-amber-100">Get ready to DJ</h3>
      </div>
      <p className="text-xs text-amber-200/80">{status.user_message}</p>
      <ul className="space-y-2">
        {status.steps.map((step) => (
          <li key={step.id} className="flex items-start gap-2 text-xs text-slate-300">
            {step.done ? (
              <CheckCircle2 size={14} className="text-green-400 shrink-0 mt-0.5" />
            ) : (
              <Circle size={14} className="text-slate-600 shrink-0 mt-0.5" />
            )}
            <span>
              {step.label}
              {!step.done && step.hint && (
                <span className="block text-slate-500 mt-0.5">{step.hint}</span>
              )}
            </span>
          </li>
        ))}
      </ul>
      {status.preferred_path && (
        <p className="text-[10px] font-mono text-slate-500 truncate">
          Detected: {status.preferred_path}
        </p>
      )}
    </div>
  );
}
