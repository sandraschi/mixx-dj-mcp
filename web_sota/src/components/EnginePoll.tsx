import { useEffect } from "react";
import { fetchEngineCapabilities, fetchHealth } from "../lib/api";
import { useStore } from "../lib/store";

/** Polls backend health + engine capabilities for global UI gating. */
export default function EnginePoll() {
  const setEngineCaps = useStore((s) => s.setEngineCaps);
  const setBackendStatus = useStore((s) => s.setBackendStatus);

  useEffect(() => {
    let cancelled = false;
    let delay = 2000;

    const tick = async () => {
      try {
        await fetchHealth();
        if (cancelled) return;
        setBackendStatus("connected");
        try {
          const caps = await fetchEngineCapabilities();
          if (!cancelled) setEngineCaps(caps);
        } catch {
          /* capabilities optional */
        }
        delay = 8000;
      } catch {
        if (!cancelled) setBackendStatus("error");
        delay = Math.min(delay * 2, 16000);
      }
      if (!cancelled) {
        window.setTimeout(tick, delay);
      }
    };

    tick();
    return () => {
      cancelled = true;
    };
  }, [setEngineCaps, setBackendStatus]);

  return null;
}
