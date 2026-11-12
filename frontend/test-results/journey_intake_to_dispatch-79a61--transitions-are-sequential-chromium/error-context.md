# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journey_intake_to_dispatch.spec.ts >> Journey: Intake to Dispatch (IT-Service Success Flow) >> verifies workflow state transitions are sequential
- Location: e2e/journey_intake_to_dispatch.spec.ts:272:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/intake_normalized|normalized/i)
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByText(/intake_normalized|normalized/i) with timeout 5000ms
  - waiting for getByText(/intake_normalized|normalized/i)

```

```yaml
- heading "DT IT Procurement" [level=2]
- paragraph: Sign in to your account
- text: Email address
- textbox "Email address"
- text: Password
- textbox "Password"
- button "Sign in"
- paragraph: "Development credentials:"
- paragraph: admin@example.com / admin123
```

# Test source

```ts
  181 |     
  182 |     // Workflow stepper should show completion
  183 |     await expect(stepper).toBeVisible()
  184 |   })
  185 | 
  186 |   test('verifies workflow events and audit logs are created', async ({ page }) => {
  187 |     // This test verifies that audit trail is maintained throughout the journey
  188 |     // by checking workflow_event and audit_log records via API
  189 |     
  190 |     const caseId = 1 // CASE-2026-00001
  191 |     
  192 |     // Navigate to case overview
  193 |     await page.goto(`/cases/${caseId}`)
  194 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  195 |     
  196 |     // Intercept API calls to verify audit endpoints are called
  197 |     // Note: These variables track API calls for future audit verification
  198 |     // let workflowEventsCalled = false
  199 |     // let auditLogsCalled = false
  200 |     
  201 |     page.on('response', async (response) => {
  202 |       const url = response.url()
  203 |       if (url.includes('/workflow-events')) {
  204 |         // workflowEventsCalled = true
  205 |       }
  206 |       if (url.includes('/audit')) {
  207 |         // auditLogsCalled = true
  208 |       }
  209 |     })
  210 |     
  211 |     // Trigger an action that should create audit records
  212 |     // (e.g., navigate to extraction review)
  213 |     await page.goto(`/cases/${caseId}/extraction-review`)
  214 |     
  215 |     await page.waitForTimeout(2000)
  216 |     
  217 |     // Note: In a real implementation, we would:
  218 |     // 1. Make API call to GET /api/v1/cases/{caseId}/workflow-events
  219 |     // 2. Verify workflow_event records exist for state transitions
  220 |     // 3. Make API call to GET /api/v1/cases/{caseId}/audit-logs
  221 |     // 4. Verify audit_log records exist for review decisions
  222 |     
  223 |     // For this test, we verify the pages load correctly as a proxy for backend functionality
  224 |     await expect(page.getByRole('heading', { name: /extraction review/i })).toBeVisible()
  225 |   })
  226 | 
  227 |   test('verifies data persistence across workflow stages', async ({ page }) => {
  228 |     // This test verifies that data persisted in one stage is available in later stages
  229 |     
  230 |     const caseId = 1 // CASE-2026-00001
  231 |     
  232 |     // Navigate to case overview
  233 |     await page.goto(`/cases/${caseId}`)
  234 |     
  235 |     // Capture case number
  236 |     const caseNumber = await page.getByText('CASE-2026-00001').textContent()
  237 |     expect(caseNumber).toContain('CASE-2026-00001')
  238 |     
  239 |     // Navigate to extraction review
  240 |     await page.goto(`/cases/${caseId}/extraction-review`)
  241 |     
  242 |     // Verify case number is still displayed
  243 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  244 |     
  245 |     // Navigate to classification review
  246 |     await page.goto(`/cases/${caseId}/classification-review`)
  247 |     
  248 |     // Verify case number is still displayed
  249 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  250 |     
  251 |     // Navigate to evidence mapping
  252 |     await page.goto(`/cases/${caseId}/evidence-mapping`)
  253 |     
  254 |     // Verify case number and evidence are displayed
  255 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  256 |     await expect(page.getByText(/SUP-CLOUD-001|CloudTech/i)).toBeVisible()
  257 |     
  258 |     // Navigate to longlist adjustments
  259 |     await page.goto(`/cases/${caseId}/longlist-adjustments`)
  260 |     
  261 |     // Verify case number and supplier from evidence are in longlist
  262 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  263 |     await expect(page.getByText(/SUP-CLOUD-001|CloudTech/i)).toBeVisible()
  264 |     
  265 |     // Navigate to lock/dispatch
  266 |     await page.goto(`/cases/${caseId}/lock-dispatch`)
  267 |     
  268 |     // Verify case number and finalized data are displayed
  269 |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  270 |   })
  271 | 
  272 |   test('verifies workflow state transitions are sequential', async ({ page }) => {
  273 |     // This test verifies that workflow states progress in correct order
  274 |     
  275 |     const caseId = 2 // CASE-2026-00002 (also intake_normalized)
  276 |     
  277 |     // Navigate to case overview
  278 |     await page.goto(`/cases/${caseId}`)
  279 |     
  280 |     // Initial state should be intake_normalized
> 281 |     await expect(page.getByText(/intake_normalized|normalized/i)).toBeVisible()
      |                                                                   ^ Error: expect(locator).toBeVisible() failed
  282 |     
  283 |     // After extraction approval, should transition to classification_pending
  284 |     await page.goto(`/cases/${caseId}/extraction-review`)
  285 |     const approveButton = page.getByRole('button', { name: /approve as is|approve/i })
  286 |     if (await approveButton.isVisible()) {
  287 |       await approveButton.click()
  288 |       await page.waitForURL(/\/cases\/2$/, { timeout: 10000 })
  289 |       await page.waitForTimeout(1000)
  290 |       
  291 |       // Reload to get updated state
  292 |       await page.reload()
  293 |       
  294 |       // State should have progressed
  295 |       // (Exact state depends on backend orchestration)
  296 |     }
  297 |   })
  298 | })
  299 | 
```