import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search, Palette, Download, Check, Tag, User, Hash, ExternalLink } from "lucide-react";

interface SkinEntry {
  id: string;
  name: string;
  author: string;
  version: string;
  description: string;
  tags: string[];
  screenshotUrl?: string;
  downloadUrl?: string;
  installed: boolean;
}

const SKIN_DATA: SkinEntry[] = [
  {
    id: "mixxxxx-video",
    name: "Mixxxxx Video",
    author: "sandraschi",
    version: "1.0.0",
    description: "LateNight-based with video preview widgets, output panel, and projector controls built in",
    tags: ["video-ready", "4-deck", "dark", "recommended"],
    screenshotUrl: "",
    downloadUrl: "",
    installed: true,
  },
  {
    id: "latenight",
    name: "LateNight",
    author: "owilliams, ronso0",
    version: "2.4.0.01",
    description: "Wide nighttime skin with stacked waveforms, 4 decks, up to 16 samplers",
    tags: ["4-deck", "waveforms", "hotcues"],
    installed: false,
  },
  {
    id: "deere",
    name: "Deere",
    author: "Be",
    version: "2.4.0.01",
    description: "Clean, minimal skin with 4 decks and broad layout",
    tags: ["4-deck", "minimal", "clean"],
    installed: false,
  },
  {
    id: "shade",
    name: "Shade",
    author: "Tobias Esterer",
    version: "2.4.0.01",
    description: "Dark, compact skin for smaller screens",
    tags: ["dark", "compact"],
    installed: false,
  },
  {
    id: "tango",
    name: "Tango",
    author: "Tobias Esterer",
    version: "2.4.0.01",
    description: "Colorful skin with bold visuals",
    tags: ["colorful", "waveforms"],
    installed: false,
  },
];

const ALL_TAGS = ["video-ready", "4-deck", "minimal", "dark", "LateNight-based", "Deere-based", "Tango", "Shade"];

function SkinPlaceholder({ name, tags }: { name: string; tags: string[] }) {
  const colorMap: Record<string, string> = {
    "video-ready": "from-purple-600 to-blue-600",
    "4-deck": "from-slate-700 to-slate-900",
    dark: "from-slate-800 to-zinc-950",
    minimal: "from-zinc-600 to-slate-800",
    colorful: "from-pink-500 via-amber-400 to-cyan-400",
    clean: "from-teal-600 to-slate-800",
    waveforms: "from-emerald-600 to-slate-900",
    compact: "from-orange-600 to-slate-900",
  };
  const gradient = tags
    .map((t) => colorMap[t])
    .filter(Boolean)
    .join(", ");
  return (
    <div
      className={`w-full aspect-[16/10] rounded-lg flex items-center justify-center bg-gradient-to-br ${
        gradient || "from-slate-700 to-slate-900"
      }`}
    >
      <div className="text-center">
        <Palette size={32} className="mx-auto text-white/40 mb-1" />
        <p className="text-[10px] text-white/30 font-medium">{name}</p>
      </div>
    </div>
  );
}

