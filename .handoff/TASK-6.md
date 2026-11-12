# TASK-6 Handoff: Classification Verdict and VMS Routing

## Classification Verdict Generation

**AGN1 Service Classification Method:**
- `AGN1Service.classify_need(case_id, confirmed_attributes)` - Executes ATS3 classification step
- Returns `HITLReview` with pending classification verdict in `generated_payload`
- Verdict: `single_resource` or `it_service`
- Includes confidence score (0.0-1.0) and rationale inputs

**Classification Verdict Structure:**
```json
{
  "ai_verdict": "single_resource" | "it_service",
  "confidence_score": 0.88,
  "rationale_inputs": {
    "duration_indicator": "6_months",
    "skills_count": 1,
    "complexity_score": 0.30
  },
  "reasoning": "Classified as single_resource based on single skill requirement"
}
```

**Classification Logic:**
- Single skill requirement → `single_resource`
- Short duration (< 6 months) → `single_resource`
- Multiple skills (> 1) OR long duration (≥ 6 months) → `it_service`

## VMS Handoff Endpoint

**Route:** `POST /api/v1/cases/{caseId}/vms-handoff`

**Authentication:** Required (JWT Bearer token)

**Preconditions:**
- Case must have `final_classification = 'single_resource'`
- Classification must be confirmed via classification review

**Request:** No body required

**Response (200 OK):**
```json
{
  "message": "Case CASE-2026-00008 routed to VMS. VMS Reference: VMS-2026-000008"
}
```

**Response (409 Conflict):**
```json
{
  "detail": "Case 123 is not classified as single_resource",
  "status_code": 409
}
```

**Effects:**
- Creates `vms_handoff` record with VMS reference ID
- Updates case `workflow_state` to `routed_to_vms`
- Updates case `next_action` to `vms_processing`
- Records workflow event and audit log
- Terminates supplier-selection workflow

## VMS Handoff Payload

**TOL5 Adapter Request Snapshot:**
```json
{
  "case_id": 8,
  "case_number": "CASE-2026-00008",
  "classification": "single_resource",
  "attributes": {
    "service_category": {"value": "network_support"},
    "estimated_duration": {"value": "3_months"},
    "required_skills": {"value": ["Networking"]}
  },
  "submitted_at": "2026-11-12T10:30:00Z"
}
```

**TOL5 Adapter Response:**
```json
{
  "vms_reference_id": "VMS-2026-000008",
  "handoff_status": "success",
  "request_snapshot": "{...}"
}
```

## VMS Reference ID Format

**Format:** `VMS-YYYY-NNNNNN`

**Examples:**
- `VMS-2026-000008` - Case ID 8 routed in 2026
- `VMS-2026-000012` - Case ID 12 routed in 2026

**Generation:** Simulated in TOL5 adapter stub using case ID as sequence for reproducibility

## Seed Cases with Classifications

**CASE-2026-00007** - Classification pending (single_resource verdict)
- Workflow state: `classification_pending`
- AI verdict: `single_resource`
- Confidence: 0.85
- Rationale: Single skill requirement (Java)
- Status: Pending classification review

**CASE-2026-00008** - Confirmed single_resource with VMS handoff
- Workflow state: `routed_to_vms`
- Final classification: `single_resource`
- VMS reference: `VMS-2026-000008`
- Handoff status: `success`
- Classification confirmed and routed to VMS

**CASE-2026-00006** - IT-service classification pending
- Workflow state: `classification_pending`
- AI verdict: `it_service`
- Confidence: 0.94
- Rationale: Multi-year duration (24 months), 5 required skills
- Status: Pending classification review

## Workflow State Transitions

**Single-Resource Path:**
1. `classification_pending` → Classification review submitted
2. `classification_approved` → Classification confirmed as single_resource
3. `routed_to_vms` → VMS handoff triggered (terminal state for supplier-selection workflow)

**IT-Service Path:**
1. `classification_pending` → Classification review submitted
2. `classification_approved` → Classification confirmed as it_service
3. `evidence_retrieval_pending` → Continue to supplier evidence retrieval (not in this task)

## Database Schema

**vms_handoff Table:**
- `id` (Integer, PK, auto-increment)
- `case_id` (Integer, FK → need_case.id, unique)
- `vms_reference_id` (String(100))
- `handoff_status` (String(50)) - `success`, `failed`, `pending`
- `request_snapshot` (Text, JSONB)
- `handed_off_at` (DateTime with timezone)
- `requirement_tags` (String(500))

## AGN5 Rule Engine Method

**Method:** `AGN5RuleEngine.route_single_resource_case(case_id, case_number, classification_result, confirmed_attributes)`

**Returns:** `VMSHandoff` record

**Operations:**
1. Invokes TOL5 adapter with case details
2. Creates `vms_handoff` record with VMS reference ID
3. Persists handoff status and request snapshot

## Workflow Orchestrator Method

**Method:** `WorkflowOrchestratorService.route_single_resource_case(case_id, reviewer_id)`

**Returns:** Updated `NeedCase` with `routed_to_vms` state

**Operations:**
1. Validates case classification is `single_resource`
2. Retrieves classification result and confirmed attributes
3. Calls AGN5 rule engine to perform VMS routing
4. Updates case workflow state to `routed_to_vms`
5. Records workflow event and audit log

## Migration

**Revision:** 005

**Upgrade:** Creates `vms_handoff` table with FK to `need_case` and unique constraint on `case_id`

**Downgrade:** Drops `vms_handoff` table

## Test Coverage

**test_integrations_vms.py** - 9 integration tests:
1. `test_classification_verdict_generation` - AGN1 generates verdict with confidence
2. `test_classification_verdict_linked_to_attributes` - Verdict linked to attributes
3. `test_classification_confidence_metadata_stored` - Confidence metadata persisted
4. `test_classification_rationale_viewable` - Rationale inputs accessible
5. `test_vms_handoff_for_single_resource_case` - VMS handoff triggered
6. `test_supplier_selection_workflow_terminated_after_vms_handoff` - Workflow closed
7. `test_case_retains_vms_reference` - VMS reference retained
8. `test_routed_cases_distinguishable_in_work_queues` - Routed cases filterable

## Acceptance Criteria Verification

✅ The system produces a classification verdict of either single-resource or IT-service  
✅ The verdict is linked to the structured attribute set used for the decision  
✅ The system stores confidence or certainty metadata for the classification result  
✅ Users can view the classification rationale inputs used by the system  
✅ A confirmed single-resource case triggers a Vendor Management System handoff action  
✅ The supplier-selection workflow for that case is terminated after successful handoff registration  
✅ The case retains a reference to the external routing outcome  
✅ Users can distinguish routed-out cases from in-scope IT-service cases in reporting and work queues  
