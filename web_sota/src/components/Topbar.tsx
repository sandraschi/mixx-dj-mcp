import { useLocation } from "react-router-dom";
import { useStore } from "../lib/store";

const routeTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/decks": "Decks",
  "/library": "Library",
  "/effects": "Effects",
  "/chat": "Chat",
  "/tools": "Tools",
  "/settings": "Settings",
};

export default function Topbar() {
  const location = useLocation();
  const backendStatus = useStore((s) => s.backendStatus);
  const daniMode = useStore((s) => s.daniMode);
  const title = routeTitles[location.pathname] || "Mixx-DJ-MCP";

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl shrink-0">
      <h1 className="text-lg font-semibold text-slate-100">{title}</h1>
      <div className="flex items-center gap-2">
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
        <span className="text-xs text-slate-500 capitalize">
          {backendStatus === "connected"
            ? "Connected"
            : backendStatus === "error"
              ? "Offline"
              : "Connecting..."}
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
