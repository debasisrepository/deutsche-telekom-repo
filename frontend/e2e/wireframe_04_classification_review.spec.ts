import { test, expect } from './_pipeline_guard'

test.describe('Wireframe 04 - Classification Review', () => {
  test.beforeEach(async ({ page }) => {
    // Log in with seed credentials
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@example.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('displays classification review page with case header and stepper', async ({ page }) => {
    // Navigate to classification review page
    await page.goto('/cases/6/classification-review')

    // Verify page heading
    await expect(
      page.getByRole('heading', { name: /classification review and override/i })
    ).toBeVisible()

    // Verify case header is present
    await expect(page.getByText(/CASE-2026-/)).toBeVisible()

    // Verify workflow stepper is present
    await expect(page.getByRole('list', { name: /case progress/i })).toBeVisible()
  })

  test('displays system verdict section', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Verify verdict is displayed
    await expect(page.getByText(/IT service/i)).toBeVisible()
    await expect(page.getByText(/AI-generated/i)).toBeVisible()

    // Verify confidence section
    await expect(page.getByText(/confidence/i)).toBeVisible()
  })

  test('displays rationale inputs table', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Verify rationale section heading
    await expect(page.getByRole('heading', { name: /rationale inputs/i })).toBeVisible()

    // Verify table headers
    await expect(page.getByRole('columnheader', { name: /input attribute/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /value/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /points to/i })).toBeVisible()
  })

  test('displays warning notification about AMBER gate', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Verify warning notification
    await expect(page.getByText(/human confirmation required \(AMBER gate\)/i)).toBeVisible()
  })

  test('allows confirming classification verdict', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Select confirm option (should be default)
    const confirmRadio = page.getByRole('radio', { name: /confirm IT service/i })
    await expect(confirmRadio).toBeChecked()

    // Click confirm button
    const confirmButton = page.getByRole('button', { name: /confirm classification/i })
    await confirmButton.click()

    // Should navigate back to case overview after confirmation
    await page.waitForURL(/\/cases\/\d+$/)
  })

  test('allows overriding classification verdict', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Select override option
    const overrideRadio = page.getByRole('radio', { name: /override to single resource/i })
    await overrideRadio.click()
    await expect(overrideRadio).toBeChecked()

    // Fill in required reason
    const reasonField = page.getByRole('textbox', { name: /reason/i })
    await reasonField.fill('Test override reason')

    // Click override button
    const overrideButton = page.getByRole('button', { name: /override/i })
    await overrideButton.click()

    // Should navigate back to case overview after override
    await page.waitForURL(/\/cases\/\d+$/)
  })

  test('displays decision record table', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Verify decision record heading
    await expect(page.getByRole('heading', { name: /decision record/i })).toBeVisible()

    // Verify table shows original verdict
    await expect(page.getByRole('cell', { name: /original verdict/i })).toBeVisible()
    await expect(page.getByRole('cell', { name: /override/i })).toBeVisible()
    await expect(page.getByRole('cell', { name: /final confirmed classification/i })).toBeVisible()
  })

  test('displays routing outcome preview', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Verify routing preview heading
    await expect(page.getByRole('heading', { name: /routing outcome preview/i })).toBeVisible()

    // Verify both routing options are shown
    await expect(page.getByRole('heading', { name: /if IT service/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /if single resource/i })).toBeVisible()

    // Verify routing descriptions
    await expect(page.getByText(/evidence retrieval/i)).toBeVisible()
    await expect(page.getByText(/vendor management system handoff/i)).toBeVisible()
  })

  test('switches between confirm and override modes', async ({ page }) => {
    await page.goto('/cases/6/classification-review')

    // Initially in confirm mode
    await expect(page.getByRole('button', { name: /confirm classification/i })).toBeVisible()

    // Switch to override mode
    const overrideRadio = page.getByRole('radio', { name: /override to single resource/i })
    await overrideRadio.click()

    // Button text should change
    await expect(page.getByRole('button', { name: /override/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /confirm classification/i })).not.toBeVisible()

    // Switch back to confirm mode
    const confirmRadio = page.getByRole('radio', { name: /confirm IT service/i })
    await confirmRadio.click()

    // Button text should change back
    await expect(page.getByRole('button', { name: /confirm classification/i })).toBeVisible()
  })
})
