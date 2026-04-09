import { test, expect, Page } from '@playwright/test';
import { htmlFileUrl } from './helpers';

const HTML_FILE = htmlFileUrl('fund_chart.html');

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

test('title bar renders with fund name and period return', async ({ page }) => {
  // The title Div contains two spans: the fund name and "{period} return: ±X.XX%".
  // Both are regular DOM elements (Bokeh Div), not shadow DOM.
  await expect(page.getByText(/Dodge/i).first()).toBeVisible();

  // Default period is 1Y — the return span should show "1Y return:"
  await expect(page.getByText(/1Y return:/i)).toBeVisible();

  // Click 5Y and confirm the title updates to "5Y return:"
  await page.locator('.bk-btn').filter({ hasText: '5Y' }).click();
  await expect(page.getByText(/5Y return:/i)).toBeVisible();
  // Fund name should still be present
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

test('5Y button switches x-axis to year-only format', async ({ page }) => {
  /**
   * Uses Bokeh's own DatetimeTickFormatter.doFormat() to read the first
   * x-axis tick label for the current range, then checks its format.
   *
   * 1Y view → Bokeh picks the months scale → label like "Sep'25" (starts with a letter)
   * 5Y view → Bokeh picks the years scale  → label like "2025"   (pure 4-digit number)
   */
  const getFirstTickLabel = () =>
    page.evaluate((): string | null => {
      const doc = (window as any).Bokeh?.documents?.[0];
      if (!doc) return null;
      const models: any[] = doc._all_models instanceof Map
        ? Array.from(doc._all_models.values())
        : Object.values(doc._all_models);
      // x-axis timestamps are ms since epoch (~1.7e12 for current dates);
      // y-axis prices are in the hundreds/thousands — far smaller.
      const xRange = models.find(m => m.start > 1e12 && m.end > 1e12);
      // DatetimeTickFormatter has days, months, and years properties
      const formatter = models.find(
        m => m.months !== undefined && m.years !== undefined && m.days !== undefined,
      );
      if (!xRange || !formatter) return null;
      // doFormat needs multiple ticks to compute the interval and pick the right scale.
      // Using [start, mid, end] gives a step of (span/2):
      //   1Y → ~6-month step  → months format ("Sep'25")
      //   5Y → ~2.5-year step → years format  ("2025")
      const mid = (xRange.start + xRange.end) / 2;
      const ticks = [xRange.start, mid, xRange.end];
      const labels: string[] = formatter.doFormat(ticks, { loc: xRange.start });
      return labels?.[0] ?? null;
    });

  // Default period is 1Y: first tick label should start with a month abbreviation
  const label1Y = await getFirstTickLabel();
  expect(label1Y).not.toBeNull();
  expect(label1Y).toMatch(/^[A-Za-z]/); // e.g. "Sep'25"

  // Switch to 5Y
  await page.locator('.bk-btn').filter({ hasText: '5Y' }).click();
  // All period data is pre-embedded in the page; the switch is a pure JS callback.
  // Allow time for Bokeh to apply the new data and re-render.
  await page.waitForTimeout(1500);

  // 5Y: first tick label should be a plain 4-digit year
  const label5Y = await getFirstTickLabel();
  expect(label5Y).not.toBeNull();
  expect(label5Y).toMatch(/^\d{4}$/); // e.g. "2020"
});
