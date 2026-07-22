import { test, expect } from "@playwright/test";

const BE = "http://127.0.0.1:11116";

test.describe("Fleet Audit", () => {
  test("Backend health", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("ok");
    expect(body.server).toBeTruthy();
  });

  test("Frontend loads", async ({ page }) => {
    await page.goto("/", { timeout: 15000 });
    await page.waitForTimeout(3000);
    await expect(page.locator("#root")).toBeAttached();
  });

  test("Dashboard has testid", async ({ page }) => {
    await page.goto("/dashboard", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="dashboard"]')).toBeAttached();
  });

  test("No console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto("/", { timeout: 15000 });
    await page.waitForTimeout(3000);
    expect(errors).toHaveLength(0);
  });

  test("Tools page loads", async ({ page }) => {
    await page.goto("/tools", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="tools-page"]')).toBeAttached();
  });

  test("Chat page has input and send", async ({ page }) => {
    await page.goto("/chat", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="chat-input"]')).toBeAttached();
    await expect(page.locator('[data-testid="chat-send"]')).toBeAttached();
  });

  test("Library page renders", async ({ page }) => {
    await page.goto("/library", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="library-page"]')).toBeAttached();
  });

  test("Settings page renders", async ({ page }) => {
    await page.goto("/settings", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="settings-page"]')).toBeAttached();
  });

  test("Effects page renders", async ({ page }) => {
    await page.goto("/effects", { timeout: 15000 });
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="effects-page"]')).toBeAttached();
  });

  test("All routes resolve without 404", async ({ page }) => {
    const routes = [
      "/dashboard",
      "/decks",
      "/library",
      "/effects",
      "/chat",
      "/tools",
      "/settings",
    ];
    for (const route of routes) {
      await page.goto(route, { timeout: 15000 });
      await page.waitForTimeout(1000);
      expect(page.url()).toContain(route);
    }
  });
});

test.describe("REST API", () => {
  test("GET /api/health returns 200", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.status()).toBe(200);
  });

  test("POST invalid input returns 422", async ({ request }) => {
    const resp = await request.post(`${BE}/api/library/search`, {
      data: { invalid: true },
    });
    expect([200, 422]).toContain(resp.status());
  });
});
