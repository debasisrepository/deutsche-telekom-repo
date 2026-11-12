import { test, expect } from './_pipeline_guard'

test.describe('Wireframe 06 - Evidence and Panel Mapping Page', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/')
    
    // Login with seed credentials
    await page.fill('input[name="email"]', 'admin@example.com')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // Wait for navigation to complete
    await page.waitForURL('/')
  })

  test('should display evidence and mapping page', async ({ page }) => {
    // Navigate to evidence mapping page for case 1 (seeded with evidence and mapping)
    await page.goto('/cases/1/evidence-mapping')
    
    // Wait for main content to load
    const mainContent = page.locator('main#main-content')
    await expect(mainContent).toBeVisible()
    
    // Verify page heading
    const heading = mainContent.locator('h1')
    await expect(heading).toBeVisible()
    await expect(heading).toContainText('Historical supplier evidence')
  })

  test('should display workflow stepper', async ({ page }) => {
    await page.goto('/cases/1/evidence-mapping')
    
    // Wait for page to load
    await page.waitForSelector('main#main-content')
    
    // Find the workflow stepper
    const stepper = page.locator('ol[aria-label="Case progress"]')
    await expect(stepper).toBeVisible()
    
    // Verify steps are present
    const steps = stepper.locator('li')
    await expect(steps.first()).toBeVisible()
  })

  test('should display case banner', async ({ page }) => {
    await page.goto('/cases/1/evidence-mapping')
    
    // Wait for page to load
    await page.waitForSelector('main#main-content')
    
    // Scope banner query to main content
    const mainContent = page.locator('main#main-content')
    const banner = mainContent.locator('dl').first()
    await expect(banner).toBeVisible()
    
    // Verify banner contains case info
    await expect(banner).toContainText('Case ID')
    await expect(banner).toContainText('Current state')
  })

  test('should display evidence section', async ({ page }) => {
    await page.goto('/cases/1/evidence-mapping')
    
    // Wait for page to load
    await page.waitForSelector('main#main-content')
    
    const mainContent = page.locator('main#main-content')
    
    // Find sections
    const sections = mainContent.locator('section')
    await expect(sections.first()).toBeVisible()
  })

  test('should display generate longlist button', async ({ page }) => {
    await page.goto('/cases/1/evidence-mapping')
    
    // Wait for page to load
    await page.waitForSelector('main#main-content')
    
    const mainContent = page.locator('main#main-content')
    
    // Find the action button - use Button component text
    const button = mainContent.locator('button', { hasText: 'Generate ranked longlist proposal' })
    await expect(button).toBeVisible()
    await expect(button).toBeEnabled()
  })
})
