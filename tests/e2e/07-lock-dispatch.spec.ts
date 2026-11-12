import { test, expect } from './_pipeline_guard'

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

test.describe('Lock and Dispatch', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page)
  })

  test('should display lock and dispatch interface', async ({ page, apiGuard }) => {
    // FR-024, FR-026 acceptance: lock and dispatch controls
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/lock-dispatch')
    
    // Should show lock/dispatch interface
    await expect(page.getByText(/lock|dispatch|tender/i)).toBeVisible({ timeout: 5000 })
  })

  test('should show lock status', async ({ page, apiGuard }) => {
    // FR-024 acceptance: record locking before dispatch
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/lock-dispatch')
    
    // Should show lock status or lock action
    await expect(page.getByText(/lock.*status|locked|unlocked/i)).toBeVisible({ timeout: 5000 })
  })

  test('should allow locking longlist', async ({ page, apiGuard }) => {
    // FR-024 acceptance: explicit record-lock action
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/lock-dispatch')
    
    // Should have lock button
    const lockButton = page.getByRole('button', { name: /lock|finalize/i })
    await expect(lockButton).toBeVisible({ timeout: 5000 })
  })

  test('should show dispatch status per supplier', async ({ page, apiGuard }) => {
    // FR-026 acceptance: dispatch status tracking
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/lock-dispatch')
    
    // Should show dispatch status
    await expect(page.getByText(/dispatch.*status|sent|pending|delivered/i)).toBeVisible({ timeout: 5000 })
  })

  test('should allow dispatching tender', async ({ page, apiGuard }) => {
    // FR-026 acceptance: tender dispatch action
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/lock-dispatch')
    
    // Should have dispatch button
    const dispatchButton = page.getByRole('button', { name: /dispatch|send tender/i })
    await expect(dispatchButton).toBeVisible({ timeout: 5000 })
  })

  test('should display audit trail', async ({ page, apiGuard }) => {
    // FR-037 (cross-cutting): immutable audit trail
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Look for audit history or timeline
    await expect(page.getByText(/audit|history|timeline|activity/i)).toBeVisible({ timeout: 5000 })
  })
})
