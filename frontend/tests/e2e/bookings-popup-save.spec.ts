import { expect, test, type Locator, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

async function clickByEvaluate(locator: Locator) {
  await locator.evaluate((el: HTMLButtonElement) => el.click());
}

test('user flow: open booking popup, edit, save', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await loginAsAdmin(page);

  await page.goto('/bookings');
  const createButton = page.locator('main button').filter({ hasText: /إنشاء وثيقة حجز|Create booking document/ }).first();
  await clickByEvaluate(createButton);
  await expect(page.getByText(/محرر وثيقة الحجز|Booking document editor/)).toBeVisible();

  const dialog = page.getByRole('dialog').last();
  const dateInputs = dialog.locator('input[type="date"]');
  await expect(dateInputs).toHaveCount(2);
  await dateInputs.nth(1).fill('2026-12-20');

  const saveButton = page.getByRole('button', { name: /حفظ الوثيقة|Save document/ }).first();
  const createResponsePromise = page.waitForResponse((response) => response.url().includes('/api/bookings') && response.request().method() === 'POST' && response.ok());
  await clickByEvaluate(saveButton);
  const createResponse = await createResponsePromise;
  const createdDocument = (await createResponse.json()) as { booking_number: string };

  await expect(page.getByText(/محرر وثيقة الحجز|Booking document editor/)).toHaveCount(0);
  expect(createdDocument.booking_number).toMatch(/^BK/);
});
