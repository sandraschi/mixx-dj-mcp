import { useEffect, useRef, useCallback } from "react";
import { useStore } from "../lib/store";

let butterchurn: any = null;
let presets: any = null;

export default function Visualizer({ className = "" }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const visualizerRef = useRef<any>(null);
  const presetIndexRef = useRef(0);
  const presetKeysRef = useRef<string[]>([]);

  const decks = useStore((s) => s.decks);
  const backendStatus = useStore((s) => s.backendStatus);

  useEffect(() => {
    let animId: number;
    let running = true;

    (async () => {
      try {
        butterchurn = await import("butterchurn");
        presets = await import("butterchurn-presets");

        const canvas = canvasRef.current;
        if (!canvas) return;

        const viz = butterchurn.default.createVisualizer(canvas, {
          width: canvas.clientWidth || 640,
          height: canvas.clientHeight || 480,
          meshX: 64,
          meshY: 48,
          pixelRatio: window.devicePixelRatio || 1,
          textureRatio: 1,
          presetOutput: false,
        });

        const presetKeys = Object.keys(presets.default);
        presetKeysRef.current = presetKeys;

        const idx = Math.floor(Math.random() * presetKeys.length);
        presetIndexRef.current = idx;
        viz.loadPreset(presets.default[presetKeys[idx]], 0.0);
        viz.launchRenderer(true);

        visualizerRef.current = viz;

        const render = () => {
          if (!running) return;
          if (viz) {
            const freq = new Float32Array(512);
            const time = Date.now() / 1000;
            const deck = decks.find((d) => d.playing);
            const bpm = deck?.bpm || 128;
            const beatPhase = (time * (bpm / 60)) % 1.0;

            if (beatPhase < 0.05) {
              for (let i = 0; i < freq.length; i++) {
                freq[i] = Math.random() * 0.3 + 0.7;
              }
            } else {
              const decay = Math.max(0, 1 - beatPhase * 3);
              for (let i = 0; i < freq.length; i++) {
                freq[i] = Math.random() * 0.1 + decay * 0.2;
              }
            }

            viz.render({
              waveformData: freq,
              frequencyData: freq,
              framebuffer: null,
              source: "butterchurn",
              screenPreset: false,
            });
          }
          animId = requestAnimationFrame(render);
        };
        render();
      } catch (e) {
        console.warn("Butterchurn init failed:", e);
      }
    })();

    return () => {
      running = false;
      cancelAnimationFrame(animId);
      if (visualizerRef.current) {
        try { visualizerRef.current.destroyRenderer(); } catch {}
      }
    };
  }, [decks]);

  const cyclePreset = useCallback(() => {
    const viz = visualizerRef.current;
    const keys = presetKeysRef.current;
    if (!viz || !keys.length) return;
    presetIndexRef.current = (presetIndexRef.current + 1) % keys.length;
    viz.loadPreset(presets.default[keys[presetIndexRef.current]], 2.0);
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "ArrowUp") cyclePreset();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [cyclePreset]);

  if (backendStatus !== "connected") {
    return (
      <div className={`flex items-center justify-center bg-black text-zinc-500 ${className}`}>
        <p>Connect backend to enable MilkDrop visuals</p>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden rounded-lg bg-black ${className}`}>
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-pointer"
        onClick={cyclePreset}
      />
      <div className="absolute bottom-2 left-2 text-[10px] text-white/30 font-mono">
        Click to change visual · Arrow keys to browse
      </div>
    </div>
  );
}
