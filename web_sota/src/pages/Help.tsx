import { useState } from "react";
import { motion } from "framer-motion";
import {
  BookOpen,
  Radio,
  Palette,
  Video,
  Plug,
  Network,
  Sparkles,
  Lock,
} from "lucide-react";
import { useStore } from "../lib/store";
import { HELP_TAB_FEATURES, featureEnabled } from "../lib/capabilities";
import { FeatureNotice } from "../components/FeatureGate";

type TabId = "overview" | "rig" | "ndi" | "resolume" | "video" | "skins" | "osc";

const tabs: { id: TabId; label: string; icon: typeof BookOpen }[] = [
  { id: "overview", label: "Overview", icon: BookOpen },
  { id: "rig", label: "AV Rig", icon: Network },
  { id: "ndi", label: "NDI", icon: Radio },
  { id: "resolume", label: "Resolume", icon: Sparkles },
  { id: "video", label: "Video", icon: Video },
  { id: "skins", label: "Skins", icon: Palette },
  { id: "osc", label: "OSC / MCP", icon: Plug },
];

const linkClass =
  "text-amber-400/90 hover:text-amber-300 underline underline-offset-2";

export default function Help() {
  const [tab, setTab] = useState<TabId>("overview");
  const engineCaps = useStore((s) => s.engineCaps);

  const tabEnabled = (id: TabId) => {
    const feat = HELP_TAB_FEATURES[id];
    if (!feat) return true;
    return featureEnabled(engineCaps, feat);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Help</h1>
        <p className="text-slate-400 text-sm mt-1">
          {engineCaps.is_vanilla
            ? "Vanilla Mixxx — audio/OSC docs below. Video, NDI, and AV rig tabs require mixxxxx."
            : "mixxxxx as the AV hub — NDI, Resolume, OBS, and this control tower. Not a substitute for the Mixxx manual."}
        </p>
      </div>

      {engineCaps.is_vanilla && (
        <FeatureNotice caps={engineCaps} feature="help_video" />
      )}

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {tabs.map(({ id, label, icon: Icon }) => {
          const enabled = tabEnabled(id);
          return (
          <button
            key={id}
            type="button"
            onClick={() => enabled && setTab(id)}
            disabled={!enabled}
            title={!enabled ? "Requires mixxxxx (video fork)" : undefined}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === id
                ? "bg-amber-500/15 text-amber-400"
                : enabled
                  ? "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  : "text-slate-600 cursor-not-allowed opacity-50"
            }`}
          >
            <Icon size={16} />
            {label}
            {!enabled && <Lock size={12} className="opacity-60" />}
          </button>
        );
        })}
      </div>

      <motion.div
        key={tab}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="prose prose-invert prose-sm max-w-none text-slate-300"
      >
        {tab === "overview" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">
              mixxxxx — superapp orchestrator (AV hub)
            </h2>
            <p className="text-slate-400">
              You DJ in <strong className="text-slate-200">mixxxxx</strong> (audio + deck video +
              crossfader). When you need streaming or club visuals, you do not cram everything into
              one window — you <strong className="text-slate-200">hand off</strong> video over the
              network (NDI®) and control the rig from here (OSC / MCP).
            </p>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>
                <strong className="text-slate-200">mixxxxx</strong> — engine room: mix, blend video,
                optional NDI sender, export, OSC server (UDP 11118/11119).
              </li>
              <li>
                <strong className="text-slate-200">mixx-dj-mcp</strong> — this webapp + MCP; library,
                SFX, deck control, Resolume BPM bridge.
              </li>
              <li>
                <strong className="text-slate-200">resolume-mcp</strong> — separate MCP for Resolume
                layers/clips/effects (needs Resolume installed).
              </li>
            </ul>
            <p className="text-slate-400">
              New to NDI? Start with the <button type="button" onClick={() => setTab("ndi")} className={linkClass}>NDI tab</button> — written for people who only heard of it yesterday.
            </p>
            <p className="text-slate-500 text-xs">
              Repo: mixxxxx <code>docs/ORCHESTRATOR.md</code>, <code>docs/NDI.md</code> · mixx-dj-mcp{" "}
              <code>docs/ORCHESTRATOR.md</code>
            </p>
          </section>
        )}

        {tab === "rig" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">Typical AV rig</h2>
            <pre className="text-xs text-slate-400 bg-slate-900/80 border border-slate-800 rounded-lg p-4 overflow-x-auto leading-relaxed">
{`mixx-dj-mcp (MCP + webapp)
        │ OSC 11119 → 11118
        ▼
   mixxxxx ──NDI® (LAN)──► Resolume (layers / FX / projection)
        │                        │
        │                        └──► OBS ──► stream (Kick, YouTube, …)
        └── 2nd monitor HDMI (optional, no NDI)`}
            </pre>
            <h3 className="text-base font-medium text-slate-200">Two pipes</h3>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>
                <strong className="text-slate-200">OSC</strong> — small control messages (volume,
                BPM sync, enable video). This is what mixx-dj-mcp speaks.
              </li>
              <li>
                <strong className="text-slate-200">NDI®</strong> — full video (~30 fps). Install the{" "}
                <a href="https://ndi.link/NDIRedistV5" className={linkClass} target="_blank" rel="noreferrer">
                  free NDI runtime
                </a>
                ; mixxxxx does not bundle it.
              </li>
            </ul>
            <h3 className="text-base font-medium text-slate-200">Pick your consumer</h3>
            <table className="w-full text-sm border border-slate-800 rounded-lg overflow-hidden">
              <thead className="bg-slate-900">
                <tr>
                  <th className="text-left p-2 text-slate-400">Tool</th>
                  <th className="text-left p-2 text-slate-400">Best for</th>
                </tr>
              </thead>
              <tbody className="text-slate-400">
                <tr className="border-t border-slate-800">
                  <td className="p-2">NDI Studio Monitor</td>
                  <td className="p-2">Free sanity check — “do I see Mixxxxx?”</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2">OBS + NDI plugin</td>
                  <td className="p-2">Streaming, overlays, recording</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2">Resolume Avenue / Arena</td>
                  <td className="p-2">Club VJ: layers, effects, outputs to projectors</td>
                </tr>
              </tbody>
            </table>
            <p className="text-slate-500 text-sm">
              mixxxxx owns the <em>mix</em>; Resolume/OBS own <em>presentation</em>. That split is
              intentional — it is what makes the stack scale for mobile DJs and Sunday streams alike.
            </p>
          </section>
        )}

        {tab === "ndi" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">NDI® — network video (for beginners)</h2>
            <p className="text-amber-400/90 text-sm font-medium">
              Partial MVP in mixxxxx — enable and verify with NDI Studio Monitor before a gig.
            </p>
            <p>
              <strong className="text-slate-200">NDI</strong> (Network Device Interface) is{" "}
              <em>not</em> a video file format. It is live plumbing: mixxxxx publishes a named video
              source on your LAN; other apps subscribe — no HDMI dongle, no fragile window capture.
            </p>
            <h3 className="text-base font-medium text-slate-200">Analogy</h3>
            <p className="text-slate-400">
              OSC is like texting mixxxxx (“crossfade harder”). NDI is like shipping the actual video
              feed to Resolume or OBS over the network.
            </p>
            <h3 className="text-base font-medium text-slate-200">Setup checklist</h3>
            <ol className="list-decimal pl-5 space-y-2 text-slate-400">
              <li>
                Install{" "}
                <a href="https://ndi.link/NDIRedistV5" className={linkClass} target="_blank" rel="noreferrer">
                  NDI redistributable
                </a>{" "}
                (free).
              </li>
              <li>
                Set environment variable <code>NDI_RUNTIME_DIR_V5</code> to the folder containing{" "}
                <code>Processing.NDI.Lib.x64.dll</code>.
              </li>
              <li>
                In mixxxxx: enable <code>[Ndi],enabled</code> or start with <code>--ndi-enable</code>.
              </li>
              <li>Open NDI Studio Monitor → look for source <strong>Mixxxxx</strong> (or your custom name).</li>
              <li>In Resolume/OBS: add NDI input → same source name.</li>
            </ol>
            <p className="text-slate-500 text-sm">
              Wired gigabit is recommended for 1080p. Wi‑Fi works for testing; treat it as best-effort
              live.
            </p>
            <p className="text-slate-500 text-sm">
              Implementation: mixxxxx <code>VideoMixer</code> blend → NDI sender thread. Licensing:{" "}
              <code>docs/NDI-LICENSING.md</code> (headers only in git; runtime is separate).
            </p>

            <h3 className="text-base font-medium text-slate-200 mt-6">Important NDI targets</h3>
            <p className="text-slate-400 text-sm">
              mixxxxx <em>publishes</em>; these apps <em>subscribe</em>. Full writeup: mixxxxx{" "}
              <code>docs/NDI-TARGETS.md</code>.
            </p>
            <table className="w-full text-sm border border-slate-800 rounded-lg overflow-hidden mt-3">
              <thead className="bg-slate-900">
                <tr>
                  <th className="text-left p-2 text-slate-400">Target</th>
                  <th className="text-left p-2 text-slate-400">Use</th>
                  <th className="text-left p-2 text-slate-400">Cost</th>
                </tr>
              </thead>
              <tbody className="text-slate-400">
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">NDI Studio Monitor</td>
                  <td className="p-2">Verify feed — always test here first</td>
                  <td className="p-2">Free</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">OBS + DistroAV</td>
                  <td className="p-2">Stream/record; NDI Source → overlays → RTMP</td>
                  <td className="p-2">Free</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">Resolume Avenue/Arena</td>
                  <td className="p-2">VJ layers on top of mixxxxx video</td>
                  <td className="p-2">Demo free · Avenue ~€299</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">vMix / Wirecast</td>
                  <td className="p-2">Broadcast-style software switcher</td>
                  <td className="p-2">Paid</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">TouchDesigner</td>
                  <td className="p-2">Custom generative / projection visuals</td>
                  <td className="p-2">Free–paid</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2 font-medium text-slate-300">Zoom / Teams</td>
                  <td className="p-2">Usually OBS Virtual Cam bridge — not native NDI</td>
                  <td className="p-2">Varies</td>
                </tr>
              </tbody>
            </table>
            <p className="text-slate-500 text-sm mt-3">
              Not targets: NDI PTZ cameras and HDMI→NDI boxes are typically <em>sources</em>, not
              consumers of mixxxxx. mixxxxx does not send NDI HX (GPL / Advanced SDK).
            </p>
          </section>
        )}

        {tab === "resolume" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">Resolume in this stack</h2>
            <p className="text-slate-400">
              <strong className="text-slate-200">Resolume</strong> is a visual mixer: layers, clips,
              effects, multi-output for projectors. mixxxxx sends the <em>base</em> crossfaded video
              (via NDI); Resolume adds VJ layers on top.{" "}
              <strong className="text-slate-200">resolume-mcp</strong> lets AI/tools drive Resolume
              over OSC.
            </p>
            <h3 className="text-base font-medium text-slate-200">Avenue vs Arena</h3>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>
                <strong className="text-slate-200">Avenue</strong> (~€299 one-time) — entry tier; NDI
                in/out, OSC, enough for many mobile/club setups and for testing this integration.
              </li>
              <li>
                <strong className="text-slate-200">Arena</strong> — advanced mapping, DMX, more outputs;
                what resolume-mcp docs target by name. Overkill until you need projection mapping.
              </li>
            </ul>
            <h3 className="text-base font-medium text-slate-200">Should you buy it?</h3>
            <p className="text-slate-400">
              <strong className="text-slate-200">For NDI testing only</strong> — no. Use free NDI
              Studio Monitor or OBS NDI Source first.
            </p>
            <p className="text-slate-400">
              <strong className="text-slate-200">For full mixxxxx + resolume-mcp integration</strong>{" "}
              — yes, reasonable if you are building the fleet rig or gig with layered visuals. Many
              mobile DJs use Avenue as the “visual deck” next to Serato/VDJ/mixxx-class apps; you are
              wiring the open-source version of that story.
            </p>
            <p className="text-slate-400">
              <strong className="text-slate-200">Before paying</strong> — install Resolume’s{" "}
              <a href="https://resolume.com/download/" className={linkClass} target="_blank" rel="noreferrer">
                unlimited demo
              </a>{" "}
              (watermark on output). Enough to develop resolume-mcp, test NDI input, and run{" "}
              <code>mixx_daw(resolume_sync)</code> BPM OSC on port 7000.
            </p>
            <h3 className="text-base font-medium text-slate-200">Integration pieces</h3>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li>Video: mixxxxx NDI → Resolume NDI input layer</li>
              <li>Tempo/energy: mixx-dj-mcp → Resolume OSC (see <code>docs/AUDIO_REACTIVE_VISUALS.md</code>)</li>
              <li>Clip/layer MCP: resolume-mcp repo</li>
            </ul>
          </section>
        )}

        {tab === "video" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">Video in mixxxxx</h2>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>Companion file: same basename as audio (<code>.mp4</code>, <code>.mkv</code>, …).</li>
              <li>
                Fallback chain when no file: pool loops → generative beats → Ken Burns album art.
              </li>
              <li>
                Use skin <strong className="text-slate-200">Mixxxxx Video</strong> or enable video in
                LateNight skin settings.
              </li>
              <li>Legacy skins only — QML skin has no VideoWidget.</li>
              <li>OSC / this webapp when mixxxxx is running and connected.</li>
            </ul>
            <p className="text-slate-500 text-sm">
              Local output: 2nd monitor or projector. Network output: NDI tab. Orchestration: AV Rig tab.
            </p>
          </section>
        )}

        {tab === "skins" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">Skins</h2>
            <p className="text-slate-400">
              No central marketplace (unlike VirtualDJ). Install community skins into{" "}
              <code>%LOCALAPPDATA%\Mixxx\skins\</code> — see mixxxxx <code>docs/SKINS.md</code>.
            </p>
            <p className="text-slate-400">
              Use the <strong className="text-slate-200">Skins</strong> page here to browse the
              manifest; <code>mixx_skin(create_video_skin)</code> copies Mixxxxx Video to your user
              folder.
            </p>
          </section>
        )}

        {tab === "osc" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">OSC bridge</h2>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>mixxxxx listens on UDP <strong>11119</strong>, sends on <strong>11118</strong>.</li>
              <li>Heartbeat: <code>/mixxxxx/ping</code> → <code>/mixxxxx/pong</code>.</li>
              <li>mixx-dj-mcp must see a live mixxxxx instance — dashboard shows connection status.</li>
              <li>Resolume default OSC input is often port <strong>7000</strong> (separate from mixxxxx).</li>
            </ul>
          </section>
        )}
      </motion.div>
    </div>
  );
}
