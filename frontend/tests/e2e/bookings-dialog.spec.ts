import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe('bookings dialog', () => {
  test('create booking opens and closes in a popup dialog', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await loginAsAdmin(page);

    await page.goto('/bookings');
    const createButton = page.locator('main button').filter({ hasText: /إنشاء وثيقة حجز|Create booking document/ }).first();
    await createButton.evaluate((el: HTMLButtonElement) => el.click());
    await expect(page.getByText(/محرر وثيقة الحجز|Booking document editor/)).toBeVisible();

    await page.getByRole('button', { name: /إلغاء|Cancel/ }).first().evaluate((el: HTMLButtonElement) => el.click());
    await expect(page.getByText(/محرر وثيقة الحجز|Booking document editor/)).toHaveCount(0);
  });
});
