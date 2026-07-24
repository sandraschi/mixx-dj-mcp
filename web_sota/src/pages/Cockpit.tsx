import { useState, useCallback, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Send,
  Loader2,
  Monitor,
  Play,
  Pause,
  Radio,
  Circle,
  Zap,
} from "lucide-react";
import { useStore } from "../lib/store";
import {
  apiPost,
  fetchNowPlaying,
  type NowPlayingDeck,
} from "../lib/api";
import PlexPanel from "../components/PlexPanel";
import SFXPanel from "../components/SFXPanel";
import SongGenPanel from "../components/SongGenPanel";
import DeckStrip from "../components/DeckStrip";
import Visualizer from "../components/Visualizer";
import type { CockpitMessage } from "../lib/types";

export default function Cockpit() {
  const decks = useStore((s) => s.decks);
  const backendStatus = useStore((s) => s.backendStatus);
  const [messages, setMessages] = useState<CockpitMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [np, setNp] = useState<NowPlayingDeck[]>([]);
  const [recording, setRecording] = useState<{ name: string; events: number } | null>(null);
  const [fleetSources, setFleetSources] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const data = await fetchNowPlaying();
        setNp(data.decks);
        setRecording(data.recording);
        setFleetSources(data.external_sources);
      } catch {}
      timer = setTimeout(poll, 5000);
    };
    poll();
    return () => clearTimeout(timer);
  }, []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    setSending(true);
    const userMsg: CockpitMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    try {
      const reply = await apiPost<{ response: string }>("/api/chat", {
        message: text,
        context: "cockpit",
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Backend unreachable. Start the server to use the AI assistant.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }, [input, sending]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage],
  );

  const playingCount = decks.filter((d) => d.playing).length;

  return (
    <div data-testid="cockpit-page" className="flex flex-col h-full gap-3">
      {/* Header with mini deck indicators + recording status */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Monitor size={20} className="text-amber-400" />
          <h2 className="text-xl font-semibold text-slate-100">
            Performance Cockpit
          </h2>
          {recording && (
            <span className="flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-medium bg-red-500/10 text-red-400 border border-red-500/20 animate-pulse">
              <Circle size={6} className="fill-red-400" />
              REC {recording.events}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {fleetSources.length > 0 && (
            <span className="flex items-center gap-1 text-[10px] text-purple-400">
              <Zap size={10} />
              {fleetSources.length} source{fleetSources.length > 1 ? "s" : ""}
            </span>
          )}
          {np.map((d) => (
            <div
              key={d.id}
              className="flex items-center gap-1.5 text-xs text-slate-500"
            >
              <span className="font-medium text-slate-400">D{d.id}</span>
              {d.playing ? (
                <Play size={12} className="text-green-400" />
              ) : (
                <Pause size={12} className="text-slate-600" />
              )}
              {d.bpm > 0 && (
                <span className="text-[10px] text-slate-600">{d.bpm.toFixed(1)}</span>
              )}
            </div>
          ))}
          <span className="text-xs text-slate-600 ml-2">
            {playingCount > 0
              ? `${playingCount} deck${playingCount > 1 ? "s" : ""} playing`
              : "all stopped"}
          </span>
        </div>
      </div>

      {/* Cross-MCP Fleet Hub — now playing from connected sources */}
      {fleetSources.length > 0 && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-900/10 border border-purple-800/20 text-[11px] text-purple-300">
          <Radio size={12} />
          <span>Fleet sources active:</span>
          {fleetSources.map((s) => (
            <span
              key={s}
              className="px-1.5 py-0.5 rounded bg-purple-800/20 text-purple-300 font-mono"
            >
              {s}
            </span>
          ))}
          <span className="text-slate-600 ml-auto">
            Cross-MCP deck handoff ready
          </span>
        </div>
      )}

      {/* Three-column panel area */}
      <div className="grid grid-cols-3 gap-3 flex-1 min-h-0">
        <PlexPanel />
        <SFXPanel />
        <SongGenPanel />
      </div>

      {/* Deck status strip */}
      <DeckStrip />

      {/* MilkDrop Visualizer */}
      <Visualizer className="h-28 w-full" />

      {/* AI Assistant chat bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden shrink-0"
      >
        {messages.length > 0 && (
          <div className="max-h-24 overflow-y-auto px-4 py-2 space-y-1 border-b border-slate-800">
            {messages.slice(-3).map((msg, i) => (
              <p
                key={i}
                className={`text-xs ${
                  msg.role === "user" ? "text-slate-300" : "text-amber-400/70"
                }`}
              >
                <span className="font-semibold text-[10px] uppercase tracking-wider text-slate-500 mr-1.5">
                  {msg.role === "user" ? "You" : "AI"}
                </span>
                {msg.content}
              </p>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 px-4 py-3">
          <span className="text-xs text-slate-500 font-medium shrink-0">
            Cockpit AI
          </span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. load songgen output to deck 3, play deck 1, record this set..."
            disabled={backendStatus !== "connected"}
            className="flex-1 px-3 py-1.5 text-sm rounded-lg bg-slate-800/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors disabled:opacity-40"
          />
          <button
            onClick={sendMessage}
            disabled={
              !input.trim() || sending || backendStatus !== "connected"
            }
            data-testid="cockpit-send"
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {sending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Send size={14} />
            )}
            Send
          </button>
        </div>
      </motion.div>
    </div>
  );
}
