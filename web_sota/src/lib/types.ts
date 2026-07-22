export interface PlexMediaItem {
  id: string;
  title: string;
  year: number;
  duration: number;
  type: "movie" | "episode" | "clip";
}

export interface SFXSound {
  id: number;
  name: string;
  duration: number;
  tags: string[];
  preview_url: string;
  license: string;
}

export interface CockpitMessage {
  role: "user" | "assistant";
  content: string;
}
