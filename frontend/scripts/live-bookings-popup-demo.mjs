import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

const OUT_DIR = '/app/test-results/live-demo';

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function run() {
  await ensureDir(OUT_DIR);
  const browser = await chromium.launch({ headless: true, executablePath: '/usr/bin/chromium-browser' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

  await page.goto('http://127.0.0.1:5173/login', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(OUT_DIR, '01-login.png'), fullPage: true });

  await page.locator('button[type="submit"]').click();
  await page.waitForURL(/\/dashboard$/, { timeout: 20000 });
  await page.goto('http://127.0.0.1:5173/bookings', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(OUT_DIR, '02-bookings-page.png'), fullPage: true });

  const createButton = page.locator('main button.MuiButton-contained').first();
  await createButton.evaluate((el) => el.click());

  const bookingDialog = page.locator('[role="dialog"]').first();
  await bookingDialog.waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, '03-popup-open.png'), fullPage: true });

  const dateInputs = bookingDialog.locator('input[type="date"]');
  const dateCount = await dateInputs.count();
  if (dateCount > 0) {
    await dateInputs.nth(dateCount - 1).fill('2026-12-20');
  }

  const saveButton = bookingDialog.locator('button.MuiButton-contained').first();
  await saveButton.click();
  await bookingDialog.waitFor({ state: 'hidden', timeout: 20000 });
  await page.screenshot({ path: path.join(OUT_DIR, '04-after-save.png'), fullPage: true });

  await browser.close();
}

run();
