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

test.describe('grid preferences persistence smoke', () => {
  test('user preference survives logout/login cycle', async ({ page }) => {
    await loginAsAdmin(page);
    const request = page.context().request;

    await api(request, '/api/users/me/grid-preferences/customers-list', {
      method: 'PUT',
      data: {
        state: {
          pageSize: 50,
          columnState: [{ colId: 'full_name', hide: false, pinned: 'left' }],
        },
      },
    });

    await api(request, '/api/auth/logout', { method: 'POST' });
    await loginAsAdmin(page);

    const loaded = await api<{ table_key: string; state: { pageSize: number } }>(
      request,
      '/api/users/me/grid-preferences/customers-list',
      { method: 'GET' },
    );
    expect(loaded.table_key).toBe('customers-list');
    expect(loaded.state.pageSize).toBe(50);
  });
});
