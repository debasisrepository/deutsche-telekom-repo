import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 01: Need intake monitoring', () => {
  test('logs in and views need intake page', async ({ page, apiGuard }) => {
    // Log in through login form with seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'procurement.reviewer@telekom.de');
    await page.fill('input[type="password"]', 'Review-pass-1');
    await page.click('button[type="submit"]');

    // Wait for navigation away from login
    await page.waitForURL((url) => !url.pathname.includes('/login'));

    // Navigate to intake page
    await page.goto('/intake');
    await page.waitForLoadState('networkidle');

    // Verify page heading is visible
    await expect(page.getByRole('heading', { name: /need intake/i })).toBeVisible();
    
    // Verify key sections are present
    await expect(page.getByRole('heading', { name: /inbound submissions/i })).toBeVisible();
  });
});
