import { useCallback } from "react";
import { Sparkles, Sliders } from "lucide-react";

export default function Effects() {
  const handleMixxEffects = useCallback((effect: string) => {
    // Use mixx_effects tool via API
    console.log("Call mixx_effects via MCP:", effect);
  }, []);

  return (
    <div className="space-y-6" data-testid="effects-page">
      <h2 className="text-xl font-semibold text-slate-100">Effects</h2>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-8 text-center">
        <Sparkles size={48} className="mx-auto text-slate-700 mb-4" />
        <h3 className="text-lg font-medium text-slate-300 mb-2">
          Effects via MCP Tools
        </h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
          Mixxx doesn't expose effect rack state over OSC. Use the
          <code className="mx-1 px-1.5 py-0.5 rounded bg-slate-800 text-amber-400 text-xs">
            mixx_effects
          </code>
          MCP tool to control effects from your AI assistant.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {[
            { label: "Chain 1: Reverb", cmd: 'mixx_effects("chain_load", rack=1, unit=1, effect="Reverb")' },
            { label: "Chain 2: Flanger", cmd: 'mixx_effects("chain_load", rack=1, unit=2, effect="Flanger")' },
            { label: "Clear Chain 1", cmd: 'mixx_effects("chain_clear", rack=1, unit=1)' },
          ].map((item) => (
            <button
              key={item.label}
              onClick={() => handleMixxEffects(item.cmd)}
              className="px-3 py-2 text-xs rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors border border-slate-700"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((rack) => (
          <div
            key={rack}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <Sliders size={14} className="text-amber-400" />
              <h3 className="text-sm font-medium text-slate-300">
                Effect Rack {rack}
              </h3>
            </div>
            {[1, 2, 3].map((unit) => (
              <div
                key={unit}
                className="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-800/30 mb-1.5 text-sm"
              >
                <span className="text-xs text-slate-500 w-16">Unit {unit}</span>
                <span className="text-slate-500 italic text-xs">
                  Use mixx_effects tool
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
