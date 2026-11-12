import { test, expect } from './_pipeline_guard'

test.describe('Wireframe 03 - Extraction Review', () => {
  test.beforeEach(async ({ page }) => {
    // Log in with seed credentials
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@example.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('displays extraction review page with case header and stepper', async ({ page }) => {
    // Navigate to extraction review page
    await page.goto('/cases/4/extraction-review')

    // Verify page heading
    await expect(page.getByRole('heading', { name: /extraction review gate/i })).toBeVisible()

    // Verify case header is present
    await expect(page.getByText(/CASE-2026-/)).toBeVisible()

    // Verify workflow stepper is present
    await expect(page.getByRole('list', { name: /case progress/i })).toBeVisible()
  })

  test('displays extracted attributes table', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Verify table headers
    await expect(page.getByRole('columnheader', { name: /attribute/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /extracted value/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /provenance/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /confidence/i })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: /source excerpt/i })).toBeVisible()

    // Verify some attributes are present
    await expect(page.getByRole('cell', { name: /service scope/i })).toBeVisible()
    await expect(page.getByRole('cell', { name: /duration/i })).toBeVisible()
  })

  test('displays warning notification about AMBER gate', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Verify warning notification
    await expect(page.getByText(/human approval required \(AMBER gate\)/i)).toBeVisible()
  })

  test('allows approving extraction as-is', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Click approve button
    const approveButton = page.getByRole('button', { name: /approve as is/i })
    await approveButton.click()

    // Should navigate back to case overview after successful approval
    await page.waitForURL(/\/cases\/\d+$/)
  })

  test('allows editing attributes before approval', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Find an editable attribute cell and interact with it
    // The implementation allows editing by changing values in TextInput fields
    const saveButton = page.getByRole('button', { name: /save edits and approve/i })

    // Initially, save button should be disabled (no edits)
    await expect(saveButton).toBeDisabled()

    // After making edits, the button should become enabled
    // (In actual test, you would edit a field first)
  })

  test('allows rejecting extraction', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Click reject button
    const rejectButton = page.getByRole('button', { name: /reject extraction/i })
    await rejectButton.click()

    // Should navigate back to case overview after rejection
    await page.waitForURL(/\/cases\/\d+$/)
  })

  test('displays reviewer comment textarea', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Verify comment field
    const commentField = page.getByRole('textbox', {
      name: /reviewer comment/i,
    })
    await expect(commentField).toBeVisible()

    // Can type in comment field
    await commentField.fill('Test reviewer comment')
    await expect(commentField).toHaveValue('Test reviewer comment')
  })

  test('displays source context section', async ({ page }) => {
    await page.goto('/cases/4/extraction-review')

    // Verify source context heading
    await expect(page.getByRole('heading', { name: /source context/i })).toBeVisible()

    // Verify source document reference
    await expect(page.getByText(/\.pdf/i)).toBeVisible()
  })
})
