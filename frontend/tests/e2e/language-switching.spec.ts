import { expect, test } from '@playwright/test';

test.describe('language switching', () => {
  test('guest login language and session language switch work', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.getByRole('heading', { name: 'مرحبًا بك' })).toBeVisible();

    await page.getByTestId('language-switcher-guest').locator('.MuiSelect-select').click();
    await page.getByRole('option', { name: 'English' }).click();

    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).not.toHaveURL(/\/login$/);
    await expect(page.locator('body')).toContainText('MyAtelier Pro');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('body')).toContainText('Dashboard');

    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('body')).toContainText('Dashboard');

    await page.getByTestId('language-switcher-auth').locator('.MuiSelect-select').click();
    await page.getByRole('option', { name: 'العربية' }).click();

    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.locator('body')).toContainText('الرئيسية');
  });
});
