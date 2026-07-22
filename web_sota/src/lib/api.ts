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
}

export interface LibrarySearchResponse {
  results: LibraryItem[];
  total: number;
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

export function fetchLibraryQuery(
  query: string
): Promise<LibrarySearchResponse> {
  return apiPost<LibrarySearchResponse>("/api/library/search", { query });
}

export function fetchSkills(): Promise<string[]> {
  return apiGet<string[]>("/api/skills");
}

export function fetchSkillContent(name: string): Promise<string> {
  return apiGet<string>(`/api/skills/${encodeURIComponent(name)}`);
}

export { API_BASE };
