import { expect, test, type APIRequestContext, type Page } from '@playwright/test';

const frontendOrigin = process.env.PLAYWRIGHT_FRONTEND_ORIGIN ?? 'http://127.0.0.1:5173';

type BookingDocument = {
  id: string;
  booking_number: string;
  lines: Array<{ id: string; service_date: string; revenue_journal_entry_number: string | null }>;
};

type PaymentDocument = {
  id: string;
  payment_number: string;
};

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

test.describe('booking and payment document redesign smoke', () => {
  test('multi-line bookings and multi-allocation payments render correctly', async ({ page }) => {
    await loginAsAdmin(page);

    const request = page.context().request;
    const runId = `${Date.now()}`;
    const phone = `01${runId.slice(-9)}`;

    const customer = await api<{ id: string; full_name: string }>(request, '/api/customers', {
      method: 'POST',
      data: { full_name: `Customer ${runId}`, phone },
    });

    const department = await api<{ id: string }>(request, '/api/catalog/departments', {
      method: 'POST',
      data: { code: `dress-${runId.slice(-6)}`, name: `Dress Dept ${runId.slice(-4)}` },
    });

    const service = await api<{ id: string; default_price: number }>(request, '/api/catalog/services', {
      method: 'POST',
      data: { department_id: department.id, name: `Service ${runId.slice(-5)}`, default_price: 700 },
    });

    const dressOne = await api<{ id: string }>(request, '/api/dresses', {
      method: 'POST',
      data: { code: `DR-${runId.slice(-6)}-1`, dress_type: 'Test', status: 'available', description: 'Smoke one' },
    });
    const dressTwo = await api<{ id: string }>(request, '/api/dresses', {
      method: 'POST',
      data: { code: `DR-${runId.slice(-6)}-2`, dress_type: 'Test', status: 'available', description: 'Smoke two' },
    });
    const dressThree = await api<{ id: string }>(request, '/api/dresses', {
      method: 'POST',
      data: { code: `DR-${runId.slice(-6)}-3`, dress_type: 'Test', status: 'available', description: 'Smoke three' },
    });

    const bookingOne = await api<BookingDocument>(request, '/api/bookings', {
      method: 'POST',
      data: {
        customer_id: customer.id,
        booking_date: '2026-03-17',
        notes: 'Playwright smoke booking one',
        lines: [
          {
            department_id: department.id,
            service_id: service.id,
            service_date: '2026-08-10',
            dress_id: dressOne.id,
            suggested_price: service.default_price,
            line_price: 2500,
            initial_payment_amount: 100,
            status: 'confirmed',
          },
          {
            department_id: department.id,
            service_id: service.id,
            service_date: '2026-08-11',
            dress_id: dressTwo.id,
            suggested_price: service.default_price,
            line_price: 3000,
            initial_payment_amount: 150,
            status: 'confirmed',
          },
        ],
      },
    });

    const bookingTwo = await api<BookingDocument>(request, '/api/bookings', {
      method: 'POST',
      data: {
        customer_id: customer.id,
        booking_date: '2026-03-17',
        notes: 'Playwright smoke booking two',
        lines: [
          {
            department_id: department.id,
            service_id: service.id,
            service_date: '2026-08-12',
            dress_id: dressThree.id,
            suggested_price: service.default_price,
            line_price: 1800,
            status: 'confirmed',
          },
        ],
      },
    });

    const extraPayment = await api<PaymentDocument>(request, '/api/payments', {
      method: 'POST',
      data: {
        customer_id: customer.id,
        payment_date: '2026-03-18',
        notes: 'Playwright smoke allocation',
        allocations: [
          { booking_id: bookingOne.id, booking_line_id: bookingOne.lines[0].id, allocated_amount: 200 },
          { booking_id: bookingTwo.id, booking_line_id: bookingTwo.lines[0].id, allocated_amount: 300 },
        ],
      },
    });

    const completedBookingOne = await api<BookingDocument>(request, `/api/bookings/${bookingOne.id}/lines/${bookingOne.lines[0].id}/complete`, {
      method: 'POST',
    });
    const completedLine = completedBookingOne.lines.find((line) => line.id === bookingOne.lines[0].id);
    expect(completedLine?.revenue_journal_entry_number).toBeTruthy();

    await page.goto('/bookings');
    await expect(page.locator('main')).toContainText(/وثائق الحجز|Booking documents/);

    await page.goto('/payments');
    await page.locator('button[data-payment-create-dialog-button="true"]').click();
    const paymentDialog = page.getByRole('dialog').last();
    const targetSearch = paymentDialog.locator('input[data-payment-target-search-input="true"]');
    await targetSearch.fill(customer.full_name);
    await expect.poll(async () => paymentDialog.getByRole('button', { name: new RegExp(customer.full_name) }).count()).toBeGreaterThan(0);
    await paymentDialog.getByRole('button', { name: new RegExp(customer.full_name) }).first().click();
    await expect(paymentDialog).toContainText(bookingOne.booking_number);
    await expect(paymentDialog).toContainText(bookingTwo.booking_number);
    expect(extraPayment.payment_number).toMatch(/^PAY/);

    await page.goto('/reports');
    await expect(page.locator('main')).toContainText(customer.full_name);

    await page.goto('/exports');
    await expect.poll(async () => page.locator('button', { hasText: 'CSV' }).count()).toBeGreaterThanOrEqual(5);
  });
});
