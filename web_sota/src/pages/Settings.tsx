import { useEffect, useState } from "react";
import {
  Server,
  Wifi,
  Moon,
  Info,
  Package2,
  Cpu,
} from "lucide-react";
import { API_BASE, fetchHealth, fetchLLMDiscover, fetchAppSettings, saveAppSettings, type LLMProvider } from "../lib/api";
import { useStore } from "../lib/store";

const LLM_PROVIDER_KEY = "mixx-llm-provider";
const LLM_MODEL_KEY = "mixx-llm-model";

export default function Settings() {
  const daniMode = useStore((s) => s.daniMode);
  const setDaniMode = useStore((s) => s.setDaniMode);
  const [oscPort, setOscPort] = useState("11119");
  const [oscOutPort, setOscOutPort] = useState("11118");
  const [host, setHost] = useState("127.0.0.1");
  const [settingsSaved, setSettingsSaved] = useState<string | null>(null);
  const [savingOsc, setSavingOsc] = useState(false);
  const [backendInfo, setBackendInfo] = useState<{
    version: string;
    server: string;
    uptime_seconds: number;
  } | null>(null);

  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [providerStatus, setProviderStatus] = useState<Record<string, "probing" | "detected" | "not_found">>({});
  const [selectedProvider, setSelectedProvider] = useState(() => localStorage.getItem(LLM_PROVIDER_KEY) || "");
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem(LLM_MODEL_KEY) || "");
  const [availableModels, setAvailableModels] = useState<string[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const h = await fetchHealth();
        setBackendInfo(h);
      } catch {}
      try {
        const s = await fetchAppSettings();
        setHost(s.mixx_host);
        setOscPort(String(s.osc_in_port));
        setOscOutPort(String(s.osc_out_port));
      } catch {}
    })();
  }, []);

  const saveOscSettings = async () => {
    setSavingOsc(true);
    setSettingsSaved(null);
    try {
      const r = await saveAppSettings({
        mixx_host: host,
        osc_in_port: parseInt(oscPort, 10),
        osc_out_port: parseInt(oscOutPort, 10),
      });
      setSettingsSaved(r.message);
    } catch (e) {
      setSettingsSaved(e instanceof Error ? e.message : "Save failed");
    }
    setSavingOsc(false);
  };

  useEffect(() => {
    (async () => {
      setProviderStatus({ ollama: "probing", lmstudio: "probing", vllm: "probing" });
      try {
        const data = await fetchLLMDiscover();
        setProviders(data.providers);
        const statuses: Record<string, "detected" | "not_found"> = {};
        for (const p of data.providers) {
          statuses[p.name] = p.status;
        }
        setProviderStatus(statuses);

        const detected = data.providers.filter((p) => p.status === "detected");
        if (detected.length > 0) {
          const saved = localStorage.getItem(LLM_PROVIDER_KEY);
          const match = detected.find((p) => p.name === saved);
          const active = match || detected[0];
          if (!match) {
            localStorage.setItem(LLM_PROVIDER_KEY, active.name);
          }
          setSelectedProvider(active.name);
          setAvailableModels(active.models);
          const savedModel = localStorage.getItem(LLM_MODEL_KEY);
          if (savedModel && active.models.includes(savedModel)) {
            setSelectedModel(savedModel);
          } else if (active.models.length > 0) {
            setSelectedModel(active.models[0]);
            localStorage.setItem(LLM_MODEL_KEY, active.models[0]);
          }
        }
      } catch {
        setProviderStatus({ ollama: "not_found", lmstudio: "not_found", vllm: "not_found" });
      }
    })();
  }, []);

  const handleProviderChange = (name: string) => {
    setSelectedProvider(name);
    localStorage.setItem(LLM_PROVIDER_KEY, name);
    const p = providers.find((x) => x.name === name);
    if (p) {
      setAvailableModels(p.models);
      if (p.models.length > 0) {
        setSelectedModel(p.models[0]);
        localStorage.setItem(LLM_MODEL_KEY, p.models[0]);
      } else {
        setSelectedModel("");
      }
    }
  };

  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    localStorage.setItem(LLM_MODEL_KEY, model);
  };

  const detectedCount = Object.values(providerStatus).filter((s) => s === "detected").length;
  const hasAnyProvider = detectedCount > 0;

  return (
    <div data-testid="settings-page" className="space-y-6 max-w-2xl">
      <h2 className="text-xl font-semibold text-slate-100">Settings</h2>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
          <Cpu size={16} className="text-amber-400" />
          <span className="text-sm font-medium text-slate-200">
            Local LLM
          </span>
        </div>
        <div className="p-4 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500 block uppercase tracking-wider">
              Provider Detection
            </label>
            <div className="grid grid-cols-3 gap-3">
              {["ollama", "lmstudio", "vllm"].map((name) => {
                const status = providerStatus[name] || "probing";
                const p = providers.find((x) => x.name === name);
                return (
                  <div
                    key={name}
                    data-testid={`llm-provider-${name}`}
                    className={`rounded-lg border p-3 ${
                      status === "detected"
                        ? "border-emerald-700 bg-emerald-900/20"
                        : status === "probing"
                          ? "border-slate-700 bg-slate-800/30"
                          : "border-slate-800 bg-slate-900/50"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          status === "detected"
                            ? "bg-green-500"
                            : status === "probing"
                              ? "bg-yellow-500 animate-pulse"
                              : "bg-slate-600"
                        }`}
                      />
                      <span className="text-sm font-medium text-slate-200 capitalize">{name}</span>
                      <span className="text-[10px] text-slate-500 ml-auto">:{p?.port ?? (name === "ollama" ? 11434 : name === "lmstudio" ? 1234 : 8000)}</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      {status === "detected" ? "Detected" : status === "probing" ? "Probing..." : "Not found"}
                    </p>
                    {status === "detected" && p && (
                      <p className="text-[10px] text-slate-500 mt-1">{p.models.length} model{p.models.length !== 1 ? "s" : ""}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {!hasAnyProvider && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <span className="text-amber-400 text-sm mt-0.5">!</span>
              <p className="text-xs text-amber-300">
                Install <strong>Ollama</strong> or <strong>LM Studio</strong> to enable AI features (chat, AI transitions, smart crates).
              </p>
            </div>
          )}

          {hasAnyProvider && (
            <>
              <div>
                <label className="text-xs text-slate-500 block mb-1">
                  Provider
                </label>
                <select
                  data-testid="llm-provider-select"
                  value={selectedProvider}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  className="w-full bg-zinc-800 text-zinc-100 border border-zinc-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-500/50"
                >
                  {providers
                    .filter((p) => p.status === "detected")
                    .map((p) => (
                      <option key={p.name} value={p.name}>
                        {p.name.charAt(0).toUpperCase() + p.name.slice(1)} (:{p.port})
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-500 block mb-1">
                  Model
                </label>
                {availableModels.length > 0 ? (
                  <select
                    data-testid="llm-model-select"
                    value={selectedModel}
                    onChange={(e) => handleModelChange(e.target.value)}
                    className="w-full bg-zinc-800 text-zinc-100 border border-zinc-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-500/50"
                  >
                    {availableModels.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="text"
                    data-testid="llm-model-input"
                    value={selectedModel}
                    onChange={(e) => handleModelChange(e.target.value)}
                    placeholder="e.g. llama3.2:3b"
                    className="w-full bg-zinc-800 text-zinc-100 border border-zinc-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-500/50"
                  />
                )}
              </div>
            </>
          )}
        </div>
      </div>

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
              OSC Host (Mixxx receives commands here)
            </label>
            <input
              type="text"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500/50"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500 block mb-1">
                OSC In (→ Mixxx)
              </label>
              <input
                type="number"
                value={oscPort}
                onChange={(e) => setOscPort(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500/50"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 block mb-1">
                OSC Out (← Mixxx)
              </label>
              <input
                type="number"
                value={oscOutPort}
                onChange={(e) => setOscOutPort(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500/50"
              />
            </div>
          </div>
          <button
            type="button"
            onClick={saveOscSettings}
            disabled={savingOsc}
            className="px-4 py-2 rounded-lg bg-amber-500/10 text-amber-400 text-sm hover:bg-amber-500/20 disabled:opacity-50"
          >
            {savingOsc ? "Saving…" : "Save OSC settings"}
          </button>
          {settingsSaved && (
            <p className="text-xs text-slate-400">{settingsSaved}</p>
          )}
          <p className="text-[10px] text-slate-600">
            Match Mixxx Preferences → MIDI/OSC. Changing the listen (out) port requires restarting the mixx-dj-mcp backend.
          </p>
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
