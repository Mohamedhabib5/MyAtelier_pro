import { chromium } from '@playwright/test';
import * as path from 'path';

// Target artifact path
const artifactDir = 'C:\\Users\\moham\\.gemini\\antigravity\\brain\\b1e3ee28-070a-4c69-9bbc-61a57d6bffb5';

async function main() {
  console.log('Starting visual review script (optimized)...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'ar-EG',
    colorScheme: 'light',
  });

  const page = await context.newPage();

  // 1. Go to Login Page
  console.log('Navigating to login page...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'load' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(artifactDir, '01_login_page.png') });
  console.log('Saved 01_login_page.png');

  // Fill in correct admin credentials from backend config
  console.log('Filling credentials...');
  await page.locator('input[type="text"]').fill('admin');
  await page.locator('input[type="password"]').fill('iq8oDveLIxbCXVefLDm8dA');
  await page.screenshot({ path: path.join(artifactDir, '02_login_filled.png') });

  // Click login
  console.log('Clicking login...');
  await page.getByRole('button', { name: 'تسجيل الدخول' }).click();
  
  // Wait for navigation
  await page.waitForURL('**/dashboard', { timeout: 15000 });
  console.log('Logged in successfully, landed on dashboard!');
  
  // Let dashboard load completely
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(artifactDir, '03_dashboard.png') });
  console.log('Saved 03_dashboard.png');

  // 2. Go to Accounting Page (contains Chart of Accounts, Journal Entries, Periods)
  console.log('Navigating to Accounting page...');
  await page.goto('http://localhost:5173/accounting', { waitUntil: 'load' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(artifactDir, '04_accounting_page.png') });
  console.log('Saved 04_accounting_page.png');

  // Tab 1: Trial Balance
  console.log('Clicking Trial Balance tab...');
  const trialBalanceTab = page.locator('#accounting-subtab-trial');
  if (await trialBalanceTab.count() > 0) {
    await trialBalanceTab.click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(artifactDir, '07_trial_balance.png') });
    console.log('Saved 07_trial_balance.png');
  }

  // Tab 2: Income Statement
  console.log('Clicking Income Statement tab...');
  const incomeStatementTab = page.locator('#accounting-subtab-income');
  if (await incomeStatementTab.count() > 0) {
    await incomeStatementTab.click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(artifactDir, '08_income_statement.png') });
    console.log('Saved 08_income_statement.png');
  }

  // Tab 3: Aging Reports
  console.log('Clicking Aging Reports tab...');
  const agingTab = page.locator('#accounting-subtab-aging');
  if (await agingTab.count() > 0) {
    await agingTab.click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(artifactDir, '09_aging_reports.png') });
    console.log('Saved 09_aging_reports.png');
  }

  // Tab 4: Cash Reconciliation
  console.log('Clicking Cash Reconciliation tab...');
  const reconciliationTab = page.locator('#accounting-subtab-reconciliation');
  if (await reconciliationTab.count() > 0) {
    await reconciliationTab.click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(artifactDir, '10_reconciliation.png') });
    console.log('Saved 10_reconciliation.png');
  }

  // 3. Go to Financial Settings Page (for fiscal periods and locks)
  console.log('Navigating to General Financial Settings page...');
  await page.goto('http://localhost:5173/settings/general/financial', { waitUntil: 'load' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(artifactDir, '05_accounting_periods.png') });
  console.log('Saved 05_accounting_periods.png');

  // 4. Go to Reports Page
  console.log('Navigating to Reports page...');
  await page.goto('http://localhost:5173/reports', { waitUntil: 'load' });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(artifactDir, '06_reports_dashboard.png') });
  console.log('Saved 06_reports_dashboard.png');

  // Close browser
  await browser.close();
  console.log('All screenshots captured successfully!');
}

main().catch(err => {
  console.error('Error taking screenshots:', err);
  process.exit(1);
});