export default function Skins() {
  const [search, setSearch] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [installing, setInstalling] = useState<string | null>(null);

  const toggleTag = (tag: string) => {
    setActiveTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  const filtered = useMemo(() => {
    return SKIN_DATA.filter((skin) => {
      if (search) {
        const q = search.toLowerCase();
        if (
          !skin.name.toLowerCase().includes(q) &&
          !skin.author.toLowerCase().includes(q)
        )
          return false;
      }
      if (activeTags.length > 0) {
        if (!activeTags.every((t) => skin.tags.includes(t))) return false;
      }
      return true;
    });
  }, [search, activeTags]);

  const handleInstall = async (skin: SkinEntry) => {
    setInstalling(skin.id);
    await new Promise((r) => setTimeout(r, 1200));
    setInstalling(null);
  };

  return (
    <div data-testid="skins-page" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Skins</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Browse and manage Mixxx skins
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Palette size={14} />
          <span>{SKIN_DATA.length} skins</span>
        </div>
      </div>

      <div className="flex gap-4">
        {/* Sidebar filters */}
        <div className="w-52 shrink-0 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
            />
            <input
              type="text"
              placeholder="Search skins..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-slate-700 bg-slate-900 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500/50"
              data-testid="skins-search"
            />
          </div>

          {/* Tag filters */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Tag size={12} className="text-slate-500" />
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">
                Filters
              </span>
            </div>
            <div className="space-y-1">
              {ALL_TAGS.map((tag) => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  data-testid={`tag-filter-${tag}`}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-xs transition-colors ${
                    activeTags.includes(tag)
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
            {activeTags.length > 0 && (
              <button
                onClick={() => setActiveTags([])}
                className="mt-2 text-[10px] text-slate-500 hover:text-slate-300 transition-colors"
              >
                Clear filters
              </button>
            )}
          </div>
        </div>

        {/* Skin grid */}
        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 auto-rows-max">
          {filtered.map((skin, i) => (
            <motion.div
              key={skin.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.25 }}
              className="group rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden hover:border-slate-700 hover:bg-slate-900/80 transition-all"
              data-testid={`skin-card-${skin.id}`}
            >
              {/* Screenshot / placeholder */}
              {skin.screenshotUrl ? (
                <img
                  src={skin.screenshotUrl}
                  alt={skin.name}
                  className="w-full aspect-[16/10] object-cover"
                />
              ) : (
                <SkinPlaceholder name={skin.name} tags={skin.tags} />
              )}

              <div className="p-3 space-y-2.5">
                {/* Name + recommended badge */}
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <h3 className="text-sm font-medium text-slate-200 truncate">
                      {skin.name}
                    </h3>
                    <div className="flex items-center gap-1 mt-0.5">
                      <User size={10} className="text-slate-500 shrink-0" />
                      <span className="text-[10px] text-slate-500 truncate">
                        {skin.author}
                      </span>
                    </div>
                  </div>
                  {skin.tags.includes("recommended") && (
                    <span className="shrink-0 text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 font-medium border border-amber-500/20">
                      RECOMMENDED
                    </span>
                  )}
                </div>

                {/* Version + installed badge */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <Hash size={10} className="text-slate-500" />
                    <span className="text-[10px] text-slate-500">{skin.version}</span>
                  </div>
                  {skin.installed && (
                    <span className="flex items-center gap-0.5 text-[10px] text-emerald-400">
                      <Check size={10} />
                      Installed
                    </span>
                  )}
                  {!skin.downloadUrl && !skin.installed && (
                    <span className="text-[10px] text-slate-600 italic">No download link</span>
                  )}
                </div>

                {/* Description */}
                <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">
                  {skin.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {skin.tags.filter((t) => t !== "recommended").map((tag) => (
                    <span
                      key={tag}
                      className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Actions */}
                <div className="pt-1">
                  {skin.installed ? (
                    <span className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs text-emerald-400 bg-emerald-500/5 border border-emerald-500/10">
                      <Check size={12} />
                      Installed
                    </span>
                  ) : skin.downloadUrl || skin.id === "mixxxxx-video" ? (
                    <button
                      onClick={() => handleInstall(skin)}
                      disabled={installing === skin.id}
                      className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs font-medium text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-wait transition-colors"
                      data-testid={`install-skin-${skin.id}`}
                    >
                      {installing === skin.id ? (
                        <>
                          <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Installing...
                        </>
                      ) : (
                        <>
                          <Download size={12} />
                          Install
                        </>
                      )}
                    </button>
                  ) : (
                    <span className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs text-slate-600 bg-slate-800/50">
                      <ExternalLink size={10} />
                      Not available
                    </span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-slate-500">
          <Palette size={40} className="mb-3 opacity-30" />
          <p className="text-sm">No skins match your filters</p>
          <button
            onClick={() => {
              setSearch("");
              setActiveTags([]);
            }}
            className="mt-2 text-xs text-amber-400 hover:text-amber-300 transition-colors"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}
