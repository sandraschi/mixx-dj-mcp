import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Send,
  Download,
  Eraser,
  Bot,
  User,
  Loader2,
} from "lucide-react";
import { API_BASE, fetchSkills, fetchSkillContent } from "../lib/api";

const STORAGE_KEY = "mixx-dj-mcp-chat-history";
const PERSONALITY_KEY = "mixx-dj-mcp-chat-personality";
const MAX_MESSAGES = 100;

interface Message {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

const PERSONALITIES: Record<
  string,
  { label: string; prompt: string }
> = {
  "research-assistant": {
    label: "Research Assistant",
    prompt:
      "You are a research assistant for Mixxx DJ software. Help the user understand decks, effects, library management, and performance techniques. Be concise and technical.",
  },
  "expert-reviewer": {
    label: "Expert Reviewer",
    prompt:
      "You are an expert Mixxx DJ reviewer. Analyze setups, suggest optimizations, and provide detailed technical feedback on DJ workflows and configurations.",
  },
  "quick-summarizer": {
    label: "Quick Summarizer",
    prompt:
      "You summarize Mixxx DJ topics concisely in 2-3 bullet points. Focus on key technical details and actionable advice.",
  },
  "custom": {
    label: "Custom",
    prompt: "",
  },
};

const EXAMPLE_PROMPTS = [
  { group: "Control", items: ["Load track to deck 1", "Sync deck 2 to deck 1", "Set crossfader to -0.5"] },
  { group: "Library", items: ["Search for tech house tracks", "Show my recently added tracks", "List crates"] },
  { group: "Effects", items: ["Add reverb to deck 3", "Configure flanger on chain 2", "Enable beatgrid on deck 1"] },
  { group: "Analysis", items: ["Analyze BPM for track in deck 2", "What key is the current track?", "Show cue points for loaded track"] },
];

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return [];
}

