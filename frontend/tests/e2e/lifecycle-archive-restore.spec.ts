import { expect, test, type APIRequestContext, type Page } from '@playwright/test';

const frontendOrigin = process.env.PLAYWRIGHT_FRONTEND_ORIGIN ?? 'http://127.0.0.1:5173';

async function api<T>(request: APIRequestContext, path: string, init?: Parameters<APIRequestContext['fetch']>[1]): Promise<T> {
  const response = await request.fetch(`${frontendOrigin}${path}`, init);
  const body = await response.text();
  expect(response.ok(), `${path} -> ${response.status()} -> ${body}`).toBeTruthy();
  return body ? (JSON.parse(body) as T) : (undefined as T);
}

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

test.describe('archive and restore lifecycle smoke', () => {
  test('customers table supports archive, inactive filter, and restore', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToEnglish(page);

    const runId = `${Date.now()}`;
    const customer = await api<{ id: string; full_name: string }>(page.context().request, '/api/customers', {
      method: 'POST',
      data: { full_name: `Lifecycle ${runId}`, phone: `01${runId.slice(-9)}` },
    });

    await page.goto('/customers');
    await expect(page.locator('main')).toContainText('Customers');

    await api(page.context().request, `/api/customers/${customer.id}/archive`, {
      method: 'POST',
      data: { reason: 'Archive in smoke test' },
    });

    await page.getByLabel('Status').first().selectOption('inactive');
    const inactiveRow = page.locator('.ag-row').filter({ hasText: customer.full_name }).first();
    await expect(inactiveRow).toBeVisible();

    await api(page.context().request, `/api/customers/${customer.id}/restore`, {
      method: 'POST',
      data: { reason: 'Restore in smoke test' },
    });

    await page.getByLabel('Status').first().selectOption('active');
    await expect(page.locator('main')).toContainText(customer.full_name);
  });
});
