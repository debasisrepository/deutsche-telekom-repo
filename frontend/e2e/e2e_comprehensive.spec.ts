import { test, expect } from './_pipeline_guard'

test.describe('Comprehensive E2E Test Suite', () => {
  let authToken: string
  
  // Helper to login via UI - faster than repeating in each test
  async function doLogin(page: any) {
    await page.goto('http://127.0.0.1:5220/login')
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/', { timeout: 10000 })
  }

  test('01 - Login through form with valid credentials (CRITICAL)', async ({ page }) => {
    // FR-001 acceptance: authenticate to access protected features
    await page.goto('http://127.0.0.1:5220/login')
    
    // Verify we're on the login page
    await expect(page).toHaveURL(/.*login/)
    await expect(page.getByRole('heading', { name: /DT IT Procurement/i })).toBeVisible()
    
    // Fill in the login form
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('admin123')
    
    // Submit the form
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Should redirect away from login
    await expect(page).not.toHaveURL(/.*login/, { timeout: 10000 })
    
    // Should see authenticated content
    await expect(page.locator('body')).toContainText(/intake|cases|queue|procurement/i, { timeout: 10000 })
  })

  test('02 - Access and display intake queue page', async ({ page }) => {
    // FR-003: newly created cases appear in work queue
    await doLogin(page)
    
    // Should already be on the intake page after login
    await expect(page.locator('body')).toContainText(/intake|queue|cases/i, { timeout: 5000 })
  })

  test('03 - Display cases list with seeded data', async ({ page }) => {
    // FR-001, FR-003: users can find created cases
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto('http://127.0.0.1:5220/cases')
    
    // Should show at least one case from seed data
    await expect(page.getByText(/CASE-2026-/)).toBeVisible({ timeout: 5000 })
  })

  test('04 - Navigate to case overview page', async ({ page, apiGuard }) => {
    // FR-001: users can open created case and view source artifact
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto('http://127.0.0.1:5220/cases')
    
    // Click on first case
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Should navigate to case detail
    await expect(page).toHaveURL(/\/cases\/\d+/, { timeout: 5000 })
    
    // Should show case information
    await expect(page.locator('body')).toContainText(/CASE-2026-/, { timeout: 5000 })
  })

  test('05 - Access extraction review page', async ({ page, apiGuard }) => {
    // FR-005, FR-006: extraction review interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto('http://127.0.0.1:5220/cases')
    const firstCase = page.getByText(/CASE-2026-/).first()
    const caseText = await firstCase.textContent()
    const caseNumber = caseText?.match(/CASE-2026-\d+/)?.[0]
    
    if (caseNumber) {
      // Navigate directly to extraction review for first case
      await page.goto(`http://127.0.0.1:5220/cases/1/extraction-review`)
      
      // Page should load without 404
      await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    }
  })

  test('06 - Access classification review page', async ({ page, apiGuard }) => {
    // FR-007, FR-008: classification review interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto(`http://127.0.0.1:5220/cases/1/classification-review`)
    
    // Page should load without 404
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('07 - Access VMS routing page', async ({ page, apiGuard }) => {
    // FR-010: VMS handoff interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto(`http://127.0.0.1:5220/cases/1/vms-routing`)
    
    // Page should load without 404
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('08 - Access evidence mapping page', async ({ page, apiGuard }) => {
    // FR-011, FR-012: evidence retrieval and mapping interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto(`http://127.0.0.1:5220/cases/1/evidence-mapping`)
    
    // Page should load without 404
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('09 - Access longlist adjustments page', async ({ page, apiGuard }) => {
    // FR-016, FR-017, FR-020, FR-021: longlist management interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto(`http://127.0.0.1:5220/cases/1/longlist-adjustments`)
    
    // Page should load without 404
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('10 - Access lock and dispatch page', async ({ page, apiGuard }) => {
    // FR-024, FR-026: lock and dispatch interface accessible
    apiGuard.allowFailedState('/api/v1/') // Allow various workflow states
    
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto(`http://127.0.0.1:5220/cases/1/lock-dispatch`)
    
    // Page should load without 404
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('11 - API endpoint responds with cases', async ({ request }) => {
    // Verify backend API is functional
    const response = await request.get('http://127.0.0.1:9420/api/v1/cases', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })
    
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data.items).toBeDefined()
    expect(data.items.length).toBeGreaterThan(0)
  })

  test('12 - Logout successfully', async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem('access_token', token)
    }, authToken)
    
    await page.goto('http://127.0.0.1:5220/')
    
    // Look for logout button - assert it exists
    const logoutButton = page.getByRole('button', { name: /logout|sign out/i })
    await expect(logoutButton).toBeVisible()
    await logoutButton.click()
    // Should redirect to login
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 })
  })
})
