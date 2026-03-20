import { existsSync } from "node:fs";

import { defineConfig } from "@playwright/test";

function resolveChromiumPath() {
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
  ].filter((value): value is string => Boolean(value));
  return candidates.find((value) => existsSync(value));
}

const executablePath = resolveChromiumPath();

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  workers: 1,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:5173",
    trace: "on-first-retry",
    browserName: "chromium",
    navigationTimeout: 60_000,
    actionTimeout: 15_000,
    launchOptions: executablePath ? { executablePath } : undefined,
  },
  webServer: undefined,
});
