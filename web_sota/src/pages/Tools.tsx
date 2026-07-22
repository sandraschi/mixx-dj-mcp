import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Wrench, ChevronDown, Code, FileText } from "lucide-react";
import { apiGet } from "../lib/api";

interface ToolInfo {
  name: string;
  description?: string;
  parameters?: Record<string, unknown>;
  examples?: string[];
  category?: string;
}

export default function Tools() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await apiGet<{
          tools: ToolInfo[];
        }>("/api/v1/diagnostics");
        setTools(data.tools || []);
      } catch {
        setTools([]);
      }
      setLoading(false);
    })();
  }, []);

  if (loading) {
    return (
      <div data-testid="tools-page" className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2 text-slate-500">
          <Wrench size={20} className="animate-pulse" />
          <span>Loading tools...</span>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="tools-page" className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-100">Tools</h2>
      <p className="text-sm text-slate-500">
        {tools.length} tool(s) registered on the server
      </p>

      <div className="space-y-2">
        {tools.map((tool) => {
          const isPortmanteau =
            tool.parameters &&
            typeof tool.parameters === "object" &&
            "operation" in tool.parameters;
          return (
            <motion.div
              key={tool.name}
              className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <button
                onClick={() =>
                  setExpanded(expanded === tool.name ? null : tool.name)
                }
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Wrench size={16} className="text-amber-400 shrink-0" />
                  <span className="text-sm font-medium text-slate-200">
                    {tool.name}
                  </span>
                  {isPortmanteau && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 font-medium">
                      PORTMANTEAU
                    </span>
                  )}
                </div>
                <ChevronDown
                  size={16}
                  className={`text-slate-500 transition-transform ${
                    expanded === tool.name ? "rotate-180" : ""
                  }`}
                />
              </button>

              <AnimatePresence>
                {expanded === tool.name && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-slate-800"
                  >
                    <div className="px-4 py-3 space-y-3">
                      {tool.description && (
                        <p className="text-xs text-slate-400 leading-relaxed">
                          {tool.description}
                        </p>
                      )}
                      {tool.parameters && (
                        <div>
                          <div className="flex items-center gap-1.5 mb-1">
                            <Code size={12} className="text-slate-500" />
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                              Parameters
                            </span>
                          </div>
                          <pre className="text-[11px] text-slate-400 bg-slate-950 rounded-lg p-2 overflow-x-auto">
                            {JSON.stringify(tool.parameters, null, 2)}
                          </pre>
                        </div>
                      )}
                      {tool.examples && tool.examples.length > 0 && (
                        <div>
                          <div className="flex items-center gap-1.5 mb-1">
                            <FileText size={12} className="text-slate-500" />
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                              Examples
                            </span>
                          </div>
                          {tool.examples.map((ex, i) => (
                            <pre
                              key={i}
                              className="text-[11px] text-emerald-400 bg-slate-950 rounded-lg p-2 mb-1 overflow-x-auto"
                            >
                              {ex}
                            </pre>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
