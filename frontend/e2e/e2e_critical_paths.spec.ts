import { test, expect } from './_pipeline_guard'

test.describe('Critical Path E2E Tests', () => {
  test('Login through form and access all workflow pages', async ({ page, apiGuard }) => {
    // Allow any workflow state responses
    apiGuard.allowFailedState('/api/v1/')
    
    // === TEST 1: Login through form (CRITICAL - FR-001) ===
    await page.goto('http://127.0.0.1:5220/login')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.getByRole('heading', { name: /DT IT Procurement/i })).toBeVisible()
    
    // Fill and submit login form
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Should redirect away from login
    await expect(page).not.toHaveURL(/.*login/, { timeout: 10000 })
    await page.waitForTimeout(2000) // Wait for any redirects to settle
    
    // === TEST 2: Intake Queue Page (FR-003) ===
    await page.goto('http://127.0.0.1:5220/')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 3: Cases List Page (FR-001, FR-003) ===
    await page.goto('http://127.0.0.1:5220/cases')
    await expect(page.getByText(/CASE-2026-/)).toBeVisible({ timeout: 5000 })
    
    // === TEST 4: Case Overview Page (FR-001) ===
    await page.goto('http://127.0.0.1:5220/cases/1')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 5: Extraction Review Page (FR-005, FR-006) ===
    await page.goto('http://127.0.0.1:5220/cases/1/extraction-review')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 6: Classification Review Page (FR-007, FR-008) ===
    await page.goto('http://127.0.0.1:5220/cases/1/classification-review')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 7: VMS Routing Page (FR-010) ===
    await page.goto('http://127.0.0.1:5220/cases/1/vms-routing')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 8: Evidence Mapping Page (FR-011, FR-012) ===
    await page.goto('http://127.0.0.1:5220/cases/1/evidence-mapping')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 9: Longlist Adjustments Page (FR-016, FR-017, FR-020, FR-021) ===
    await page.goto('http://127.0.0.1:5220/cases/1/longlist-adjustments')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
    
    // === TEST 10: Lock and Dispatch Page (FR-024, FR-026) ===
    await page.goto('http://127.0.0.1:5220/cases/1/lock-dispatch')
    await expect(page.locator('body')).not.toContainText(/404|not found/i, { timeout: 5000 })
  })

  test('API endpoints are functional', async ({ request, page }) => {
    // Login to get token
    const loginResponse = await request.post('http://127.0.0.1:9420/api/v1/auth/login', {
      data: {
        email: 'admin@example.com',
        password: 'admin123'
      }
    })
    expect(loginResponse.status()).toBe(200)
    const { access_token } = await loginResponse.json()
    
    // Test cases endpoint
    const casesResponse = await request.get('http://127.0.0.1:9420/api/v1/cases', {
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    })
    expect(casesResponse.status()).toBe(200)
    const casesData = await casesResponse.json()
    expect(casesData.items).toBeDefined()
    expect(casesData.items.length).toBeGreaterThan(0)
    
    // Test case detail endpoint
    const caseDetailResponse = await request.get('http://127.0.0.1:9420/api/v1/cases/1', {
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    })
    expect(caseDetailResponse.status()).toBe(200)
    const caseDetail = await caseDetailResponse.json()
    expect(caseDetail.id).toBe(1)
    expect(caseDetail.case_number).toBeDefined()
  })

  test('Invalid login credentials are rejected', async ({ page, apiGuard }) => {
    apiGuard.allow(401, '/api/v1/auth/login')
    
    await page.goto('http://127.0.0.1:5220/login')
    
    await page.getByLabel(/email/i).fill('admin@example.com')
    await page.getByLabel(/password/i).fill('wrongpassword')
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Should remain on login page
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 })
    
    // Should show error message
    await expect(page.locator('.text-red-800, .text-red-600, [class*="error"]')).toBeVisible({ timeout: 5000 })
  })
})
