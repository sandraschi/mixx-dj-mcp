import { useEffect, useState } from "react";
import {
  Server,
  Wifi,
  Moon,
  Info,
  Package2,
} from "lucide-react";
import { API_BASE, fetchHealth } from "../lib/api";
import { useStore } from "../lib/store";

export default function Settings() {
  const daniMode = useStore((s) => s.daniMode);
  const setDaniMode = useStore((s) => s.setDaniMode);
  const [oscPort, setOscPort] = useState("5133");
  const [host, setHost] = useState("127.0.0.1");
  const [backendInfo, setBackendInfo] = useState<{
    version: string;
    server: string;
    uptime_seconds: number;
  } | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const h = await fetchHealth();
        setBackendInfo(h);
      } catch {}
    })();
  }, []);

  return (
    <div data-testid="settings-page" className="space-y-6 max-w-2xl">
      <h2 className="text-xl font-semibold text-slate-100">Settings</h2>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
          <Server size={16} className="text-amber-400" />
          <span className="text-sm font-medium text-slate-200">
            Mixxx OSC Connection
          </span>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="text-xs text-slate-500 block mb-1">
              OSC Host
            </label>
            <input
              type="text"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500/50"
            />
          </div>
          <div>
            <label className="text-xs text-slate-500 block mb-1">
              OSC Port
            </label>
            <input
              type="number"
              value={oscPort}
              onChange={(e) => setOscPort(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500/50"
            />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
          <Wifi size={16} className="text-amber-400" />
          <span className="text-sm font-medium text-slate-200">
            Backend Connection
          </span>
        </div>
        <div className="p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">API URL</span>
            <span className="text-slate-300 font-mono text-xs">{API_BASE}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Status</span>
            <span
              className={`text-xs font-medium ${
                backendInfo ? "text-green-400" : "text-red-400"
              }`}
            >
              {backendInfo ? "Connected" : "Offline"}
            </span>
          </div>
          {backendInfo && (
            <>
              <div className="flex justify-between">
                <span className="text-slate-500">Server</span>
                <span className="text-slate-300 text-xs">
                  {backendInfo.server} v{backendInfo.version}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Uptime</span>
                <span className="text-slate-300 text-xs">
                  {Math.floor(backendInfo.uptime_seconds / 60)}m{" "}
                  {backendInfo.uptime_seconds % 60}s
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
          <Moon size={16} className="text-amber-400" />
          <span className="text-sm font-medium text-slate-200">Theme</span>
        </div>
        <div className="p-4">
          <p className="text-xs text-slate-500">
            Dark mode is permanently enabled. Mixx-DJ-MCP uses a Slate-950 dark
            theme for optimal visibility in low-light DJ environments.
          </p>
        </div>
      </div>

      <div className="border border-zinc-700 rounded-lg p-4 bg-zinc-900/50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-zinc-100 flex items-center gap-2">
              <Package2 className="h-4 w-4 text-amber-500" />
              Dani Mode
            </h3>
            <p className="text-xs text-zinc-400 mt-1">
              Rename "Playlists" to "Crates" throughout the UI
              (because that's what they are, Dan is right)
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={daniMode}
              onChange={(e) => setDaniMode(e.target.checked)}
            />
            <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-600" />
          </label>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
          <Info size={16} className="text-amber-400" />
          <span className="text-sm font-medium text-slate-200">About</span>
        </div>
        <div className="p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">Version</span>
            <span className="text-slate-300">0.1.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Webapp Port</span>
            <span className="text-slate-300 font-mono text-xs">11117</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Backend Port</span>
            <span className="text-slate-300 font-mono text-xs">11116</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">MCP Transport</span>
            <span className="text-slate-300 font-mono text-xs">/mcp</span>
          </div>
        </div>
      </div>
    </div>
  );
}
