import { create } from "zustand";

export interface Deck {
  id: number;
  playing: boolean;
  bpm: number;
  key: string;
  track_title: string;
  track_artist: string;
  volume: number;
  gain: number;
  sync_enabled: boolean;
  loop_enabled: boolean;
}

export interface LibraryItem {
  id: string;
  title: string;
  artist: string;
  bpm: number;
  key: string;
  length: string;
}

interface AppState {
  backendStatus: "connecting" | "connected" | "error";
  decks: Deck[];
  crossfader: number;
  libraryResults: LibraryItem[];
  sidebarCollapsed: boolean;
  daniMode: boolean;
  setBackendStatus: (status: "connecting" | "connected" | "error") => void;
  setDeck: (id: number, data: Partial<Deck>) => void;
  setDecks: (decks: Deck[]) => void;
  setCrossfader: (pos: number) => void;
  setLibraryResults: (results: LibraryItem[]) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setDaniMode: (enabled: boolean) => void;
}

const defaultDecks: Deck[] = [1, 2, 3, 4].map((id) => ({
  id,
  playing: false,
  bpm: 128,
  key: "C maj",
  track_title: "No Track Loaded",
  track_artist: "",
  volume: 0.8,
  gain: 1.0,
  sync_enabled: false,
  loop_enabled: false,
}));

export const useStore = create<AppState>((set) => ({
  backendStatus: "connecting",
  decks: defaultDecks,
  crossfader: 0,
  libraryResults: [],
  sidebarCollapsed: false,
  setBackendStatus: (status) => set({ backendStatus: status }),
  setDeck: (id, data) =>
    set((state) => ({
      decks: state.decks.map((d) => (d.id === id ? { ...d, ...data } : d)),
    })),
  setDecks: (decks) => set({ decks }),
  setCrossfader: (pos) => set({ crossfader: Math.max(-1, Math.min(1, pos)) }),
  setLibraryResults: (results) => set({ libraryResults: results }),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  daniMode: localStorage.getItem("mixx-dani-mode") === "true",
  setDaniMode: (enabled) => {
    localStorage.setItem("mixx-dani-mode", String(enabled));
    set({ daniMode: enabled });
  },
}));