function saveHistory(messages: Message[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)));
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [personalityId, setPersonalityId] = useState(() => {
    return localStorage.getItem(PERSONALITY_KEY) || "research-assistant";
  });
  const [skillContent, setSkillContent] = useState("");
  const [providerStatus, setProviderStatus] = useState<"detecting" | "online" | "offline">("detecting");
  const [providerName, setProviderName] = useState("Ollama");
  const [providerHost, setProviderHost] = useState(":11434");
  const [modelName, setModelName] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    saveHistory(messages);
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(PERSONALITY_KEY, personalityId);
  }, [personalityId]);

  useEffect(() => {
    (async () => {
      try {
        const skills = await fetchSkills();
        if (skills.length > 0) {
          const content = await fetchSkillContent(skills[0]);
          setSkillContent(content);
        }
      } catch {
        setSkillContent("You are a helpful Mixxx DJ assistant. Help users manage their DJ sets, browse tracks, apply effects, and configure the software.");
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/llm/discover`, { signal: AbortSignal.timeout(3000) });
        if (r.ok) {
          const data = await r.json();
          setProviderStatus(data.status === "online" ? "online" : "offline");
          setProviderName(data.provider || "unknown");
          setProviderHost(data.host || "");
          if (data.models?.length) setModelName(data.models[0]);
        } else {
          setProviderStatus("offline");
        }
      } catch {
        setProviderStatus("offline");
      }
    })();
  }, []);

  const buildSystemPrompt = useCallback(() => {
    const rolePrompt = PERSONALITIES[personalityId]?.prompt || "";
    if (personalityId === "custom") return skillContent;
    return `${skillContent}\n\n---\n\n## Role\n${rolePrompt}`;
  }, [skillContent, personalityId]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = {
      role: "user",
      content: input.trim(),
      ts: new Date().toISOString(),
    };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const systemPrompt = buildSystemPrompt();
      const chatMessages = [
        { role: "system", content: systemPrompt },
        ...updated.map((m) => ({ role: m.role, content: m.content })),
      ];

      const baseUrl = `${API_BASE}/api/llm/chat`;
      const r = await fetch(baseUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: chatMessages, model: modelName || undefined }),
      });

      if (!r.ok) throw new Error(`HTTP ${r.status}`);

      const data = await r.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.message || data.response || JSON.stringify(data),
        ts: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      const errorMsg: Message = {
        role: "assistant",
        content: `**Error:** ${e instanceof Error ? e.message : "Failed to reach LLM provider"}`,
        ts: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
    setLoading(false);
  }, [input, loading, messages, buildSystemPrompt]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleExport = () => {
    const lines = messages.map(
      (m) => `[${m.ts || "no-timestamp"}] ${m.role === "user" ? "User" : "Assistant"}: ${m.content}`
    );
    const blob = new Blob([lines.join("\n\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mixx-dj-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div data-testid="chat-page" className="flex flex-col h-[calc(100vh-var(--topbar-height)-3rem)]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <select
            data-testid="personality-select"
            value={personalityId}
            onChange={(e) => setPersonalityId(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-amber-500/50"
          >
            {Object.entries(PERSONALITIES).map(([id, p]) => (
              <option key={id} value={id}>
                {p.label}
              </option>
            ))}
          </select>
          <span
            className={`text-[10px] px-2 py-0.5 rounded-full ${
              providerStatus === "online"
                ? "bg-green-500/10 text-green-400"
                : providerStatus === "offline"
                  ? "bg-red-500/10 text-red-400"
                  : "bg-slate-800 text-slate-500"
            }`}
          >
            {providerStatus === "online"
              ? `${providerName} on ${providerHost}`
              : providerStatus === "offline"
                ? "No Provider"
                : "Detecting..."}
          </span>
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded px-2 py-0.5 text-[10px] text-slate-400 font-mono focus:outline-none focus:border-amber-500/50"
            data-testid="model-input"
          >
            <option value="">auto</option>
            <option value="llama3.2:3b">llama3.2:3b</option>
            <option value="llama3.1:8b">llama3.1:8b</option>
            <option value="qwen2.5:7b">qwen2.5:7b</option>
            <option value="gemma3:12b">gemma3:12b</option>
            <option value="mistral:7b">mistral:7b</option>
          </select>
        </div>
        <div className="flex items-center gap-1" data-testid="chat-controls">
          <button
            data-testid="chat-export"
            onClick={handleExport}
            disabled={messages.length === 0}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors disabled:opacity-30"
            title="Export chat"
          >
            <Download size={16} />
          </button>
          <button
            data-testid="chat-clear"
            onClick={handleClear}
            disabled={messages.length === 0}
            className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors disabled:opacity-30"
            title="Clear chat"
          >
            <Eraser size={16} />
          </button>
        </div>
      </div>

      <div
        data-testid="chat-messages"
        className="flex-1 overflow-y-auto space-y-3 pr-2"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Bot size={40} className="text-slate-700 mb-3" />
            <p className="text-sm text-slate-500 mb-4">
              Ask me anything about Mixxx DJ
            </p>
            <div data-testid="example-prompts" className="space-y-2 max-w-md">
              {EXAMPLE_PROMPTS.map((group) => (
                <div key={group.group}>
                  <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1">
                    {group.group}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {group.items.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => {
                          setInput(prompt);
                        }}
                        className="text-xs px-2.5 py-1.5 rounded-full bg-slate-800/50 text-slate-400 hover:bg-slate-700 hover:text-slate-200 transition-colors border border-slate-700/50"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
          >
            {msg.role === "assistant" && (
              <div className="w-7 h-7 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0 mt-1">
                <Bot size={14} className="text-amber-400" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-amber-500/10 text-slate-200 border border-amber-500/20"
                  : "bg-slate-900 text-slate-300 border border-slate-800"
              }`}
            >
              {msg.content}
            </div>
            {msg.role === "user" && (
              <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center shrink-0 mt-1">
                <User size={14} className="text-slate-400" />
              </div>
            )}
          </motion.div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0">
              <Bot size={14} className="text-amber-400" />
            </div>
            <div className="rounded-xl px-4 py-2.5 bg-slate-900 border border-slate-800">
              <Loader2 size={16} className="animate-spin text-slate-500" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2 mt-3 pt-3 border-t border-slate-800">
        <input
          data-testid="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about Mixxx DJ..."
          disabled={loading}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-colors disabled:opacity-50"
        />
        <button
          data-testid="chat-send"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="px-4 py-2.5 bg-amber-500/10 text-amber-400 rounded-lg hover:bg-amber-500/20 transition-colors disabled:opacity-30"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
