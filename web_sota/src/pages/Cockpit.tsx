import { useState, useCallback, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Send,
  Loader2,
  Monitor,
  Play,
  Pause,
} from "lucide-react";
import { useStore } from "../lib/store";
import { apiPost } from "../lib/api";
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
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
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
      const assistantMsg: CockpitMessage = {
        role: "assistant",
        content: reply.response,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errMsg: CockpitMessage = {
        role: "assistant",
        content: "Backend unreachable. Start the server to use the AI assistant.",
      };
      setMessages((prev) => [...prev, errMsg]);
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
    <div data-testid="cockpit-page" className="flex flex-col h-full gap-4">
      {/* Header with mini deck indicators */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Monitor size={20} className="text-amber-400" />
          <h2 className="text-xl font-semibold text-slate-100">
            Mixx-DJ Cockpit
          </h2>
        </div>
        <div className="flex items-center gap-3">
          {decks.map((deck) => (
            <div
              key={deck.id}
              className="flex items-center gap-1.5 text-xs text-slate-500"
            >
              <span className="font-medium text-slate-400">D{deck.id}</span>
              {deck.playing ? (
                <Play size={12} className="text-green-400" />
              ) : (
                <Pause size={12} className="text-slate-600" />
              )}
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  deck.playing ? "bg-green-400 animate-pulse" : "bg-slate-700"
                }`}
              />
            </div>
          ))}
          <span className="text-xs text-slate-600 ml-2">
            {playingCount > 0
              ? `${playingCount} deck${playingCount > 1 ? "s" : ""} playing`
              : "all stopped"}
          </span>
        </div>
      </div>

      {/* Two-column panel area */}
      <div className="grid grid-cols-3 gap-4 flex-1 min-h-0">
        <PlexPanel />
        <SFXPanel />
        <SongGenPanel />
      </div>

      {/* Deck status strip */}
      <DeckStrip />

      {/* MilkDrop Visualizer */}
      <Visualizer className="h-32 w-full" />

      {/* AI Assistant chat bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden shrink-0"
      >
        {/* Recent messages */}
        {messages.length > 0 && (
          <div className="max-h-24 overflow-y-auto px-4 py-2 space-y-1 border-b border-slate-800">
            {messages.slice(-3).map((msg, i) => (
              <p
                key={i}
                className={`text-xs ${
                  msg.role === "user"
                    ? "text-slate-300"
                    : "text-amber-400/70"
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

        {/* Input row */}
        <div className="flex items-center gap-2 px-4 py-3">
          <span className="text-xs text-slate-500 font-medium shrink-0">
            AI Assistant
          </span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask the cockpit AI..."
            disabled={backendStatus !== "connected"}
            className="flex-1 px-3 py-1.5 text-sm rounded-lg bg-slate-800/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors disabled:opacity-40"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || sending || backendStatus !== "connected"}
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
