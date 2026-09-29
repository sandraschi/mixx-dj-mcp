export type ForkId = "mixxxxx" | "mixxx" | "unknown";

export type FeatureId =
  | "osc_deck_control"
  | "deck_load"
  | "effects_racks"
  | "hotcues"
  | "crossfader"
  | "library_load"
  | "video_deck"
  | "video_fullscreen"
  | "ndi_output"
  | "video_skins"
  | "stem_separation"
  | "stem_swap_transitions"
  | "engine_export"
  | "phase_indicator"
  | "help_video"
  | "help_ndi"
  | "help_av_rig";

export interface FeatureCapability {
  available: boolean;
  enabled: boolean;
  reason: string | null;
}

export interface EngineCapabilities {
  fork: ForkId;
  process_running: boolean;
  osc_connected: boolean;
  is_mixxxxx: boolean;
  is_vanilla: boolean;
  summary: string;
  features: Record<string, FeatureCapability>;
}

export const DEFAULT_CAPABILITIES: EngineCapabilities = {
  fork: "unknown",
  process_running: false,
  osc_connected: false,
  is_mixxxxx: false,
  is_vanilla: false,
  summary: "Launch Mixxx or mixxxxx and connect OSC",
  features: {},
};

export function featureEnabled(
  caps: EngineCapabilities | null,
  id: FeatureId
): boolean {
  return Boolean(caps?.features[id]?.enabled);
}

export function featureReason(
  caps: EngineCapabilities | null,
  id: FeatureId
): string | null {
  return caps?.features[id]?.reason ?? null;
}

export function forkLabel(fork: ForkId): string {
  if (fork === "mixxxxx") return "mixxxxx";
  if (fork === "mixxx") return "Mixxx (vanilla)";
  return "Not detected";
}

export const HELP_TAB_FEATURES: Record<string, FeatureId> = {
  rig: "help_av_rig",
  ndi: "help_ndi",
  resolume: "help_av_rig",
  video: "help_video",
};
