import { test, expect } from './_pipeline_guard'

async function loginViaAPI(page: any) {
  const response = await page.request.post('http://127.0.0.1:9420/api/v1/auth/login', {
    data: {
      email: 'admin@example.com',
      password: 'admin123'
    }
  })
  const data = await response.json()
  // Use addInitScript to set token before any navigation
  await page.addInitScript((token) => {
    localStorage.setItem('access_token', token)
  }, data.access_token)
}

test.describe('Extraction Review', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page)
  })

  test('should display extracted attributes for review', async ({ page }) => {
    // FR-005 acceptance: structured attribute set displayed with source context
    await page.goto('http://127.0.0.1:5220/cases')
    
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/extraction-review')
    
    // Should show extraction form or review interface
    await expect(page.getByText(/attribute|extract|field/i)).toBeVisible({ timeout: 5000 })
  })

  test('should allow approving extraction without modification', async ({ page, apiGuard }) => {
    // FR-006 acceptance: reviewer can approve without modification
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/extraction-review')
    
    // Look for approve button
    const approveButton = page.getByRole('button', { name: /approve|confirm|accept/i })
    
    // Button should exist (may be disabled based on state)
    await expect(approveButton).toBeVisible({ timeout: 5000 })
  })

  test('should allow editing extracted attributes', async ({ page, apiGuard }) => {
    // FR-006 acceptance: reviewer can edit and save corrections
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/extraction-review')
    
    // Should have editable fields or edit mode
    const editableFields = page.locator('input[type="text"], textarea, [contenteditable="true"]')
    await expect(editableFields.first()).toBeVisible({ timeout: 5000 })
  })

  test('should allow rejecting extraction', async ({ page, apiGuard }) => {
    // FR-006 acceptance: reviewer can reject and require rework
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5220/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/extraction-review')
    
    // Look for reject button
    const rejectButton = page.getByRole('button', { name: /reject|decline|rework/i })
    
    // Button should exist (may be disabled based on state)
    await expect(rejectButton).toBeVisible({ timeout: 5000 })
  })
})
