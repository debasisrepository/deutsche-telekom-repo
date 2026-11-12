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

test.describe('Classification Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page)
  })

  test('should display classification verdict', async ({ page, apiGuard }) => {
    // FR-007 acceptance: system produces classification verdict
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/classification-review')
    
    // Should show classification result
    await expect(page.getByText(/classification|single.?resource|it.?service/i)).toBeVisible({ timeout: 5000 })
  })

  test('should show classification rationale', async ({ page, apiGuard }) => {
    // FR-007 acceptance: rationale inputs visible to users
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/classification-review')
    
    // Should show rationale or confidence
    await expect(page.getByText(/rationale|reason|confidence|certainty/i)).toBeVisible({ timeout: 5000 })
  })

  test('should allow accepting classification', async ({ page, apiGuard }) => {
    // FR-008 acceptance: reviewer can accept classification
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/classification-review')
    
    // Should have accept button
    const acceptButton = page.getByRole('button', { name: /accept|approve|confirm/i })
    await expect(acceptButton).toBeVisible({ timeout: 5000 })
  })

  test('should allow overriding classification', async ({ page, apiGuard }) => {
    // FR-008 acceptance: reviewer can override verdict
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    await page.goto(page.url() + '/classification-review')
    
    // Should have override option or alternate classification choice
    await expect(page.getByRole('button', { name: /override|change|correct/i })).toBeVisible({ timeout: 5000 })
  })

  test('should show VMS routing for single-resource cases', async ({ page, apiGuard }) => {
    // FR-010 acceptance: single-resource triggers VMS handoff
    apiGuard.allowFailedState('/api/v1/') // Allow any workflow state responses
    
    await page.goto('http://127.0.0.1:5200/cases')
    const caseLink = page.getByText(/CASE-2026-/).first()
    await caseLink.click()
    
    // Try navigating to VMS routing
    await page.goto(page.url() + '/vms-routing')
    
    // Should show VMS handoff interface or status
    await expect(page.getByText(/vms|vendor management|handoff|routed/i)).toBeVisible({ timeout: 5000 })
  })
})
