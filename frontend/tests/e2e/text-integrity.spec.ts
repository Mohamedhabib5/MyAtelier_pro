import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: /تسجيل الدخول|Sign in/ })).toBeVisible();
  await page.getByRole('button', { name: /تسجيل الدخول|Sign in/ }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe('arabic text integrity', () => {
  test('critical pages render Arabic without placeholder question marks', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');

    await loginAsAdmin(page);

    await page.goto('/users');
    await expect(page.locator('main')).toContainText('إدارة المستخدمين');
    await expect(page.locator('main')).toContainText('قائمة المستخدمين');

    await page.goto('/bookings');
    await expect(page.locator('main')).toContainText('وثائق الحجز');
    await expect(page.locator('main')).toContainText('قائمة وثائق الحجز');
    await expect(page.locator('main')).toContainText('رقم الحجز');
    await expect(page.locator('main')).toContainText('العميل');

    await page.goto('/payments');
    await expect(page.locator('main')).toContainText('سندات الدفع');
    await expect(page.locator('main')).toContainText('قائمة سندات الدفع');
    await expect(page.locator('main')).toContainText('رقم السند');
    await expect(page.locator('main')).toContainText('الإجراءات');

    const criticalTexts = await page.locator('main').allTextContents();
    expect(criticalTexts.join(' ')).not.toContain('???');
  });
});
