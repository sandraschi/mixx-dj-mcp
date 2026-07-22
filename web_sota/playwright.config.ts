import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: "http://localhost:11117",
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: {
    command: `uv run python -m mixx_dj_mcp.server --port 11116 --host 127.0.0.1`,
    port: 11116,
    cwd: "../",
    timeout: 30000,
    reuseExistingServer: false,
  },
});
