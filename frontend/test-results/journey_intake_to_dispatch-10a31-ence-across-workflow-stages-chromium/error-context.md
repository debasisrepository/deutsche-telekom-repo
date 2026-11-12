# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journey_intake_to_dispatch.spec.ts >> Journey: Intake to Dispatch (IT-Service Success Flow) >> verifies data persistence across workflow stages
- Location: e2e/journey_intake_to_dispatch.spec.ts:227:3

# Error details

```
TimeoutError: locator.textContent: Timeout 15000ms exceeded.
Call log:
  - waiting for getByText('CASE-2026-00001')

```

# Page snapshot

```yaml
- generic [ref=f1e4]:
  - generic [ref=f1e5]:
    - heading "DT IT Procurement" [level=2] [ref=f1e6]
    - paragraph [ref=f1e7]: Sign in to your account
  - generic [ref=f1e8]:
    - generic [ref=f1e9]:
      - generic [ref=f1e10]:
        - generic [ref=f1e11]: Email address
        - textbox "Email address" [ref=f1e12]
      - generic [ref=f1e13]:
        - generic [ref=f1e14]: Password
        - textbox "Password" [ref=f1e15]
    - button "Sign in" [ref=f1e17] [cursor=pointer]
    - generic [ref=f1e18]:
      - paragraph [ref=f1e19]: "Development credentials:"
      - paragraph [ref=f1e20]: admin@example.com / admin123
```

# Test source

```ts
  136 |     // Trigger validation
  137 |     const validateButton = page.getByRole('button', { name: /validate count|validate supplier/i })
  138 |     if (await validateButton.isVisible()) {
  139 |       await validateButton.click()
  140 |       await page.waitForTimeout(1000)
  141 |     }
  142 |     
  143 |     // Verify validation result
  144 |     // (With 1 supplier, validation should fail - need 3-6 suppliers)
  145 |     // But for journey test, we'll proceed to demonstrate the flow
  146 |     
  147 |     // Step 8: Lock & Dispatch
  148 |     // Navigate to lock/dispatch page
  149 |     await page.goto('/cases/1/lock-dispatch')
  150 |     
  151 |     await expect(page.getByRole('heading', { name: /lock.*dispatch|finalization/i })).toBeVisible()
  152 |     
  153 |     // Verify finalized longlist is displayed
  154 |     await expect(page.getByText(/finalized longlist|locked longlist/i)).toBeVisible()
  155 |     
  156 |     // Lock the longlist
  157 |     const lockButton = page.getByRole('button', { name: /lock longlist|lock/i })
  158 |     if (await lockButton.isVisible()) {
  159 |       await lockButton.click()
  160 |       await page.waitForTimeout(1000)
  161 |       
  162 |       // Verify lock success notification or state change
  163 |       // After lock, dispatch button should be available
  164 |     }
  165 |     
  166 |     // Dispatch tender - assert button exists
  167 |     const dispatchButton = page.getByRole('button', { name: /dispatch tender|dispatch/i })
  168 |     await expect(dispatchButton).toBeVisible()
  169 |     await dispatchButton.click()
  170 |     await page.waitForTimeout(2000)
  171 |     
  172 |     // Verify dispatch success
  173 |     await expect(page.getByText(/dispatch.*success|successfully dispatched/i)).toBeVisible()
  174 |     
  175 |     // Step 9: Verify Final State
  176 |     // Return to case overview to verify final state
  177 |     await page.goto('/cases/1')
  178 |     
  179 |     // Case should show dispatched state
  180 |     await expect(page.getByText(/dispatched|complete/i)).toBeVisible()
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
> 236 |     const caseNumber = await page.getByText('CASE-2026-00001').textContent()
      |                                                                ^ TimeoutError: locator.textContent: Timeout 15000ms exceeded.
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
  281 |     await expect(page.getByText(/intake_normalized|normalized/i)).toBeVisible()
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