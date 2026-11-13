import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 02: Attribute extraction review', () => {
  test('logs in, navigates to attribute review', async ({ page, apiGuard }) => {
    // Log in through login form with seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'procurement.reviewer@telekom.de');
    await page.fill('input[type="password"]', 'Review-pass-1');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForLoadState('networkidle');
    await page.waitForURL((url) => !url.pathname.includes('/login'));

    // Navigate to attribute review for a seed need ID
    const needId = '00000000-0000-0000-0000-000000000001';
    await page.goto(`/reviews/${needId}/attributes`);
    await page.waitForLoadState('networkidle');

    // Verify page heading
    await expect(page.getByRole('heading', { name: /extracted need attributes/i })).toBeVisible();

    // Verify extracted fields table heading is present
    await expect(page.getByRole('heading', { name: /needattributes/i })).toBeVisible();

    // Verify attribute fields are rendered
    await expect(page.getByText('service_type')).toBeVisible();
    await expect(page.getByText('Managed cloud migration service')).toBeVisible();

    // Verify confidence visualization with high confidence field
    await expect(page.getByText('0.94').first()).toBeVisible();

    // Verify warning notification for low confidence fields
    await expect(page.getByText(/2 fields need attention/i)).toBeVisible();

    // Verify source comparison section
    await expect(page.getByText(/raw artifact excerpt/i)).toBeVisible();

    // Verify budget correction field
    const budgetInput = page.getByLabel(/correct budget_indication/i);
    await expect(budgetInput).toBeVisible();

    // Verify reviewer notes field
    const notesTextarea = page.getByLabel(/reviewer notes/i);
    await expect(notesTextarea).toBeVisible();

    // Verify decision buttons
    const approveButton = page.getByRole('button', { name: /approve and continue to ats3/i });
    await expect(approveButton).toBeVisible();
    
    const modifyButton = page.getByRole('button', { name: /save modifications/i });
    await expect(modifyButton).toBeVisible();

    const rejectButton = page.getByRole('button', { name: /reject extraction/i });
    await expect(rejectButton).toBeVisible();
  });
});
