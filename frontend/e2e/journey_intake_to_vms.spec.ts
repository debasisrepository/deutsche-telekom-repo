import { test, expect } from './_pipeline_guard'

/**
 * E2E Journey Test: Intake → Extraction Review → Classification Review → Single-Resource VMS Routing (Alternate Flow)
 * 
 * This test covers the alternate workflow for single-resource cases that are routed to VMS instead of
 * continuing through the IT-service supplier selection workflow.
 * 
 * Uses CASE-2026-00007 (email, Senior Java Developer) which has:
 * - classification_pending state
 * - Pending classification review with single_resource AI verdict
 * - Should route to VMS after classification confirmation
 */

test.describe('Journey: Intake to VMS (Single-Resource Alternate Flow)', () => {
  test.beforeEach(async ({ page }) => {
    // Log in with admin credentials
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@example.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('complete journey from intake to VMS routing for single-resource case', async ({ page }) => {
    // Step 1: Verify case appears in intake queue or cases list
    await page.goto('/')
    await expect(page.getByRole('heading', { name: /intake queue/i })).toBeVisible()
    
    // Navigate to cases list to find CASE-2026-00007
    await page.goto('/cases')
    await expect(page.getByText('CASE-2026-00007')).toBeVisible()
    await expect(page.getByText(/Senior Java Developer/i)).toBeVisible()
    
    // Click case to view details
    await page.click('text=CASE-2026-00007')
    await page.waitForURL(/\/cases\/7$/)
    
    // Step 2: Verify case overview shows classification_pending state
    await expect(page.getByRole('heading', { name: /case overview/i })).toBeVisible()
    await expect(page.getByText('CASE-2026-00007')).toBeVisible()
    
    // Verify workflow stepper
    const stepper = page.getByRole('list', { name: /case progress/i })
    await expect(stepper).toBeVisible()
    
    // Verify state indicates classification pending
    await expect(page.getByText(/classification_pending|classification pending/i)).toBeVisible()
    
    // Step 3: Navigate to Classification Review
    await page.goto('/cases/7/classification-review')
    
    await expect(page.getByRole('heading', { name: /classification review/i })).toBeVisible()
    
    // Verify AMBER gate notification
    await expect(page.getByText(/human approval required|AMBER gate/i)).toBeVisible()
    
    // Verify single_resource classification verdict
    await expect(page.getByText(/single_resource|single resource/i)).toBeVisible()
    
    // Verify confidence score is displayed
    await expect(page.getByText(/confidence/i)).toBeVisible()
    
    // Verify rationale inputs are shown
    await expect(page.getByText(/duration|skills|complexity/i)).toBeVisible()
    
    // Confirm classification verdict (accept single_resource classification)
    const confirmButton = page.getByRole('button', { name: /confirm classification|confirm/i })
    await expect(confirmButton).toBeVisible()
    await confirmButton.click()
    
    // Should navigate back to case overview
    await page.waitForURL(/\/cases\/7$/, { timeout: 10000 })
    
    // Wait for backend VMS routing processing
    await page.waitForTimeout(2000)
    
    // Step 4: Verify VMS Routing
    // After single_resource confirmation, case should be routed to VMS
    // Navigate to VMS routing confirmation page
    await page.goto('/cases/7/vms-routing')
    
    await expect(page.getByRole('heading', { name: /vms routing|vendor management/i })).toBeVisible()
    
    // Verify VMS handoff confirmation is displayed
    await expect(page.getByText(/routed to vms|vms handoff|vendor management system/i)).toBeVisible()
    
    // Verify VMS reference ID is displayed
    await expect(page.getByText(/VMS-2026-|VMS reference/i)).toBeVisible()
    
    // Verify handoff status is shown
    await expect(page.getByText(/handoff status|success|pending/i)).toBeVisible()
    
    // Verify case details are preserved
    await expect(page.getByText('CASE-2026-00007')).toBeVisible()
    
    // Step 5: Verify workflow termination
    // Return to case overview
    await page.goto('/cases/7')
    
    // Case should show routed_to_vms state
    await expect(page.getByText(/routed_to_vms|routed to vms|vms processing/i)).toBeVisible()
    
    // Verify next action indicates VMS processing
    await expect(page.getByText(/vms_processing|vms processing/i)).toBeVisible()
    
    // Verify final classification is set to single_resource
    await expect(page.getByText(/single_resource|single resource/i)).toBeVisible()
    
    // Step 6: Verify IT-service workflow did NOT continue
    // Evidence mapping should not be available for VMS-routed cases
    await page.goto('/cases/7/evidence-mapping')
    
    // Should either redirect or show that this workflow is not applicable
    // (Exact behavior depends on implementation)
    // For now, verify we don't see longlist generation options
    const generateButton = page.getByRole('button', { name: /generate longlist|generate proposal/i })
    const isGenerateVisible = await generateButton.isVisible().catch(() => false)
    
    if (isGenerateVisible) {
      // If page loads, verify it indicates VMS routing instead
      await expect(page.getByText(/routed to vms|not applicable/i)).toBeVisible()
    }
  })

  test('verifies VMS handoff data is persisted', async ({ page }) => {
    // This test verifies that VMS handoff record is created and persisted
    
    const caseId = 8 // CASE-2026-00008 (already routed to VMS in seed data)
    
    // Navigate directly to VMS routing page for already-routed case
    await page.goto(`/cases/${caseId}/vms-routing`)
    
    await expect(page.getByRole('heading', { name: /vms routing|vendor management/i })).toBeVisible()
    
    // Verify VMS reference ID is displayed
    await expect(page.getByText('VMS-2026-000008')).toBeVisible()
    
    // Verify handoff status is success
    await expect(page.getByText(/success/i)).toBeVisible()
    
    // Verify case number is displayed
    await expect(page.getByText('CASE-2026-00008')).toBeVisible()
    
    // Verify handoff details section
    await expect(page.getByText(/handoff details|request snapshot/i)).toBeVisible()
    
    // Verify attributes from handoff are displayed
    await expect(page.getByText(/classification|single_resource/i)).toBeVisible()
  })

  test('verifies single-resource cases are distinguishable from IT-service cases', async ({ page }) => {
    // This test verifies that VMS-routed cases can be filtered/distinguished from IT-service cases
    
    // Navigate to cases list
    await page.goto('/cases')
    
    // Look for workflow state filter or case list
    await expect(page.getByRole('heading', { name: /cases|case list/i })).toBeVisible()
    
    // Verify CASE-2026-00008 (routed_to_vms) is visible
    await expect(page.getByText('CASE-2026-00008')).toBeVisible()
    
    // Verify state badge or indicator
    await expect(page.getByText(/routed_to_vms|vms/i)).toBeVisible()
    
    // Verify CASE-2026-00001 (IT-service flow) is also visible but with different state
    await expect(page.getByText('CASE-2026-00001')).toBeVisible()
    
    // Can filter by workflow_state
    // Assert filter exists and use it
    const filterOrSearch = page.getByRole('combobox', { name: /filter|state/i })
    await expect(filterOrSearch).toBeVisible()
    // Select routed_to_vms filter
    await filterOrSearch.click()
    const vmsOption = page.getByRole('option', { name: /routed.*vms|vms/i })
    await expect(vmsOption).toBeVisible()
    await vmsOption.click()
    
    // Should now see only VMS-routed cases
    await expect(page.getByText('CASE-2026-00008')).toBeVisible()
  })

  test('verifies workflow events for VMS routing path', async ({ page }) => {
    // This test verifies that workflow events are created for VMS routing actions
    
    const caseId = 8 // CASE-2026-00008 (already routed)
    
    // Navigate to case overview
    await page.goto(`/cases/${caseId}`)
    
    await expect(page.getByText('CASE-2026-00008')).toBeVisible()
    
    // Verify final state
    await expect(page.getByText(/routed_to_vms/i)).toBeVisible()
    
    // Navigate to VMS routing page
    await page.goto(`/cases/${caseId}/vms-routing`)
    
    // Verify audit trail section - assert it exists
    const auditSection = page.getByRole('heading', { name: /audit|history|timeline/i })
    await expect(auditSection).toBeVisible()
    // Verify workflow events are displayed
    await expect(page.getByText(/classification.*confirmed|routed to vms|vms handoff/i)).toBeVisible()
    
    // Verify handoff timestamp
    await expect(page.getByText(/handed off at|handoff date/i)).toBeVisible()
  })

  test('verifies classification override can route to VMS', async ({ page }) => {
    // This test verifies that overriding an it_service classification to single_resource routes to VMS
    
    const caseId = 6 // CASE-2026-00006 (it_service verdict pending)
    
    // Navigate to classification review
    await page.goto(`/cases/${caseId}/classification-review`)
    
    await expect(page.getByRole('heading', { name: /classification review/i })).toBeVisible()
    
    // Verify AI verdict is it_service
    await expect(page.getByText(/it_service|IT Service/i)).toBeVisible()
    
    // Override to single_resource - assert override button exists
    const overrideButton = page.getByRole('button', { name: /override|change classification/i })
    await expect(overrideButton).toBeVisible()
    await overrideButton.click()
    
    // Select single_resource from override options - assert it exists
    const singleResourceOption = page.getByRole('radio', { name: /single_resource|single resource/i })
    await expect(singleResourceOption).toBeVisible()
    await singleResourceOption.click()
    
    // Provide rationale - assert field exists
    const rationaleField = page.getByRole('textbox', { name: /rationale|reason/i })
    await expect(rationaleField).toBeVisible()
    await rationaleField.fill('Overriding to single_resource based on stakeholder input')
    
    // Confirm override - assert confirm button exists
    const confirmOverride = page.getByRole('button', { name: /confirm override|save/i })
    await expect(confirmOverride).toBeVisible()
    await confirmOverride.click()
    await page.waitForURL(/\/cases\/6$/, { timeout: 10000 })
    await page.waitForTimeout(2000)
    
    // Verify case was routed to VMS
    await page.goto(`/cases/${caseId}/vms-routing`)
    await expect(page.getByText(/routed to vms|vms handoff/i)).toBeVisible()
  })

  test('verifies VMS reference ID format and external routing outcome', async ({ page }) => {
    // This test verifies VMS reference ID format and audit trail
    
    const caseId = 8 // CASE-2026-00008
    
    // Navigate to VMS routing page
    await page.goto(`/cases/${caseId}/vms-routing`)
    
    // Verify VMS reference ID follows format VMS-YYYY-NNNNNN
    const vmsRefElement = page.getByText(/VMS-2026-\d{6}/)
    await expect(vmsRefElement).toBeVisible()
    
    const vmsRefText = await vmsRefElement.textContent()
    expect(vmsRefText).toMatch(/VMS-2026-\d{6}/)
    
    // Verify external routing outcome is retained
    await expect(page.getByText(/handoff status/i)).toBeVisible()
    await expect(page.getByText(/success|pending|failed/i)).toBeVisible()
    
    // Verify request snapshot is available for audit
    await expect(page.getByText(/request snapshot|handoff details/i)).toBeVisible()
    
    // Verify case attributes are in snapshot
    await expect(page.getByText(/service_category|network_support/i)).toBeVisible()
    await expect(page.getByText(/estimated_duration|3_months/i)).toBeVisible()
  })

  test('verifies supplier selection workflow terminates after VMS routing', async ({ page }) => {
    // This test verifies that VMS-routed cases do not continue through supplier selection
    
    const caseId = 8 // CASE-2026-00008 (routed to VMS)
    
    // Navigate to case overview
    await page.goto(`/cases/${caseId}`)
    
    // Verify routed_to_vms state
    await expect(page.getByText(/routed_to_vms/i)).toBeVisible()
    
    // Try to navigate to longlist adjustments page
    await page.goto(`/cases/${caseId}/longlist-adjustments`)
    
    // Should either redirect, show error, or indicate not applicable
    // Verify we don't see supplier selection UI
    const supplierTable = page.getByRole('table', { name: /suppliers|longlist/i })
    const isTableVisible = await supplierTable.isVisible().catch(() => false)
    
    if (isTableVisible) {
      // If page loads, verify it shows VMS routing instead
      await expect(page.getByText(/routed to vms|not applicable/i)).toBeVisible()
    }
    
    // Try to navigate to lock/dispatch page
    await page.goto(`/cases/${caseId}/lock-dispatch`)
    
    // Should not show tender dispatch for VMS-routed cases
    const dispatchButton = page.getByRole('button', { name: /dispatch tender/i })
    const isDispatchVisible = await dispatchButton.isVisible().catch(() => false)
    
    if (isDispatchVisible) {
      // Should be disabled or not applicable
      await expect(page.getByText(/vms routed|not applicable/i)).toBeVisible()
    }
  })
})
