import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  // Each test gets up to 60 s; global setup can take several minutes (live data fetch).
  timeout: 60_000,
  retries: 1,

  use: {
    headless: true,
    // Bokeh embeds large JS bundles — allow extra time for the page to boot.
    actionTimeout: 15_000,

    // Keep useful debugging artifacts when a test fails.
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',    
  },

  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
});
