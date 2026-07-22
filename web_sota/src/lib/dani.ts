import { useStore } from "./store";

const DANI_MAP: Record<string, [string, string]> = {
  "Playlist": ["Playlist", "Crate"],
  "playlist": ["playlist", "crate"],
  "Playlists": ["Playlists", "Crates"],
  "playlists": ["playlists", "crates"],
};

export function useDaniLabel(label: string): string {
  const daniMode = useStore((s) => s.daniMode);
  if (!daniMode) return label;
  const pair = DANI_MAP[label];
  return pair ? pair[1] : label;
}

export function daniLabel(label: string, enabled: boolean): string {
  if (!enabled) return label;
  const pair = DANI_MAP[label];
  return pair ? pair[1] : label;
}
