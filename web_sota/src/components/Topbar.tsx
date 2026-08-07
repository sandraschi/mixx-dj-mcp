import { useLocation } from "react-router-dom";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { useStore } from "../lib/store";
import { forkLabel } from "../lib/capabilities";

// EXPERIMENTAL light mode (invert hack). Not fleet standard — see index.css.
// Toggling `.dark` off the root flips the invert filter; persisted so the
// choice survives reloads. Delete this + the CSS block to revert.
const THEME_KEY = "mixx-light-mode";

function useExperimentalTheme() {
  const [light, setLight] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", !light);
    try {
      localStorage.setItem(THEME_KEY, light ? "1" : "0");
    } catch {
      // ignore storage errors
    }
  }, [light]);

  return { light, toggle: () => setLight((v) => !v) };
}

const routeTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/decks": "Decks",
  "/library": "Library",
  "/effects": "Effects",
  "/chat": "Chat",
  "/tools": "Tools",
  "/cockpit": "Cockpit",
  "/skins": "Skins",
  "/help": "Help",
  "/settings": "Settings",
};

export default function Topbar() {
  const location = useLocation();
  const backendStatus = useStore((s) => s.backendStatus);
  const engineCaps = useStore((s) => s.engineCaps);
  const daniMode = useStore((s) => s.daniMode);
  const title = routeTitles[location.pathname] || "Mixx-DJ-MCP";
  const { light, toggle } = useExperimentalTheme();

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl shrink-0">
      <h1 className="text-lg font-semibold text-slate-100">{title}</h1>
      <div className="flex items-center gap-3 flex-wrap justify-end">
        <button
          type="button"
          onClick={toggle}
          className="p-2 rounded-md text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          title={light ? "Switch to dark (experimental light mode)" : "Switch to light (experimental, ugly)"}
          aria-label="Toggle light mode (experimental)"
        >
          {light ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
        </button>
        <span
          className={`text-[10px] px-2 py-0.5 rounded font-medium ${
            engineCaps.is_mixxxxx
              ? "bg-purple-500/15 text-purple-300 border border-purple-500/25"
              : engineCaps.is_vanilla
                ? "bg-slate-800 text-slate-400 border border-slate-700"
                : "bg-slate-900 text-slate-500 border border-slate-800"
          }`}
          title={engineCaps.summary}
        >
          {forkLabel(engineCaps.fork)}
        </span>
        {engineCaps.process_running && (
          <span
            className={`text-[10px] ${
              engineCaps.osc_connected ? "text-green-400" : "text-amber-400"
            }`}
          >
            OSC {engineCaps.osc_connected ? "ok" : "off"}
          </span>
        )}
        <span
          data-testid="backend-dot"
          className={`w-2 h-2 rounded-full ${
            backendStatus === "connected"
              ? "bg-green-500"
              : backendStatus === "error"
                ? "bg-red-500"
                : "bg-gray-500 animate-pulse"
          }`}
        />
        <span className="text-xs text-slate-500">
          MCP{" "}
          {backendStatus === "connected"
            ? "online"
            : backendStatus === "error"
              ? "offline"
              : "…"}
        </span>
        {daniMode && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono">
            Dani Mode
          </span>
        )}
      </div>
    </header>
  );
}
