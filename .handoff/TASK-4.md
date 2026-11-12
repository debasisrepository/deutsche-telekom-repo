# Task 4 Handoff: Case Status Initialization & Attribute Extraction

## Overview
Completed case status and workflow state initialization with attribute extraction (AGN1 service), HITL review workflow, and case list filtering by workflow state.

## Backend Endpoints Added

### Case List with Workflow State Filter
**GET /api/v1/cases?workflow_state={state}**
- Query parameter: `workflow_state` (optional) - filter cases by workflow state
- Response: `{ items: CaseListItem[], total, page, page_size }`
- Example workflow states: `intake_normalized`, `extraction_pending`, `extraction_approved`, `classification_pending`

### Workflow State Values
Cases can be in the following workflow states:
- `intake_pending` - Incomplete mandatory fields
- `intake_normalized` - Successfully normalized with complete fields
- `extraction_pending` - Attribute extraction in progress, HITL review pending
- `extraction_approved` - Extraction review approved by human reviewer
- `classification_pending` - Classification step initiated
- `classification_approved` - Classification review approved

## Data Model Additions

### hitl_review Table
Columns:
- `id` (Integer, PK)
- `case_id` (Integer, FK to need_case.id)
- `review_type` (String) - 'extraction' or 'classification'
- `status` (String) - 'pending', 'approved', 'rejected'
- `assigned_role` (String) - role authorized to review
- `decision` (String) - 'approve', 'edit', 'reject', 'override'
- `reviewer_id` (Integer, FK to user.id, nullable)
- `reviewed_at` (DateTime, nullable)
- `generated_payload` (Text/JSONB) - AI-generated output
- `final_payload` (Text/JSONB) - Human-confirmed output
- `requirement_tags` (Text)
- `created_at` (DateTime)

### Migration
- `003_add_hitl_review_table.py` - Creates hitl_review table with proper indexes

## Services Added

### AGN1Service (`app/services/agents/agn1_service.py`)
Methods:
- `extract_attributes(case_id, normalized_fields)` - Execute ATS2 extraction step, returns HITLReview
- `classify_need(case_id, confirmed_attributes)` - Execute ATS3 classification step, returns HITLReview

Extraction payload structure:
```json
{
  "service_category": {
    "value": "software_development",
    "source_excerpt": "Inferred from title...",
    "confidence": 0.85,
    "lineage": "ai_generated"
  },
  "estimated_duration": {
    "value": "6_months",
    "source_excerpt": "Derived from...",
    "confidence": 0.70,
    "lineage": "ai_generated"
  },
  "required_skills": {
    "value": ["Python", "React"],
    "source_excerpt": "Extracted from...",
    "confidence": 0.90,
    "lineage": "directly_sourced"
  }
}
```

Classification payload structure:
```json
{
  "ai_verdict": "it_service",
  "confidence_score": 0.88,
  "rationale_inputs": {
    "duration_indicator": "6_months",
    "skills_count": 2,
    "complexity_score": 0.75
  },
  "reasoning": "Classified as it_service based on..."
}
```

### HITLService (`app/services/reviews/hitl_service.py`)
Methods:
- `open_review(case_id, review_type, generated_payload, assigned_role)` - Create pending review
- `apply_decision(review_id, decision, reviewer_id, edited_payload?)` - Apply reviewer decision

Decisions:
- `approve` - Accept generated payload as-is
- `edit` - Accept with modifications (requires edited_payload)
- `reject` - Reject and require rework
- `override` - Override classification verdict (requires edited_payload)

### WorkflowOrchestratorService Extended
New methods:
- `initialize_workflow_state(case_id)` - Initialize/verify workflow state
- `advance_to_extraction(case_id, actor_id?)` - Advance case to extraction_pending and trigger AGN1 extraction

## Repositories Added

### ReviewRepository (`app/repositories/review_repository.py`)
Methods:
- `get_by_id(review_id)`
- `get_by_case_and_type(case_id, review_type, status?)`
- `get_pending_for_case(case_id)`
- `get_latest_by_case_and_type(case_id, review_type)`

### CaseRepository Extended
New methods:
- `get_by_workflow_state(workflow_state, limit, offset)` - Filter cases by workflow state
- `count_by_workflow_state(workflow_state)` - Count cases in specific state

## Seed Data

Sample cases created with various workflow states:
1. `CASE-2026-00001` - intake_normalized (Cloud Infrastructure)
2. `CASE-2026-00002` - intake_normalized (Security Assessment)
3. `CASE-2026-00003` - intake_pending (incomplete)
4. `CASE-2026-00004` - extraction_pending (Application Development) with pending extraction review
5. `CASE-2026-00005` - extraction_approved (Database Administrator) with approved extraction review

## Seed Credentials
- Admin: `admin@example.com` / `admin123`
- Reviewer: `reviewer@example.com` / `reviewer123`
- Manager: `manager@example.com` / `manager123`

## Testing Coverage

### test_agn1_service.py
- Extraction creates pending review with structured attributes
- Classification creates pending review with verdict
- IT service verdict for multi-skill projects
- Single resource verdict for simple needs
- Lineage metadata included for all attributes
- Rationale inputs included in classification

### test_workflow_service.py
- Workflow state initialization
- Advance to extraction creates review
- Workflow events recorded for state transitions
- Error handling for missing cases/normalized needs
- Complete workflow state progression

## Frontend Integration Points

The frontend can now:
1. **List cases by workflow state** - Filter intake queue by `workflow_state` parameter
2. **Display workflow progress** - Show current state and next action for each case
3. **Pending extraction reviews** - Query cases with `workflow_state=extraction_pending`
4. **Approved extractions** - Query cases with `workflow_state=extraction_approved`

Example API calls:
- All cases: `GET /api/v1/cases`
- Intake normalized: `GET /api/v1/cases?workflow_state=intake_normalized`
- Extraction pending: `GET /api/v1/cases?workflow_state=extraction_pending`
- Extraction approved: `GET /api/v1/cases?workflow_state=extraction_approved`

## Requirements Implemented
- REQ-DOMAIN-001: Case status initialization with workflow state
- REQ-DOMAIN-002: Structured need attribute extraction with source excerpts
- REQ-DOMAIN-003: Extraction review and correction gate (service layer ready)
- FR-003: Case displays current state and next action
- FR-005: System generates structured attribute set

## Next Steps for UI Task
The UI task can now implement:
1. **Intake Queue with Filters** - Use `GET /api/v1/cases?workflow_state={state}` to filter by state
2. **Case Overview** - Display `workflow_state` and `next_action` fields
3. **Extraction Review Gate** - Fetch pending extraction reviews and display attributes with source excerpts
4. **Review Decision Submission** - Call `HITLService.apply_decision()` to approve/edit/reject extraction

## Verification
- Migration 003 applied successfully
- All AGN1 service tests pass (7 tests)
- All workflow service tests pass (9 tests)
- Seed data creates cases in extraction_pending and extraction_approved states
- Case list endpoint supports workflow_state filter parameter
