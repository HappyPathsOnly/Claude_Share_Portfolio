import { expect, Page } from '@playwright/test';
import { pathToFileURL } from 'url';
import * as path from 'path';

/** Resolve the URL for an HTML file in the repo root. */
export function htmlFileUrl(filename: string): string {
  return pathToFileURL(path.resolve(__dirname, '../../../', filename)).href;
}

/** Wait for SlickGrid to finish rendering inside the Bokeh shadow DOM. */
export async function waitForGrid(page: Page): Promise<void> {
  await page.waitForSelector('.slick-viewport', { state: 'visible', timeout: 30_000 });
}

export async function waitForChart(page: Page) {
  await expect(page.locator('canvas').first()).toBeVisible({ timeout: 60_000 });
}