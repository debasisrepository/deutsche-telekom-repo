import { test, expect } from './_pipeline_guard'

test.describe('Wireframe 02 - Case Overview', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/')
    
    // Check if already logged in by looking for main content
    const isLoggedIn = await page.locator('main#main-content').isVisible().catch(() => false)
    
    if (!isLoggedIn) {
      // Perform login with correct seed credentials
      await page.fill('input[type="email"]', 'admin@example.com')
      await page.fill('input[type="password"]', 'admin123')
      await page.click('button[type="submit"]')
      
      // Wait for navigation to complete
      await page.waitForURL('/')
      await page.waitForTimeout(500)
    }
  })

  test('should display case overview page with case details', async ({ page }) => {
    // Wait for intake queue to load
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })

    // Click on the first case to navigate to overview
    const firstCaseLink = page.locator('table tbody tr a').first()
    await firstCaseLink.click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify we're on a case overview page (URL should contain /cases/)
    await expect(page).toHaveURL(/\/cases\/\d+/)

    // Verify case header exists with case number in the main content area (not the global header)
    const mainContent = page.locator('main#main-content')
    const caseHeading = mainContent.getByRole('heading', { level: 1 })
    await expect(caseHeading).toBeVisible()
    await expect(caseHeading).toContainText('CASE-')
  })

  test('should display workflow progress stepper', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for page to load
    await page.waitForTimeout(1000)

    // Verify the stepper element exists
    const stepper = page.locator('ol[aria-label="Case progress"]')
    await expect(stepper).toBeVisible()

    // Verify key workflow steps are present as text in the stepper
    await expect(stepper.getByText('Intake', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Extraction', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Classification', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Evidence and mapping', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Longlist', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Lock', { exact: true })).toBeVisible()
    await expect(stepper.getByText('Dispatch', { exact: true })).toBeVisible()
  })

  test('should display normalized need record table', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify the normalized need section heading
    await expect(page.getByRole('heading', { name: /normalized need record/i })).toBeVisible()

    // Verify the normalized need table exists
    const needTable = page.locator('table').first()
    await expect(needTable).toBeVisible()

    // Verify table has expected columns
    await expect(page.getByRole('columnheader', { name: 'Field' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Normalized value' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /mapped from/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Origin' })).toBeVisible()
  })

  test('should display completeness progress bar', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify completeness indicator
    await expect(page.getByText(/mandatory fields complete:/i)).toBeVisible()
    
    // Verify progress bar exists
    const progressBar = page.locator('[role="progressbar"]')
    await expect(progressBar).toBeVisible()
  })

  test('should display preserved source artifact section', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify preserved source artifact heading
    await expect(page.getByRole('heading', { name: /preserved source artifact/i })).toBeVisible()

    // Verify case history section
    await expect(page.getByRole('heading', { name: /case history/i })).toBeVisible()
    
    // Verify history items are present
    await expect(page.getByText('Case created')).toBeVisible()
    await expect(page.getByText('Normalized record created')).toBeVisible()
  })

  test('should show action buttons for next steps', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify action buttons exist
    await expect(page.getByRole('button', { name: /open extraction review/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /view source artifact/i })).toBeVisible()
  })

  test('should navigate back to cases list from breadcrumb', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Click breadcrumb link to go back
    await page.getByRole('link', { name: /cases/i }).first().click()

    // Verify we're back on the intake queue page
    await expect(page.getByRole('heading', { name: /need intake and case list/i })).toBeVisible()
  })

  test('should display classification tags correctly', async ({ page }) => {
    // Navigate to a case
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 10000 })
    await page.locator('table tbody tr a').first().click()

    // Wait for case overview to load
    await page.waitForTimeout(1000)

    // Verify that tags are rendered (specific tag types depend on case state)
    const tags = page.locator('.cds--tag')
    const tagCount = await tags.count()
    expect(tagCount).toBeGreaterThan(0)
  })
})
