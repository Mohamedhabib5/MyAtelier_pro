import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

async function switchToEnglish(page: Page) {
  await page.locator('[aria-label="language switcher"]').getByRole('combobox').click();
  await page.getByRole('option', { name: 'English' }).click();
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
}

test.describe('exports center filter-aware links', () => {
  test('bookings CSV includes active export-center filters in query string', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToEnglish(page);
    await page.goto('/exports');

    await page.getByLabel('Search').first().fill('needle');
    await page.getByLabel('Status').first().selectOption('cancelled');
    await page.getByLabel('From').first().fill('2026-08-01');
    await page.getByLabel('To').first().fill('2026-08-31');

    const requestPromise = page.waitForRequest((request) => {
      const url = request.url();
      return (
        url.includes('/api/exports/bookings.csv') &&
        url.includes('search=needle') &&
        url.includes('status=cancelled') &&
        url.includes('date_from=2026-08-01') &&
        url.includes('date_to=2026-08-31')
      );
    });

    await page.getByRole('button', { name: /Download bookings CSV/i }).first().click();
    await requestPromise;
  });

  test('payment allocations CSV includes active export-center payment filters', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToEnglish(page);
    await page.goto('/exports');

    await page.getByLabel('Search').nth(1).fill('pay-needle');
    await page.getByLabel('Status').nth(1).selectOption('voided');
    await page.getByLabel('Kind').first().selectOption('collection');
    await page.getByLabel('From').nth(1).fill('2026-07-01');
    await page.getByLabel('To').nth(1).fill('2026-07-31');

    const requestPromise = page.waitForRequest((request) => {
      const url = request.url();
      return (
        url.includes('/api/exports/payment-allocations.csv') &&
        url.includes('search=pay-needle') &&
        url.includes('status=voided') &&
        url.includes('document_kind=collection') &&
        url.includes('date_from=2026-07-01') &&
        url.includes('date_to=2026-07-31')
      );
    });

    await page.getByRole('button', { name: /Download payment allocations CSV/i }).first().click();
    await requestPromise;
  });
});
