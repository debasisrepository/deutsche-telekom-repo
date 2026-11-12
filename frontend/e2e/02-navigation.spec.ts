import { test, expect } from './_pipeline_guard'

// Helper to login before each test
test.beforeEach(async ({ page }) => {
  await page.goto('http://127.0.0.1:5220/login')
  await page.getByLabel(/email/i).fill('admin@example.com')
  await page.getByLabel(/password/i).fill('admin123')
  await page.getByRole('button', { name: /log in|sign in|submit/i }).click()
  await expect(page).not.toHaveURL(/.*login/, { timeout: 10000 })
})

test.describe('Navigation - All Routes', () => {
  test('should display intake queue page', async ({ page }) => {
    // FR-003 acceptance: newly created cases appear in work queue
    await page.goto('http://127.0.0.1:5220/')
    await expect(page.getByRole('heading', { name: /intake queue/i })).toBeVisible()
  })

  test('should display cases list page', async ({ page }) => {
    // FR-001, FR-003 acceptance: users can find created cases
    await page.goto('http://127.0.0.1:5220/cases')
    await expect(page.getByRole('heading', { name: /cases|all cases/i })).toBeVisible()
    
    // Should show at least one case from seed data
    await expect(page.getByText(/CASE-2026-/)).toBeVisible({ timeout: 5000 })
  })

  test('should navigate to case overview page', async ({ page }) => {
    // FR-001 acceptance: users can open created case and view source artifact
    await page.goto('http://127.0.0.1:5220/cases')
    
    // Click on first case
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Should show case overview
    await expect(page).toHaveURL(/\/cases\/[a-f0-9-]+$/)
    await expect(page.getByRole('heading', { name: /case overview|case detail/i })).toBeVisible()
  })

  test('should navigate to extraction review page', async ({ page }) => {
    // FR-005, FR-006 acceptance: extraction review interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to extraction review
    await page.goto(page.url() + '/extraction-review')
    await expect(page.getByRole('heading', { name: /extraction review|attribute extraction/i })).toBeVisible()
  })

  test('should navigate to classification review page', async ({ page }) => {
    // FR-007, FR-008 acceptance: classification review interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to classification review
    await page.goto(page.url() + '/classification-review')
    await expect(page.getByRole('heading', { name: /classification review|classification decision/i })).toBeVisible()
  })

  test('should navigate to VMS routing page', async ({ page }) => {
    // FR-010 acceptance: VMS handoff interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to VMS routing
    await page.goto(page.url() + '/vms-routing')
    await expect(page.getByRole('heading', { name: /vms routing|vendor management system/i })).toBeVisible()
  })

  test('should navigate to evidence mapping page', async ({ page }) => {
    // FR-011, FR-012 acceptance: evidence retrieval and mapping interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to evidence mapping
    await page.goto(page.url() + '/evidence-mapping')
    await expect(page.getByRole('heading', { name: /evidence.*mapping|panel mapping/i })).toBeVisible()
  })

  test('should navigate to longlist adjustments page', async ({ page }) => {
    // FR-016, FR-017, FR-020, FR-021 acceptance: longlist management interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to longlist adjustments
    await page.goto(page.url() + '/longlist-adjustments')
    await expect(page.getByRole('heading', { name: /longlist.*adjustment|supplier.*adjustment/i })).toBeVisible()
  })

  test('should navigate to lock and dispatch page', async ({ page }) => {
    // FR-024, FR-026 acceptance: lock and dispatch interface
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to lock and dispatch
    await page.goto(page.url() + '/lock-dispatch')
    await expect(page.getByRole('heading', { name: /lock.*dispatch|tender dispatch/i })).toBeVisible()
  })
})
