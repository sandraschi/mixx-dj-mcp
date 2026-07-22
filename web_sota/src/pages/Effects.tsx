import { Sparkles, Sliders } from "lucide-react";

const effectSlots = [1, 2, 3];

const effectChains = [
  {
    id: 1,
    name: "Chain 1",
    effects: [
      { name: "Reverb", params: { wet: 0.3, decay: 0.5 } },
      { name: "Flanger", params: { rate: 0.2, depth: 0.4 } },
      null,
    ],
  },
  {
    id: 2,
    name: "Chain 2",
    effects: [
      { name: "Delay", params: { wet: 0.25, feedback: 0.3 } },
      null,
      null,
    ],
  },
  {
    id: 3,
    name: "Chain 3",
    effects: [null, null, null],
  },
  {
    id: 4,
    name: "Chain 4",
    effects: [
      { name: "Filter", params: { cutoff: 0.7, resonance: 0.2 } },
      null,
      { name: "Bitcrusher", params: { bits: 8, rate: 0.5 } },
    ],
  },
];

export default function Effects() {
  return (
    <div data-testid="effects-page" className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-100">Effects</h2>

      <div className="grid grid-cols-2 gap-4">
        {effectChains.map((chain) => (
          <div
            key={chain.id}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-amber-400" />
                <span className="text-sm font-medium text-slate-200">
                  {chain.name}
                </span>
              </div>
              <span className="text-[10px] text-slate-600 uppercase">
                {chain.effects.filter(Boolean).length}/3 active
              </span>
            </div>

            <div className="space-y-2">
              {effectSlots.map((slotIdx) => {
                const fx = chain.effects[slotIdx - 1];
                return (
                  <div
                    key={slotIdx}
                    className={`rounded-lg p-3 ${
                      fx
                        ? "bg-slate-800/50 border border-slate-700/50"
                        : "bg-slate-800/20 border border-dashed border-slate-700/30"
                    }`}
                  >
                    {fx ? (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-slate-300">
                            {fx.name}
                          </span>
                          <button className="text-[10px] text-red-400/60 hover:text-red-400 transition-colors">
                            Remove
                          </button>
                        </div>
                        {Object.entries(fx.params).map(([param, value]) => (
                          <div key={param}>
                            <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                              <span>{param}</span>
                              <span>{value}</span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-amber-500/60 rounded-full"
                                style={{
                                  width: `${(value as number) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center gap-1.5">
                        <Sliders size={12} className="text-slate-600" />
                        <span className="text-xs text-slate-600">
                          Empty slot
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
