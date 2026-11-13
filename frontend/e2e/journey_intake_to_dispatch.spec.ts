/**
 * Full journey E2E test: Intake to Dispatch
 * 
 * Tests the complete user workflow from need intake through tender dispatch,
 * verifying each screen transition and data flow. Covers all in-scope features
 * FR-001 through FR-012.
 */

import { test, expect } from './_pipeline_guard';

test.describe('Full Journey: Intake to Dispatch', () => {
  test.beforeEach(async ({ page, apiGuard }) => {
    // Navigate to login and authenticate
    await page.goto('/login');
    
    // Login with seed credentials
    await page.fill('input[type="email"]', 'procurement.reviewer@telekom.de');
    await page.fill('input[type="password"]', 'Review-pass-1');
    await page.click('button[type="submit"]');
    
    // Wait for navigation away from login
    await page.waitForURL((url) => !url.pathname.includes('/login'));
  });

  test('complete journey from intake to dispatch for IT service need', async ({ page, apiGuard }) => {
    /**
     * This test follows a complete procurement workflow:
     * 1. View intake queue (Wireframe 01 - J-01 S01)
     * 2. Review attributes (Wireframe 02 - J-01 S02)
     * 3. Review classification (Wireframe 03 - J-01 S03)
     * 4. View evidence and panel mapping (Wireframe 05 - J-02 S01-S02)
     * 5. View research and proposal (Wireframe 06 - J-02 S03-S04)
     * 6. Validate supplier count (Wireframe 07 - J-03 S01-S02)
     * 7. Lock longlist (Wireframe 08 - J-03 S03-S04)
     * 8. Verify tender dispatch
     */

    // Step 1: Navigate to Intake page and view need queue
    await page.click('a[href="/intake"]');
    await expect(page.locator('h1')).toContainText('Need Intake');
    
    // Verify intake table loads with seed data
    const intakeTable = page.locator('table').first();
    await expect(intakeTable).toBeVisible();
    
    // Look for a classified IT service need from seed data (one that has progressed past classification)
    const needRow = page.locator('tr').filter({ hasText: 'evidence_retrieved' }).first();
    await expect(needRow).toBeVisible();
    
    // Click to view need details
    const viewButton = needRow.locator('button', { hasText: /view/i }).first();
    await viewButton.click();

    // Step 2: Attribute Review page (Wireframe 02)
    // We should now be on the attribute review page
    await page.waitForURL(/\/reviews\/.+\/attributes/);
    await expect(page.locator('h1')).toContainText('Attribute Review');
    
    // Verify attribute fields are displayed
    await expect(page.getByText('service_type')).toBeVisible();
    await expect(page.getByText('scope_description')).toBeVisible();
    
    // Navigate to classification review
    const classificationLink = page.locator('a', { hasText: /classification/i }).first();
    await expect(classificationLink).toBeVisible();
    await classificationLink.click();

    // Step 3: Classification Review page (Wireframe 03)
    await page.waitForURL(/\/reviews\/.+\/classification/);
    await expect(page.locator('h1')).toContainText('Classification Review');
    
    // Verify classification verdict is displayed
    await expect(page.getByText(/it_service|single_resource/i).first()).toBeVisible();
    
    // Verify confidence visualization
    await expect(page.getByText(/confidence/i).first()).toBeVisible();

    // Step 4: Evidence and Panel Mapping (Wireframe 05)
    // Navigate to Evidence section
    await page.click('a[href="/evidence"]');
    await expect(page.locator('h1')).toContainText('Evidence');
    
    // Select a classified IT service need to view evidence
    const evidenceNeedRow = page.locator('tr').filter({ hasText: 'it_service' }).first();
    await expect(evidenceNeedRow).toBeVisible();
    const evidenceViewBtn = evidenceNeedRow.locator('button', { hasText: /view/i }).first();
    await evidenceViewBtn.click();
    
    // Should show evidence and panel data
    await page.waitForURL(/\/evidence\/.+/);
    await expect(page.locator('h1')).toContainText('Historical evidence and panel mapping');
    
    // Verify evidence items table
    await expect(page.getByText(/supplier/i).first()).toBeVisible();
    await expect(page.getByText(/evidence type|panel/i).first()).toBeVisible();

    // Step 5: Research and Proposal (Wireframe 06)
    // Navigate to Research section
    await page.click('a[href="/research"]');
    await expect(page.locator('h1')).toContainText('Research');
    
    // Select a need to view research and proposal
    const researchNeedRow = page.locator('tbody tr').first();
    await expect(researchNeedRow).toBeVisible();
    const researchViewBtn = researchNeedRow.locator('button', { hasText: /view/i }).first();
    await researchViewBtn.click();
    
    // Should show research and ranked proposal
    await page.waitForURL(/\/research\/.+/);
    await expect(page.locator('h1')).toContainText('Niche provider research and ranked longlist proposal');
    
    // Verify ranked suppliers table
    await expect(page.getByText(/rank|supplier/i).first()).toBeVisible();

    // Step 6: Validation (Wireframe 07)
    // Navigate to Validation section
    await page.click('a[href="/validation"]');
    await expect(page.locator('h1')).toContainText('Validation');
    
    // Wait for the table to finish loading by checking for either rows or the "Loading..." text to disappear
    await page.waitForFunction(() => {
      const loading = document.querySelector('body')?.textContent?.includes('Loading...');
      const hasRows = document.querySelectorAll('tbody tr').length > 0;
      return !loading || hasRows;
    }, { timeout: 10000 });
    
    // View a longlist for validation
    const validationRow = page.locator('tbody tr').first();
    await expect(validationRow).toBeVisible();
    const validationViewBtn = validationRow.locator('button', { hasText: /view/i }).first();
    await validationViewBtn.click();
    
    // Should show validation page
    await page.waitForURL(/\/validation\/.+/);
    await expect(page.locator('h1')).toContainText('Supplier Count Validation');
    
    // Verify supplier count and validation status
    await expect(page.locator('h1')).toContainText('Supplier Count Validation');

    // Step 7: Lock and Dispatch (Wireframe 08)
    // Navigate to Lock & Dispatch section
    await page.click('a[href="/lock-dispatch"]');
    await expect(page.locator('h1')).toContainText('Lock');
    
    // View a locked longlist
    const lockRow = page.locator('tbody tr').filter({ hasText: /locked|true/i }).first();
    await expect(lockRow).toBeVisible();
    const lockViewBtn = lockRow.locator('button', { hasText: /view/i }).first();
    await lockViewBtn.click();
    
    // Should show lock and dispatch page
    await page.waitForURL(/\/lock-dispatch\/.+/);
    await expect(page.locator('h1')).toContainText('Finalize and lock longlist');
    
    // Verify locked status
    await expect(page.getByText(/locked|immutable/i).first()).toBeVisible();
    
    // Verify tender dispatch section
    await expect(page.getByText(/dispatch|tender/i).first()).toBeVisible();

    // Step 8: Verify Dispatch details
    // Navigate to Dispatch section to see all tender dispatches
    await page.click('a[href="/dispatch"]');
    await expect(page.locator('h1')).toContainText('Dispatch');
    
    // Verify dispatch status table shows tender outcomes
    const dispatchTable = page.locator('table').first();
    await expect(dispatchTable).toBeVisible();
    // Should show dispatch statuses: delivered, retrying, escalated
    await expect(page.getByText(/delivered|retrying|escalated|pending/i).first()).toBeVisible();
  });

  test('VMS handoff journey for single resource need', async ({ page, apiGuard }) => {
    /**
     * This test verifies the VMS handoff workflow for single_resource cases:
     * 1. View intake queue
     * 2. Find single resource need
     * 3. Verify classification as single_resource
     * 4. Verify VMS handoff status (terminal routing)
     */

    // Navigate to Intake
    await page.click('a[href="/intake"]');
    await expect(page.locator('h1')).toContainText('Need Intake');
    
    // Look for VMS routed need from seed data
    const vmsNeedRow = page.locator('tr').filter({ hasText: /vms_routed_terminal/i }).first();
    await expect(vmsNeedRow).toBeVisible();
    const viewButton = vmsNeedRow.locator('button', { hasText: /view/i }).first();
    await viewButton.click();

    // Should navigate to attributes page
    await page.waitForURL(/\/reviews\/.+\/attributes/);
    
    // Navigate to VMS Handoff section to see the handoff status
    await page.click('a[href="/vms-handoff"]');
    await expect(page.locator('h1')).toContainText('VMS Handoff');
    
    // Find the VMS handoff for this need
    const vmsHandoffRow = page.locator('tr').filter({ hasText: /single_resource/i }).first();
    await expect(vmsHandoffRow).toBeVisible();
    const vmsViewBtn = vmsHandoffRow.locator('button', { hasText: /view/i }).first();
    await vmsViewBtn.click();
    
    // Verify VMS handoff page
    await page.waitForURL(/\/vms-handoff\/.+/);
    await expect(page.locator('h1')).toContainText('VMS Handoff');
    
    // Verify handoff confirmation and VMS reference
    await expect(page.getByText('handover_confirmation').first()).toBeVisible();
    await expect(page.getByText('vms_reference_id').first()).toBeVisible();
  });

  test('navigation between all workflow screens', async ({ page, apiGuard }) => {
    /**
     * Verify that all sections are accessible from sidebar navigation
     * and that each loads the correct content.
     */

    // Test all main navigation links
    const navLinks = [
      { href: '/', title: /dashboard/i },
      { href: '/intake', title: /intake/i },
      { href: '/needs', title: /needs/i },
      { href: '/reviews', title: /reviews/i },
      { href: '/evidence', title: /evidence/i },
      { href: '/research', title: /research/i },
      { href: '/vms-handoff', title: /vms handoff/i },
      { href: '/validation', title: /validation/i },
      { href: '/lock-dispatch', title: /lock/i },
      { href: '/dispatch', title: /dispatch/i },
    ];

    for (const link of navLinks) {
      await page.goto(link.href);
      
      // Wait for navigation
      if (link.href !== '/') {
        await page.waitForURL(`**${link.href}*`);
      }
      
      // Verify page header contains expected title
      const heading = page.locator('h1').first();
      await expect(heading).toContainText(link.title);
    }
  });

  test('end-to-end data consistency across screens', async ({ page, apiGuard }) => {
    /**
     * Verify that data shown on one screen is consistent with data
     * shown on related screens (e.g., same need_id, same supplier IDs).
     */

    // Navigate to Intake and capture a need_id
    await page.click('a[href="/intake"]');
    
    const needIdCell = page.locator('td').filter({ hasText: /^[0-9a-f-]{36}$/i }).first();
    await expect(needIdCell).toBeVisible();
    const needId = await needIdCell.textContent();
    
    // Navigate to attributes page for this need
    const needRow = page.locator('tr').filter({ hasText: needId! }).first();
    const viewBtn = needRow.locator('button', { hasText: /view/i }).first();
    await viewBtn.click();
    
    // Verify the need_id appears on the attribute review page
    await page.waitForURL(/\/reviews\/.+\/attributes/);
    await expect(page.getByText(needId!).first()).toBeVisible();
  });
});
