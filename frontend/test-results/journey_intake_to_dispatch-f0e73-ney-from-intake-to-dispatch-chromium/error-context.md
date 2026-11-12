# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journey_intake_to_dispatch.spec.ts >> Journey: Intake to Dispatch (IT-Service Success Flow) >> complete journey from intake to dispatch
- Location: e2e/journey_intake_to_dispatch.spec.ts:27:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: /intake queue/i })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('heading', { name: /intake queue/i }) with timeout 5000ms
  - waiting for getByRole('heading', { name: /intake queue/i })

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
  1   | import { test, expect } from './_pipeline_guard'
  2   | 
  3   | /**
  4   |  * E2E Journey Test: Intake → Extraction Review → Classification Review → IT-Service Path → 
  5   |  * Evidence/Mapping → Longlist Generation → Adjustments → Validation → Lock → Dispatch (Success Flow)
  6   |  * 
  7   |  * This test covers the full multi-screen workflow for IT-service cases from intake to tender dispatch,
  8   |  * verifying workflow state progression, data persistence, and audit logging at each step.
  9   |  * 
  10  |  * Uses CASE-2026-00001 (RFP document, cloud infrastructure modernization) which has:
  11  |  * - intake_normalized state (ready for extraction review)
  12  |  * - Evidence links to SUP-CLOUD-001
  13  |  * - Panel mapping to PANEL-CLOUD-001
  14  |  * - Longlist proposal with ranked suppliers
  15  |  */
  16  | 
  17  | test.describe('Journey: Intake to Dispatch (IT-Service Success Flow)', () => {
  18  |   test.beforeEach(async ({ page }) => {
  19  |     // Log in with admin credentials
  20  |     await page.goto('/login')
  21  |     await page.fill('input[type="email"]', 'admin@example.com')
  22  |     await page.fill('input[type="password"]', 'admin123')
  23  |     await page.click('button[type="submit"]')
  24  |     await page.waitForURL('/')
  25  |   })
  26  | 
  27  |   test('complete journey from intake to dispatch', async ({ page }) => {
  28  |     // Step 1: Verify case appears in intake queue
  29  |     await page.goto('/')
> 30  |     await expect(page.getByRole('heading', { name: /intake queue/i })).toBeVisible()
      |                                                                        ^ Error: expect(locator).toBeVisible() failed
  31  |     
  32  |     // Find CASE-2026-00001 in the queue
  33  |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  34  |     await expect(page.getByText(/cloud infrastructure modernization/i)).toBeVisible()
  35  |     
  36  |     // Click case to view details
  37  |     await page.click('text=CASE-2026-00001')
  38  |     await page.waitForURL(/\/cases\/1$/)
  39  |     
  40  |     // Step 2: Verify case overview page shows intake_normalized state
  41  |     await expect(page.getByRole('heading', { name: /case overview/i })).toBeVisible()
  42  |     await expect(page.getByText('CASE-2026-00001')).toBeVisible()
  43  |     
  44  |     // Verify workflow stepper shows intake stage
  45  |     const stepper = page.getByRole('list', { name: /case progress/i })
  46  |     await expect(stepper).toBeVisible()
  47  |     
  48  |     // Verify state badge shows normalized
  49  |     await expect(page.getByText(/intake_normalized|normalized/i)).toBeVisible()
  50  |     
  51  |     // Navigate to extraction review
  52  |     await page.goto('/cases/1/extraction-review')
  53  |     
  54  |     // Step 3: Extraction Review - Approve extracted attributes
  55  |     await expect(page.getByRole('heading', { name: /extraction review/i })).toBeVisible()
  56  |     
  57  |     // Verify warning notification about AMBER gate
  58  |     await expect(page.getByText(/human approval required|AMBER gate/i)).toBeVisible()
  59  |     
  60  |     // Verify extracted attributes table
  61  |     await expect(page.getByRole('columnheader', { name: /attribute/i })).toBeVisible()
  62  |     await expect(page.getByRole('columnheader', { name: /extracted value/i })).toBeVisible()
  63  |     await expect(page.getByRole('columnheader', { name: /confidence/i })).toBeVisible()
  64  |     
  65  |     // Approve extraction as-is
  66  |     const approveButton = page.getByRole('button', { name: /approve as is|approve/i })
  67  |     await expect(approveButton).toBeVisible()
  68  |     await approveButton.click()
  69  |     
  70  |     // Should navigate back to case overview
  71  |     await page.waitForURL(/\/cases\/1$/, { timeout: 10000 })
  72  |     
  73  |     // Wait for backend processing and state transition
  74  |     await page.waitForTimeout(1000)
  75  |     
  76  |     // Step 4: Navigate to Classification Review
  77  |     // After extraction approval, case should transition to classification_pending
  78  |     await page.goto('/cases/1/classification-review')
  79  |     
  80  |     await expect(page.getByRole('heading', { name: /classification review/i })).toBeVisible()
  81  |     
  82  |     // Verify classification verdict is displayed
  83  |     await expect(page.getByText(/it_service|IT Service/i)).toBeVisible()
  84  |     
  85  |     // Verify confidence score is shown
  86  |     await expect(page.getByText(/confidence/i)).toBeVisible()
  87  |     
  88  |     // Confirm classification verdict
  89  |     const confirmButton = page.getByRole('button', { name: /confirm classification|confirm/i })
  90  |     await expect(confirmButton).toBeVisible()
  91  |     await confirmButton.click()
  92  |     
  93  |     // Should navigate back to case overview
  94  |     await page.waitForURL(/\/cases\/1$/, { timeout: 10000 })
  95  |     
  96  |     // Wait for backend processing
  97  |     await page.waitForTimeout(1000)
  98  |     
  99  |     // Step 5: Evidence & Panel Mapping
  100 |     // After classification confirmation, navigate to evidence/mapping page
  101 |     await page.goto('/cases/1/evidence-mapping')
  102 |     
  103 |     await expect(page.getByRole('heading', { name: /evidence.*mapping|panel mapping/i })).toBeVisible()
  104 |     
  105 |     // Verify evidence table shows historical evidence
  106 |     await expect(page.getByText(/SUP-CLOUD-001|CloudTech/i)).toBeVisible()
  107 |     await expect(page.getByText(/citation|evidence/i)).toBeVisible()
  108 |     
  109 |     // Verify panel mapping is displayed
  110 |     await expect(page.getByText(/PANEL-CLOUD-001|Cloud Infrastructure/i)).toBeVisible()
  111 |     
  112 |     // Generate longlist proposal
  113 |     const generateButton = page.getByRole('button', { name: /generate longlist|generate proposal/i })
  114 |     await expect(generateButton).toBeVisible()
  115 |     await generateButton.click()
  116 |     
  117 |     // Wait for proposal generation
  118 |     await page.waitForTimeout(2000)
  119 |     
  120 |     // Step 6: Longlist Adjustments
  121 |     // Navigate to adjustments page
  122 |     await page.goto('/cases/1/longlist-adjustments')
  123 |     
  124 |     await expect(page.getByRole('heading', { name: /longlist adjustments/i })).toBeVisible()
  125 |     
  126 |     // Verify ranked longlist is displayed
  127 |     await expect(page.getByText(/ranked longlist|suppliers/i)).toBeVisible()
  128 |     
  129 |     // Verify supplier appears in longlist
  130 |     await expect(page.getByText(/SUP-CLOUD-001|CloudTech/i)).toBeVisible()
```