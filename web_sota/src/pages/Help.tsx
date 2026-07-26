import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Radio, Palette, Video, Plug } from "lucide-react";

type TabId = "overview" | "ndi" | "video" | "skins" | "osc";

const tabs: { id: TabId; label: string; icon: typeof BookOpen }[] = [
  { id: "overview", label: "Overview", icon: BookOpen },
  { id: "ndi", label: "NDI", icon: Radio },
  { id: "video", label: "Video", icon: Video },
  { id: "skins", label: "Skins", icon: Palette },
  { id: "osc", label: "OSC / MCP", icon: Plug },
];

export default function Help() {
  const [tab, setTab] = useState<TabId>("overview");

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Help</h1>
        <p className="text-slate-400 text-sm mt-1">
          mixxxxx + mixx-dj-mcp — concepts, not a substitute for the Mixxx manual.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === id
                ? "bg-amber-500/15 text-amber-400"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      <motion.div
        key={tab}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="prose prose-invert prose-sm max-w-none text-slate-300"
      >
        {tab === "overview" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">What is this stack?</h2>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>
                <strong className="text-slate-200">mixxxxx</strong> — Mixxx fork with per-deck
                video, export CLI, OSC server (UDP 11118/11119).
              </li>
              <li>
                <strong className="text-slate-200">mixx-dj-mcp</strong> — MCP + this webapp;
                controls mixxxxx when it is running.
              </li>
            </ul>
            <p className="text-slate-400">
              Full Mixxx preferences: <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-xs">Ctrl+P</kbd>.
              The top-right gear is skin layout only, not app settings.
            </p>
            <p className="text-slate-500 text-xs">
              Repo docs: mixxxxx <code>docs/STATUS.md</code>, <code>docs/SKINS.md</code>,{" "}
              <code>docs/NDI.md</code>.
            </p>
          </section>
        )}

        {tab === "ndi" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">NDI — network video output</h2>
            <p className="text-amber-400/90 text-sm font-medium">
              Planned (TODO 27). Not in the build yet.
            </p>
            <p>
              <strong className="text-slate-200">NDI</strong> (Network Device Interface) sends live
              video over your LAN so other apps can use mixxxxx as a video source — no HDMI dongle,
              no window capture.
            </p>
            <h3 className="text-base font-medium text-slate-200">Who consumes it?</h3>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li>OBS Studio (NDI Source plugin) — streaming</li>
              <li>Resolume — club VJ layers on top of your mix</li>
              <li>vMix, NDI Studio Monitor — broadcast / test</li>
            </ul>
            <h3 className="text-base font-medium text-slate-200">Today vs planned</h3>
            <table className="w-full text-sm border border-slate-800 rounded-lg overflow-hidden">
              <thead className="bg-slate-900">
                <tr>
                  <th className="text-left p-2 text-slate-400">Today</th>
                  <th className="text-left p-2 text-slate-400">With NDI</th>
                </tr>
              </thead>
              <tbody className="text-slate-400">
                <tr className="border-t border-slate-800">
                  <td className="p-2">Video on a 2nd monitor window</td>
                  <td className="p-2">Named source on the network</td>
                </tr>
                <tr className="border-t border-slate-800">
                  <td className="p-2">OBS needs display capture</td>
                  <td className="p-2">OBS adds NDI Source — clean feed</td>
                </tr>
              </tbody>
            </table>
            <p className="text-slate-500 text-sm">
              NDI is not a file format. It is a live pipe between apps on the same network
              (gigabit wired recommended for 1080p).
            </p>
            <p className="text-slate-500 text-sm">
              Implementation plan: optional NDI SDK, publish frames from{" "}
              <code className="text-slate-400">VideoMixer::blendFrame()</code>, CMake{" "}
              <code className="text-slate-400">NDI=ON</code>. Details in mixxxxx{" "}
              <code className="text-slate-400">docs/NDI.md</code>.
            </p>
          </section>
        )}

        {tab === "video" && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">Video in mixxxxx</h2>
            <ul className="list-disc pl-5 space-y-2 text-slate-400">
              <li>Companion file: same basename as audio (<code>.mp4</code>, <code>.mkv</code>, …).</li>
              <li>
                Use skin <strong className="text-slate-200">Mixxxxx Video</strong> (Daylight scheme
                for bright rooms) or enable video in LateNight skin settings.
              </li>
              <li>Legacy skins only — QML skin has no VideoWidget.</li>
              <li>OSC: deck video enable / fullscreen via mixx-dj-mcp when mixxxxx is running.</li>
            </ul>
            <p className="text-slate-500 text-sm">
              Roadmap: beat-locked FX → fallback when no video file → NDI output.
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
            </ul>
          </section>
        )}
      </motion.div>
    </div>
  );
}
