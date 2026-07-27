const API_BASE = "http://127.0.0.1:11116";

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`GET ${path} ${r.status}: ${body}`);
  }
  return r.json();
}

export async function apiPost<T = unknown>(
  path: string,
  body?: unknown
): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`POST ${path} ${r.status}: ${text}`);
  }
  return r.json();
}

export interface HealthResponse {
  status: string;
  server: string;
  version: string;
  uptime_seconds: number;
  tool_count: number;
  providers: Record<string, unknown>;
}

export interface DiagnosticsResponse {
  status: string;
  server: string;
  version: string;
  uptime_seconds: number;
  tool_count: number;
  tools: { name: string; description?: string }[];
  system: Record<string, unknown>;
  errors: string[];
}

export interface DeckStatus {
  id: number;
  playing: boolean;
  bpm: number;
  key: string;
  track_title: string;
  track_artist: string;
  volume: number;
  gain: number;
  sync_enabled: boolean;
  loop_enabled: boolean;
}

export interface DeckStatusResponse {
  decks: DeckStatus[];
  crossfader: number;
}

export interface LibraryItem {
  id: string;
  title: string;
  artist: string;
  bpm: number;
  key: string;
  length: string;
  source?: "plex" | "mixxx";
  rating_key?: string;
  year?: number | null;
  type?: string;
  genres?: string[];
  collections?: string[];
  tags?: string[];
  summary?: string;
  score?: number;
  loadable?: boolean;
}

export interface LibrarySearchFilters {
  query?: string;
  limit?: number;
  mode?: "auto" | "plex" | "mixxx" | "semantic";
  include_mixxx?: boolean;
  library_id?: string;
  media_type?: string;
  genre?: string;
  year?: number;
  min_year?: number;
  max_year?: number;
  collection?: string;
}

export interface PlexLibrary {
  id: string;
  title: string;
  type: string;
}

export interface LibrarySearchResponse {
  results: LibraryItem[];
  total: number;
  message?: string;
  database?: string | null;
  engine?: string | null;
  plex_available?: boolean;
}

export interface PlexLibrariesResponse {
  libraries: PlexLibrary[];
  plex_available: boolean;
}

export interface EffectsResponse {
  success: boolean;
  message?: string;
  data?: Record<string, unknown>;
}

export interface ToolCallResponse {
  success: boolean;
  tool: string;
  result: unknown;
}

export function fetchHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/api/health");
}

export function fetchDiagnostics(): Promise<DiagnosticsResponse> {
  return apiGet<DiagnosticsResponse>("/api/v1/diagnostics");
}

export function fetchDeckStatus(): Promise<DeckStatusResponse> {
  return apiGet<DeckStatusResponse>("/api/deck/status");
}

export function fetchLibrarySearch(
  filters: LibrarySearchFilters
): Promise<LibrarySearchResponse> {
  return apiPost<LibrarySearchResponse>("/api/library/search", filters);
}

export function fetchLibraryQuery(query: string): Promise<LibrarySearchResponse> {
  return fetchLibrarySearch({ query, mode: "auto" });
}

export function fetchPlexLibraries(): Promise<PlexLibrariesResponse> {
  return apiGet<PlexLibrariesResponse>("/api/library/plex/libraries");
}

export function callEffects(
  payload: Record<string, unknown>
): Promise<EffectsResponse> {
  return apiPost<EffectsResponse>("/api/v1/effects", payload);
}

export function callTool(
  name: string,
  arguments_: Record<string, unknown> = {}
): Promise<ToolCallResponse> {
  return apiPost<ToolCallResponse>("/api/v1/tools/call", {
    name,
    arguments: arguments_,
  });
}

export interface LLMProvider {
  name: string;
  port: number;
  status: "detected" | "not_found";
  models: string[];
}

export interface LLMDiscoverResponse {
  providers: LLMProvider[];
}

export function fetchLLMDiscover(): Promise<LLMDiscoverResponse> {
  return apiGet<LLMDiscoverResponse>("/api/llm/discover");
}

export interface NowPlayingDeck {
  id: number;
  playing: boolean;
  bpm: number;
  key: string;
  track_title: string;
  track_artist: string;
  volume: number;
  sync_enabled: boolean;
}

export interface NowPlayingResponse {
  decks: NowPlayingDeck[];
  crossfader: number;
  recording: { name: string; events: number } | null;
  external_sources: string[];
}

export function fetchNowPlaying(): Promise<NowPlayingResponse> {
  return apiGet<NowPlayingResponse>("/api/v1/cockpit/now_playing");
}

export function fetchFleetSources(): Promise<{ sources: Record<string, unknown> }> {
  return apiGet<{ sources: Record<string, unknown> }>("/api/v1/fleet/sources");
}

export function fetchSkills(): Promise<string[]> {
  return apiGet<string[]>("/api/skills");
}

export function fetchSkillContent(name: string): Promise<string> {
  return apiGet<string>(`/api/skills/${encodeURIComponent(name)}`);
}

export { API_BASE };
