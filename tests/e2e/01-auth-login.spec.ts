import { test, expect } from './_pipeline_guard'

test.describe('Authentication - Login Form Flow', () => {
  test('should login through the form with valid credentials', async ({ page }) => {
    // FR-001 acceptance: authenticate to access protected features
    await page.goto('http://127.0.0.1:5200/login')
    
    // Verify we're on the login page
    await expect(page).toHaveURL(/.*login/)
    await expect(page.getByRole('heading', { name: /login|sign in/i })).toBeVisible()
    
    // Fill in the login form
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('admin123')
    
    // Submit the form
    await page.getByRole('button', { name: /log in|sign in|submit/i }).click()
    
    // Should redirect away from login
    await expect(page).not.toHaveURL(/.*login/, { timeout: 10000 })
    
    // Should see authenticated content (intake queue or cases list)
    await expect(page.getByRole('heading', { name: /intake queue|cases|dashboard/i })).toBeVisible({ timeout: 10000 })
  })

  test('should reject invalid credentials', async ({ page, apiGuard }) => {
    apiGuard.allow(401, '/api/v1/auth/login')
    
    await page.goto('http://127.0.0.1:5200/login')
    
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('wrongpassword')
    
    await page.getByRole('button', { name: /log in|sign in|submit/i }).click()
    
    // Should remain on login page
    await expect(page).toHaveURL(/.*login/)
    
    // Should show error message
    await expect(page.getByText(/invalid|incorrect|failed|wrong/i)).toBeVisible({ timeout: 5000 })
  })

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('http://127.0.0.1:5200/login')
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /log in|sign in|submit/i }).click()
    await expect(page).not.toHaveURL(/.*login/, { timeout: 10000 })
    
    // Logout
    await page.getByRole('button', { name: /logout|sign out/i }).click()
    
    // Should redirect to login
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 })
  })
})
