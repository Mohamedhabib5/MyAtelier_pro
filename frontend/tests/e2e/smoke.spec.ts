import { expect, test } from '@playwright/test';

test.describe('foundation smoke', () => {
  test('login page renders and admin can sign in', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('heading', { name: 'مرحبًا بك' })).toBeVisible();
    await page.getByRole('button', { name: 'تسجيل الدخول' }).click();
    await expect(page).not.toHaveURL(/\/login$/);
    await expect(page.locator('body')).toContainText('MyAtelier Pro');
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  });
});
