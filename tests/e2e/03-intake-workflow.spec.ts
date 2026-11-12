import { test, expect } from './_pipeline_guard'

// Helper to login via API
async function loginViaAPI(page: any) {
  const response = await page.request.post('http://127.0.0.1:9100/api/v1/auth/login', {
    data: {
      username: 'admin@example.com',
      password: 'admin123'
    }
  })
  const data = await response.json()
  await page.evaluate((token: string) => {
    localStorage.setItem('token', token)
  }, data.access_token)
}

test.describe('Intake Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page)
  })

  test('should create a new case with RFP upload', async ({ page }) => {
    // FR-001 acceptance: system accepts RFP uploads and assigns unique case ID
    await page.goto('http://127.0.0.1:5200/')
    
    // Look for create case button
    const createButton = page.getByRole('button', { name: /create case|new case|add case/i })
    await expect(createButton).toBeVisible()
    await createButton.click()
    
    // Fill in case details
    await page.getByLabel(/title|name/i).fill('Test Network Infrastructure RFP')
    await page.getByLabel(/description/i).fill('Testing intake for network equipment procurement')
    
    // Select channel type as RFP
    const channelField = page.locator('select, [role="combobox"], [data-testid*="channel"]').first()
    await channelField.selectOption({ label: /rfp|document/i })
    
    // Submit
    await page.getByRole('button', { name: /submit|create|save/i }).click()
    
    // Should redirect to case overview or cases list
    await expect(page).toHaveURL(/\/cases/, { timeout: 10000 })
    
    // New case should appear with CASE-2026- prefix
    await expect(page.getByText(/CASE-2026-/)).toBeVisible({ timeout: 5000 })
  })

  test('should display created case with intake channel preserved', async ({ page }) => {
    // FR-001 acceptance: system stores channel, timestamp, and artifact reference
    await page.goto('http://127.0.0.1:5200/cases')
    
    // Open first case
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Should show case details including channel
    await expect(page.getByText(/channel|source/i)).toBeVisible()
    await expect(page.getByText(/rfp|email|phone|supplier/i)).toBeVisible()
  })

  test('should show case initial status', async ({ page }) => {
    // FR-003 acceptance: case starts in defined initial state
    await page.goto('http://127.0.0.1:5200/cases')
    
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Should display current workflow status
    await expect(page.getByText(/status|state|stage/i)).toBeVisible()
    await expect(page.getByText(/intake|pending|created|normalization/i)).toBeVisible()
  })

  test('should display normalized need attributes', async ({ page }) => {
    // FR-002 acceptance: inbound need transformed into normalized record
    await page.goto('http://127.0.0.1:5200/cases')
    
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Navigate to overview or details section
    // Should show normalized fields
    await expect(page.getByText(/normalized|attributes|fields/i)).toBeVisible({ timeout: 5000 })
  })
})
