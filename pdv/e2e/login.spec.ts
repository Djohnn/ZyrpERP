import { test, expect } from '@playwright/test';

test.describe('Login page', () => {
  test('renders login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByText('Zyrp PDV')).toBeVisible();
    await expect(page.getByText('Chave de API')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible();
  });

  test('shows error on invalid API key', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[id="apiKey"]', 'invalid-key');
    await page.click('button[type="submit"]');
    await expect(page.getByText('Erro')).toBeVisible({ timeout: 10000 });
  });
});
