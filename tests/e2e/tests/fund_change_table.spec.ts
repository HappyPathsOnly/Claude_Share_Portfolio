import { test, expect, Page } from '@playwright/test';
import { pathToFileURL } from 'url';
import * as path from 'path';

const HTML_FILE = pathToFileURL(
  path.resolve(__dirname, '../../../fund_change_table.html')
).href;

// Column headers as defined in fund_change_table.py › build_table_model()
const EXPECTED_HEADERS = [
  'Fund Name', 'Ticker', 'Units',
  '1Y Change', '6M Change', '1M Change', '1W Change',
  'Prev Day', 'Value',
];

async function waitForGrid(page: Page): Promise<void> {
  await page.waitForSelector('.slick-viewport', { state: 'visible', timeout: 30_000 });
}

test.beforeEach(async ({ page }) => {
  await page.goto(HTML_FILE);
  await waitForGrid(page);
});

test('page title bar renders', async ({ page }) => {
  await expect(page.getByText('Fund Portfolio', { exact: false })).toBeVisible();
  await expect(page.getByText('Percentage Change', { exact: false })).toBeVisible();
});

test('table has all expected column headers', async ({ page }) => {
  for (const header of EXPECTED_HEADERS) {
    await expect(
      page.locator('.slick-header-column').filter({ hasText: header }).first()
    ).toBeVisible();
  }
});

test('table has the correct column count', async ({ page }) => {
  await expect(page.locator('.slick-header-column')).toHaveCount(EXPECTED_HEADERS.length);
});

test('table has at least one data row', async ({ page }) => {
  const rows = page.locator('.slick-row');
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);
});

test('table has a total row', async ({ page }) => {
  await expect(page.locator('.slick-row').filter({ hasText: 'Total' })).toBeVisible();
});
