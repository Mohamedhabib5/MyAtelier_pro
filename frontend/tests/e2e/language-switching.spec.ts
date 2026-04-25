import { expect, test } from '@playwright/test';

test.describe('language switching', () => {
  test('guest login language and session language switch work', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');

    await page.locator('[aria-label="language switcher"]').getByRole('combobox').click();
    await page.getByRole('option', { name: 'English' }).click();

    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('body')).toContainText('Dashboard');

    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('body')).toContainText('Dashboard');

    await page.locator('[aria-label="language switcher"]').getByRole('combobox').click();
    await page.getByRole('option', { name: 'العربية' }).click();

    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.locator('body')).toContainText('الرئيسية');
  });
});
