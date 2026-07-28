import type { ReactNode } from "react";
import { Lock } from "lucide-react";
import type { EngineCapabilities, FeatureId } from "../lib/capabilities";
import { featureEnabled, featureReason } from "../lib/capabilities";

interface FeatureGateProps {
  caps: EngineCapabilities | null;
  feature: FeatureId;
  children: ReactNode;
  mode?: "hide" | "disable";
  className?: string;
}

export default function FeatureGate({
  caps,
  feature,
  children,
  mode = "disable",
  className = "",
}: FeatureGateProps) {
  const enabled = featureEnabled(caps, feature);

  if (enabled) {
    return <div className={className}>{children}</div>;
  }

  if (mode === "hide") {
    return null;
  }

  const reason = featureReason(caps, feature);

  return (
    <div className={`relative ${className}`} data-feature-gate={feature}>
      <div className="pointer-events-none opacity-40 select-none">{children}</div>
      {reason && (
        <div className="mt-2 flex items-start gap-2 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-xs text-slate-400">
          <Lock size={12} className="shrink-0 mt-0.5 text-amber-500/80" />
          <span>{reason}</span>
        </div>
      )}
    </div>
  );
}

export function FeatureNotice({
  caps,
  feature,
  className = "",
}: {
  caps: EngineCapabilities | null;
  feature: FeatureId;
  className?: string;
}) {
  if (featureEnabled(caps, feature)) return null;
  const reason = featureReason(caps, feature);
  if (!reason) return null;
  return (
    <div
      className={`flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-200/90 ${className}`}
    >
      <Lock size={12} className="shrink-0" />
      <span>{reason}</span>
    </div>
  );
}
