import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Palette,
  Download,
  Check,
  Tag,
  User,
  Hash,
  ExternalLink,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import {
  callTool,
  fetchSkins,
  type SkinManifestEntry,
} from "../lib/api";
import { useStore } from "../lib/store";
import { FeatureNotice } from "../components/FeatureGate";
import { featureEnabled } from "../lib/capabilities";

function SkinPlaceholder({ name, tags }: { name: string; tags: string[] }) {
  const colorMap: Record<string, string> = {
    "video-ready": "from-purple-600 to-blue-600",
    daylight: "from-sky-200 via-amber-100 to-slate-300",
    "4-deck": "from-slate-700 to-slate-900",
    dark: "from-slate-800 to-zinc-950",
    minimal: "from-zinc-600 to-slate-800",
    colorful: "from-pink-500 via-amber-400 to-cyan-400",
    clean: "from-teal-600 to-slate-800",
    waveforms: "from-emerald-600 to-slate-900",
    compact: "from-orange-600 to-slate-900",
    community: "from-indigo-600 to-violet-900",
    svg: "from-fuchsia-600 to-slate-900",
  };
  const gradient =
    tags.map((t) => colorMap[t]).filter(Boolean)[0] ||
    "from-slate-700 to-slate-900";
  return (
    <div
      className={`w-full aspect-[16/10] rounded-lg flex items-center justify-center bg-gradient-to-br ${gradient}`}
    >
      <div className="text-center">
        <Palette size={32} className="mx-auto text-white/40 mb-1" />
        <p className="text-[10px] text-white/30 font-medium">{name}</p>
      </div>
    </div>
  );
}

