import { test, expect } from './_pipeline_guard'

test('smoke login flow', async ({ page }) => {
  // Navigate to the application
  await page.goto('/')

  // Should redirect to login page
  await expect(page).toHaveURL(/.*login/)

  // Check login form is present
  await expect(page.getByRole('heading', { name: /DT IT Procurement/i })).toBeVisible()
  
  // Fill in login credentials from seed data
  await page.getByLabel(/email/i).fill('admin@telekom.de')
  await page.getByLabel(/password/i).fill('Admin-pass-123')

  // Submit the form
  await page.getByRole('button', { name: /sign in/i }).click()

  // Wait for navigation to complete
  await page.waitForURL('/')

  // Verify we're logged in by checking for authenticated content
  await expect(page.getByText(/Welcome to DT IT Procurement/i)).toBeVisible()
  
  // Check that header shows user info
  await expect(page.getByText(/admin/i)).toBeVisible()
})
