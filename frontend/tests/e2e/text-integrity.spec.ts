import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('heading', { name: 'مرحبًا بك' })).toBeVisible();
  await page.getByRole('button', { name: 'تسجيل الدخول' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
  await expect(page.locator('body')).toContainText('MyAtelier Pro');
}

test.describe('arabic text integrity', () => {
  test('critical pages render Arabic without placeholder question marks', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toContainText('مرحبًا بك');

    await loginAsAdmin(page);
    await page.goto('/users');
    await expect(page.locator('main')).toContainText('إدارة المستخدمين');
    await expect(page.locator('main')).toContainText('قائمة المستخدمين');

    await page.goto('/bookings');
    await expect(page.locator('main')).toContainText('وثائق الحجز');
    await expect(page.locator('main')).toContainText('قائمة وثائق الحجز');
    await expect(page.locator('thead')).toContainText('رقم الحجز');
    await expect(page.locator('thead')).toContainText('العميل');

    await page.goto('/payments');
    await expect(page.locator('main')).toContainText('سندات الدفع');
    await expect(page.locator('main')).toContainText('قائمة سندات الدفع');
    await expect(page.locator('thead')).toContainText('رقم السند');
    await expect(page.locator('thead')).toContainText('الإجراءات');
    const criticalTexts = await page.locator('main h4, main h5, main h6, thead').allTextContents();
    expect(criticalTexts.join(' ')).not.toContain('???');
  });
});
