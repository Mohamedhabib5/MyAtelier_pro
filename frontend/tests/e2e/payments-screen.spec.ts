import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe('payments screen', () => {
  test('opens payment editor as popup dialog', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await loginAsAdmin(page);

    await page.goto('/payments');
    await expect(page.locator('button[data-payment-create-dialog-button="true"]')).toBeVisible();

    await page.locator('button[data-payment-create-dialog-button="true"]').click();
    const dialog = page.getByRole('dialog').last();
    await expect(dialog).toBeVisible();
    await expect(dialog.locator('input[data-payment-target-search-input="true"]')).toBeVisible();
    await expect(dialog.getByText(/Suggested accounts|عدد الحسابات المقترحة/)).toBeVisible();
    await expect(dialog.locator('.MuiListItemButton-root').first()).toBeVisible();
  });
});
