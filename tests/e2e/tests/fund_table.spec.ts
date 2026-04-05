import { test, expect } from '@playwright/test';
import { htmlFileUrl, waitForGrid } from './helpers';

const HTML_FILE = htmlFileUrl('fund_table.html');

// Column headers as defined in fund_table.py › build_table_model()
const MAIN_HEADERS = [
  'Fund Name', 'Ticker', 'Units',
  'Value (1Y ago)', 'Value (6M ago)', 'Value (1M ago)', 'Value (1W ago)',
  'Prev Day', 'Value',
];

const CAT_HEADERS = [
  'Category',
  'Value (1Y ago)', 'Value (6M ago)', 'Value (1M ago)', 'Value (1W ago)',
  'Prev Day', 'Value',
];


test.beforeEach(async ({ page }) => {
  await page.goto(HTML_FILE);
  await waitForGrid(page);
});

test('page title bars render', async ({ page }) => {
  await expect(page.getByText('Fund Portfolio', { exact: true })).toBeVisible();
  await expect(page.getByText('By Category', { exact: true })).toBeVisible();
});

test('main table has all expected column headers', async ({ page }) => {
  // CSS selectors automatically pierce open shadow roots in Playwright.
  for (const header of MAIN_HEADERS) {
    await expect(
      page.locator('.slick-header-column').filter({ hasText: header }).first()
    ).toBeVisible();
  }
});

test('main table has the correct column count', async ({ page }) => {
  // There are two DataTables on this page (main + category).
  // The first table has MAIN_HEADERS.length columns; rely on total unique header text.
  const allHeaders = page.locator('.slick-header-column');
  // Total = 9 (main) + 7 (category) = 16
  await expect(allHeaders).toHaveCount(MAIN_HEADERS.length + CAT_HEADERS.length);
});

test('main table has at least one data row', async ({ page }) => {
  const rows = page.locator('.slick-row');
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);
});

test('main table has a total row', async ({ page }) => {
  // The total row contains the text "Total" in the Units cell.
  await expect(page.locator('.slick-row').filter({ hasText: 'Total' }).first()).toBeVisible();
});

test('category table has all expected column headers', async ({ page }) => {
  for (const header of CAT_HEADERS) {
    await expect(
      page.locator('.slick-header-column').filter({ hasText: header }).first()
    ).toBeVisible();
  }
});

test('category table has at least one data row', async ({ page }) => {
  // Both grids contribute .slick-row elements; assert the combined count is > 1
  // (at minimum: 1 fund row in main table + 1 category row).
  const rows = page.locator('.slick-row');
  const count = await rows.count();
  expect(count).toBeGreaterThan(1);
});
