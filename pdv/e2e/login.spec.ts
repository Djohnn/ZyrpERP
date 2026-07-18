import { test, expect } from './fixtures';
import { LoginPage } from './pages/login.page';

test.describe('Login page', () => {
  test('renders login form with all elements', async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.expectVisible();
    await expect(loginPage.helpLink).toBeVisible();
  });

  test('shows error on invalid API key', async ({ page }) => {
    await page.route('**/api/v1/devices/validate/**', async (route) => {
      await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'API key inv\u00E1lida' }) });
    });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('fail-key');
    await loginPage.expectError('API key inv\u00E1lida');
  });

  test('navigates to dashboard on successful login', async ({ page }) => {
    await page.route('**/api/v1/devices/validate/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ token: 'x', refresh_token: 'y', device_id: 'd', branch_id: 'b' }) });
    });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('valid-key');
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 5000 });
  });

  test('redirects to dashboard within 6 seconds', async ({ page }) => {
    await page.route('**/api/v1/devices/validate/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ token: 'x', refresh_token: 'y', device_id: 'd', branch_id: 'b' }) });
    });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('valid-key');
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 6000 });
  });
});

test.describe('Dashboard (authenticated)', () => {
  test('shows dashboard heading', async ({ authedPage }) => {
    await expect(authedPage.getByText(/dashboard/i).first()).toBeVisible();
  });

  test('shows sync indicator', async ({ authedPage }) => {
    const indicator = authedPage.locator('button').filter({ hasText: /Online|Offline|Sincronizando/ });
    await expect(indicator.first()).toBeVisible();
  });
});
