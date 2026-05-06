import { expect, test, type Page } from '@playwright/test';

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await page.getByLabel(/username/i).fill('admin');
  await page.getByLabel(/password/i).fill('admin123');
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe('Export Filename Protection', () => {
  test('Bookings XLSX export has a correct human-readable filename', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/bookings');

    // Trigger export
    await page.getByRole('button', { name: /تصدير/i }).click();
    
    // Start waiting for download before clicking
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('menuitem', { name: 'XLSX' }).click();
    const download = await downloadPromise;

    const filename = download.suggestedFilename();
    console.log(`[E2E] Downloaded filename: ${filename}`);

    // VERIFICATION: 
    // 1. Filename should NOT be a UUID (approx 36 chars with dashes)
    // 2. Filename should start with 'bookings'
    // 3. Filename should have .xlsx extension
    expect(filename).toMatch(/^bookings_.*\.xlsx$/);
    expect(filename.length).toBeLessThan(60); // UUID + extension is around 41, but let's be safe
  });

  test('Customers CSV export has a correct human-readable filename', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/customers');

    // Trigger export
    await page.getByRole('button', { name: /تصدير/i }).click();
    
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('menuitem', { name: 'CSV' }).click();
    const download = await downloadPromise;

    const filename = download.suggestedFilename();
    console.log(`[E2E] Downloaded filename: ${filename}`);

    // VERIFICATION:
    expect(filename).toMatch(/^customers.*\.csv$/);
  });
});
