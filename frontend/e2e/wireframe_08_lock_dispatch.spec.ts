import { test, expect } from './_pipeline_guard'

test.describe('Wireframe 08 - Lock and Dispatch', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@example.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/', { timeout: 10000 })
  })

  test('should display lock and dispatch page', async ({ page }) => {
    // Navigate to a locked case (case 2 from seed has locked longlist)
    await page.goto('/cases/2/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Check page heading
    await expect(page.locator('main#main-content h1')).toContainText('Locked longlist')

    // Check workflow stepper exists
    await expect(page.locator('ol[aria-label="Case progress"]')).toBeVisible()
  })

  test('should display locked longlist information', async ({ page }) => {
    await page.goto('/cases/2/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Check locked longlist section
    await expect(page.getByRole('heading', { name: /Locked longlist/i })).toBeVisible()

    // Check case header banner is displayed
    await expect(page.locator('.case-header')).toBeVisible()
  })

  test('should show dispatch button for locked but not dispatched case', async ({ page }) => {
    await page.goto('/cases/2/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Button should be visible if case is locked but not dispatched
    const dispatchButton = page.getByRole('button', { name: /Dispatch tender/i })
    await expect(dispatchButton).toBeVisible()
  })

  test('should display per-supplier dispatch outcomes when dispatched', async ({ page }) => {
    // Navigate to a dispatched case (case 4 from seed has dispatch)
    await page.goto('/cases/4/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Check if dispatch confirmation section exists
    const dispatchHeading = page.getByRole('heading', { name: /Dispatch confirmation/i })
    await expect(dispatchHeading).toBeVisible()
  })

  test('should display dispatch batch reference for dispatched case', async ({ page }) => {
    await page.goto('/cases/4/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Check for batch reference in dispatch confirmation
    await expect(page.locator('.mono')).toBeVisible()
  })

  test('should trigger dispatch when dispatch button clicked', async ({ page }) => {
    await page.goto('/cases/2/lock-dispatch')
    await page.waitForLoadState('networkidle')

    // Find and click dispatch button
    const dispatchButton = page.getByRole('button', { name: /Dispatch tender/i })
    await expect(dispatchButton).toBeVisible()
    await expect(dispatchButton).toBeEnabled()
    
    // Click dispatch button
    await dispatchButton.click()

    // Wait for dispatch to complete
    await page.waitForTimeout(2000)
  })
})
