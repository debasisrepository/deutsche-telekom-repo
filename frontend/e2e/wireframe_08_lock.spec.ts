import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 08: Lock and tender dispatch', () => {
  test('logs in, navigates to lock/dispatch page, and verifies locked state and dispatch statuses', async ({ page, apiGuard }) => {
    // Log in with seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'procurement.reviewer@telekom.de');
    await page.fill('input[type="password"]', 'Review-pass-1');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForLoadState('networkidle');
    await page.waitForURL((url) => !url.pathname.includes('/login'));

    // Navigate to lock and dispatch page for seed longlist
    const longlistId = '00000000-0000-0000-0000-000000000021';
    await page.goto(`/lock-dispatch/${longlistId}`);
    await page.waitForLoadState('networkidle');

    // Verify page renders
    await expect(
      page.getByRole('heading', { name: /Finalize and lock longlist, then dispatch tender/i })
    ).toBeVisible();

    // Verify progress indicator with finalization steps
    await expect(page.getByText(/ATS9 Count validated: pass \(5\)/i).first()).toBeVisible();
    await expect(page.getByText(/ATS10 Adjustments captured \(2\)/i).first()).toBeVisible();
    await expect(page.getByText(/ATS11 Locked/i).first()).toBeVisible();
    await expect(page.getByText(/ATS12 Tender dispatch/i).first()).toBeVisible();

    // Verify ATS11 locked longlist section
    await expect(page.getByText(/ATS11 Locked longlist record/i)).toBeVisible();

    // Verify locked status notification
    await expect(page.getByText(/Locked and immutable/i)).toBeVisible();

    // Verify longlist details (checking breadcrumb)
    await expect(page.locator('p').filter({ hasText: longlistId }).first()).toBeVisible();

    // Verify validation at lock shows pass with 5 suppliers
    await expect(page.getByText(/5 suppliers/i).first()).toBeVisible();

    // Verify pre-lock checks section
    await expect(page.getByText(/Pre-lock checks \(all passed\)/i)).toBeVisible();
    await expect(page.getByText(/Supplier count 5 within 3 to 6/i)).toBeVisible();
    await expect(page.getByText(/Each supplier has a cited evidence source/i)).toBeVisible();
    await expect(page.getByText(/Audit-log write succeeded/i)).toBeVisible();

    // Verify specific suppliers in locked table
    await expect(page.getByText('SUP-0231').first()).toBeVisible();
    await expect(page.getByText('SUP-0118').first()).toBeVisible();
    await expect(page.getByText('SUP-0045').first()).toBeVisible();
    await expect(page.getByText('SUP-0518').first()).toBeVisible();
    await expect(page.getByText('SUP-0412').first()).toBeVisible();

    // Verify ATS12 tender dispatch section
    await expect(page.getByText(/ATS12 Tender package and dispatch/i)).toBeVisible();

    // Verify dispatch batch ID
    await expect(page.getByText(/DSP-2024-0402-01/i).first()).toBeVisible();

    // Verify delivery statistics
    await expect(page.getByText(/Delivered/i).first()).toBeVisible();

    // Verify specific dispatch statuses
    await expect(page.locator('text=CONF-77120')).toBeVisible();
    await expect(page.getByText('retrying').first()).toBeVisible();
    await expect(page.getByText('escalated').first()).toBeVisible();
  });
});
