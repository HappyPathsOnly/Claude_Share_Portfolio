import { test, expect, Page } from '@playwright/test';
import { pathToFileURL } from 'url';
import * as path from 'path';

const HTML_FILE = pathToFileURL(
  path.resolve(__dirname, '../../../fund_chart.html')
).href;

// Period labels as defined in fund_chart.py › PERIODS
const PERIOD_LABELS = ['1M', '3M', '6M', '1Y', '3Y', '5Y', '10Y'];

// The chart embeds all 7 periods of price data (~192 KB), so Bokeh needs more
// time to parse and render than the table pages. Give each test 90 s.
test.setTimeout(90_000);

async function waitForChart(page: Page): Promise<void> {
  // Bokeh renders the plot as a plain <canvas> element (no bk-canvas class in 3.x).
  // Playwright's CSS engine automatically pierces open shadow roots.
  await page.locator('canvas').first().waitFor({ state: 'visible', timeout: 60_000 });
}

test.beforeEach(async ({ page }) => {
  await page.goto(HTML_FILE);
  await waitForChart(page);
});

test('title bar renders with fund name', async ({ page }) => {
  // The title is injected as innerHTML of a Bokeh Div — regular DOM, not shadow DOM.
  await expect(page.getByText(/Dodge/i).first()).toBeVisible();
});

test('all period buttons are present', async ({ page }) => {
  // .bk-btn elements live inside the RadioButtonGroup shadow DOM;
  // Playwright's CSS engine pierces open shadow roots automatically.
  await expect(page.locator('.bk-btn')).toHaveCount(PERIOD_LABELS.length);
});

test('period buttons have the correct labels', async ({ page }) => {
  for (const label of PERIOD_LABELS) {
    await expect(page.locator('.bk-btn').filter({ hasText: label })).toBeVisible();
  }
});

test('chart canvas is rendered', async ({ page }) => {
  await expect(page.locator('canvas').first()).toBeVisible();
});