export default function Skins() {
  const engineCaps = useStore((s) => s.engineCaps);
  const videoSkinsOk = featureEnabled(engineCaps, "video_skins");
  const [skins, setSkins] = useState<SkinManifestEntry[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [installing, setInstalling] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadSkins = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSkins();
      setSkins(data.skins);
      setAllTags(data.tags);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load skins");
      setSkins([]);
      setAllTags([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSkins();
  }, [loadSkins]);

  const toggleTag = (tag: string) => {
    setActiveTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  const filtered = useMemo(() => {
    return skins.filter((skin) => {
      if (search) {
        const q = search.toLowerCase();
        if (
          !skin.name.toLowerCase().includes(q) &&
          !skin.author.toLowerCase().includes(q) &&
          !skin.description.toLowerCase().includes(q)
        ) {
          return false;
        }
      }
      if (activeTags.length > 0) {
        if (!activeTags.every((t) => skin.tags.includes(t))) return false;
      }
      return true;
    });
  }, [skins, search, activeTags]);

  const handleAction = async (skin: SkinManifestEntry) => {
    setActionMessage(null);
    const isVideoSkin =
      skin.install_action === "create_video_skin" ||
      skin.tags.includes("video-ready");
    if (isVideoSkin && !videoSkinsOk) {
      setActionMessage(
        engineCaps.is_vanilla
          ? "Video skins require mixxxxx (video fork)."
          : "Connect mixxxxx via OSC to install video skins.",
      );
      return;
    }
    if (skin.install_action === "external" && skin.source_url) {
      window.open(skin.source_url, "_blank", "noopener,noreferrer");
      return;
    }

    setInstalling(skin.id);
    try {
      if (skin.install_action === "create_video_skin") {
        const res = await callTool("mixx_skin", {
          operation: "create_video_skin",
        });
        const result = res.result as { message?: string; success?: boolean };
        setActionMessage(result?.message || "Mixxxxx Video skin installed.");
        await loadSkins();
      } else if (skin.install_action === "preferences") {
        setActionMessage(
          `'${skin.name}' ships with Mixxx. Open Mixxx → Preferences → Interface → Skin.`,
        );
      } else {
        setActionMessage(
          skin.source_url
            ? `Download manually: ${skin.source_url}`
            : "Manual install required.",
        );
      }
    } catch (err) {
      setActionMessage(
        err instanceof Error ? err.message : "Skin action failed",
      );
    } finally {
      setInstalling(null);
    }
  };

  return (
    <div data-testid="skins-page" className="space-y-6">
      <FeatureNotice caps={engineCaps} feature="video_skins" />
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Skins</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Browse and manage Mixxx skins — including Mixxxxx Video and daylight
            schemes
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <button
            type="button"
            onClick={() => void loadSkins()}
            className="flex items-center gap-1.5 px-2 py-1 rounded-lg border border-slate-700 hover:border-slate-600 hover:text-slate-300 transition-colors"
            data-testid="skins-refresh"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <span className="flex items-center gap-1.5">
            <Palette size={14} />
            {loading ? "…" : `${skins.length} skins`}
          </span>
        </div>
      </div>

      {actionMessage && (
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-2 text-xs text-amber-200">
          {actionMessage}
        </div>
      )}

      {error && (
        <div className="flex items-start gap-3 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <div>
            <p>Could not load skins from mixx-dj-mcp backend.</p>
            <p className="text-xs text-red-400/80 mt-1">{error}</p>
            <button
              type="button"
              onClick={() => void loadSkins()}
              className="mt-2 text-xs text-amber-400 hover:text-amber-300"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-4 min-h-0">
        <div className="w-52 shrink-0 space-y-4">
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

          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Tag size={12} className="text-slate-500" />
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">
                Filters
              </span>
            </div>
            <div className="space-y-1 max-h-[50vh] overflow-y-auto">
              {allTags.map((tag) => (
                <button
                  key={tag}
                  type="button"
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
                type="button"
                onClick={() => setActiveTags([])}
                className="mt-2 text-[10px] text-slate-500 hover:text-slate-300 transition-colors"
              >
                Clear filters
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-xl border border-slate-800 bg-slate-900/30 h-64 animate-pulse"
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 auto-rows-max">
              {filtered.map((skin, i) => (
                <motion.div
                  key={skin.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04, duration: 0.25 }}
                  className="group rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden hover:border-slate-700 hover:bg-slate-900/80 transition-all"
                  data-testid={`skin-card-${skin.id}`}
                >
                  {skin.preview_url ? (
                    <img
                      src={skin.preview_url}
                      alt={skin.name}
                      className="w-full aspect-[16/10] object-cover"
                    />
                  ) : (
                    <SkinPlaceholder name={skin.name} tags={skin.tags} />
                  )}

                  <div className="p-3 space-y-2.5">
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

                    <div className="flex items-center gap-2 flex-wrap">
                      {skin.version && (
                        <div className="flex items-center gap-1">
                          <Hash size={10} className="text-slate-500" />
                          <span className="text-[10px] text-slate-500">
                            {skin.version}
                          </span>
                        </div>
                      )}
                      {skin.installed && (
                        <span className="flex items-center gap-0.5 text-[10px] text-emerald-400">
                          <Check size={10} />
                          Installed
                        </span>
                      )}
                      {skin.bundled && !skin.installed && (
                        <span className="text-[10px] text-slate-500">
                          Bundled with Mixxx
                        </span>
                      )}
                    </div>

                    <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">
                      {skin.description}
                    </p>

                    <div className="flex flex-wrap gap-1">
                      {skin.tags
                        .filter((t) => t !== "recommended")
                        .map((tag) => (
                          <span
                            key={tag}
                            className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400"
                          >
                            {tag}
                          </span>
                        ))}
                    </div>

                    <div className="pt-1">
                      {skin.install_action === "external" ? (
                        <button
                          type="button"
                          onClick={() => void handleAction(skin)}
                          className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs font-medium text-slate-200 bg-slate-800 hover:bg-slate-700 transition-colors"
                          data-testid={`open-skin-${skin.id}`}
                        >
                          <ExternalLink size={12} />
                          Open source
                        </button>
                      ) : skin.installed &&
                        skin.install_action === "create_video_skin" ? (
                        <span className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs text-emerald-400 bg-emerald-500/5 border border-emerald-500/10">
                          <Check size={12} />
                          Installed — select in Mixxx Preferences
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => void handleAction(skin)}
                          disabled={
                            installing === skin.id ||
                            (skin.install_action === "create_video_skin" && !videoSkinsOk)
                          }
                          className="flex items-center justify-center gap-1.5 w-full px-3 py-1.5 rounded-lg text-xs font-medium text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-wait transition-colors"
                          data-testid={`install-skin-${skin.id}`}
                        >
                          {installing === skin.id ? (
                            <>
                              <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                              Working...
                            </>
                          ) : skin.install_action === "create_video_skin" ? (
                            <>
                              <Download size={12} />
                              Install Mixxxxx Video
                            </>
                          ) : skin.install_action === "preferences" ? (
                            <>
                              <Check size={12} />
                              Use bundled skin
                            </>
                          ) : (
                            <>
                              <Download size={12} />
                              Install info
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {!loading && !error && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500">
              <Palette size={40} className="mb-3 opacity-30" />
              <p className="text-sm">No skins match your filters</p>
              <button
                type="button"
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
      </div>
    </div>
  );
}
