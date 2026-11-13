import { test, expect } from './_pipeline_guard';

test.describe('Smoke Login Test', () => {
  test('should login with seed credentials through the form', async ({ page, apiGuard }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Verify we're on the login page
    await expect(page.locator('h1')).toContainText('Deutsche Telekom');
    
    // Fill in the login form with seed credentials
    await page.fill('input[type="email"]', 'procurement.reviewer@telekom.de');
    await page.fill('input[type="password"]', 'Review-pass-1');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for navigation away from login
    await page.waitForURL((url) => !url.pathname.includes('/login'));
    
    // Verify we're logged in - check for user email or dashboard content
    await expect(page.getByText('procurement.reviewer@telekom.de')).toBeVisible({ timeout: 5000 });
  });
});
