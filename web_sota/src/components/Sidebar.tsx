import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Disc3,
  Library,
  Sparkles,
  Monitor,
  MessageSquare,
  Wrench,
  Palette,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";
import { useStore } from "../lib/store";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/cockpit", icon: Monitor, label: "Cockpit" },
  { to: "/decks", icon: Disc3, label: "Decks" },
  { to: "/library", icon: Library, label: "Library" },
  { to: "/effects", icon: Sparkles, label: "Effects" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/tools", icon: Wrench, label: "Tools" },
  { to: "/skins", icon: Palette, label: "Skins" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  const collapsed = useStore((s) => s.sidebarCollapsed);
  const setCollapsed = useStore((s) => s.setSidebarCollapsed);
  const backendStatus = useStore((s) => s.backendStatus);

  return (
    <motion.aside
      className="flex flex-col border-r border-slate-800 bg-slate-950/90 backdrop-blur-xl h-full overflow-hidden z-20"
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
    >
      <div className="flex items-center justify-between px-4 h-14 border-b border-slate-800 shrink-0">
        {!collapsed && (
          <span className="font-bold text-amber-400 text-lg tracking-wide whitespace-nowrap">
            Mixx-MCP
          </span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition-colors"
          data-testid="sidebar-toggle"
        >
          {collapsed ? (
            <ChevronRight size={20} />
          ) : (
            <ChevronLeft size={20} />
          )}
        </button>
      </div>

      <nav className="flex-1 flex flex-col gap-1 px-2 py-4 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            data-testid={`nav-${label.toLowerCase()}`}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? "bg-amber-500/10 text-amber-400"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`
            }
          >
            <Icon size={20} className="shrink-0" />
            {!collapsed && (
              <span className="text-sm font-medium whitespace-nowrap">
                {label}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-800 px-4 py-3 flex items-center gap-2 shrink-0">
        <span
          data-testid="sidebar-status-dot"
          className={`w-2 h-2 rounded-full shrink-0 ${
            backendStatus === "connected"
              ? "bg-green-500"
              : backendStatus === "error"
                ? "bg-red-500"
                : "bg-gray-500 animate-pulse"
          }`}
        />
        {!collapsed && (
          <span className="text-xs text-slate-500 capitalize">
            {backendStatus}
          </span>
        )}
      </div>
    </motion.aside>
  );
}
