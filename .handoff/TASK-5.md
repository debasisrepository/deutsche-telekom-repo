# TASK-5 Handoff: Extraction and Classification Review Endpoints

## Overview
Backend Feature B3 implementation covering extraction review (REQ-DOMAIN-003) and classification review (REQ-DOMAIN-005) with full workflow integration.

## API Endpoints

All endpoints require authentication via JWT Bearer token.

### POST /api/v1/cases/{caseId}/reviews/extraction

Apply extraction review decision for a case.

**Path Parameters:**
- `caseId` (integer) - Case identifier

**Request Body:**
```json
{
  "decision": "approve|edit|reject",
  "edited_attributes": {
    "service_category": {
      "value": "consulting",
      "source_excerpt": "Corrected by reviewer",
      "confidence": 1.0,
      "lineage": "human_corrected"
    }
  }
}
```

**Fields:**
- `decision` (required) - One of: `approve`, `edit`, `reject`
- `edited_attributes` (optional) - Required for `edit` decision. Dictionary of corrected attributes.

**Response (200 OK):**
```json
{
  "review_id": 1,
  "case_id": 4,
  "review_type": "extraction",
  "status": "approved",
  "decision": "approve",
  "reviewer_id": 2,
  "reviewed_at": "2026-11-12T14:30:00Z",
  "next_workflow_state": "extraction_approved",
  "next_action": "classification_pending"
}
```

**Workflow Impact:**
- `approve`: Advances case to `extraction_approved` state, triggers classification
- `edit`: Same as approve, but with corrected attributes
- `reject`: Sets review to `rejected` status, requires rework

---

### POST /api/v1/cases/{caseId}/reviews/classification

Apply classification review decision for a case.

**Path Parameters:**
- `caseId` (integer) - Case identifier

**Request Body:**
```json
{
  "decision": "confirm|override",
  "confirmed_verdict": "single_resource|it_service"
}
```

**Fields:**
- `decision` (required) - One of: `confirm`, `override`
- `confirmed_verdict` (optional) - Required for `override` decision. One of: `single_resource`, `it_service`

**Response (200 OK):**
```json
{
  "review_id": 2,
  "case_id": 6,
  "review_type": "classification",
  "status": "approved",
  "decision": "approve",
  "reviewer_id": 2,
  "reviewed_at": "2026-11-12T14:35:00Z",
  "next_workflow_state": "classification_approved",
  "next_action": "evidence_retrieval_pending"
}
```

**Workflow Impact:**
- `confirm` with `it_service`: Routes to evidence retrieval
- `confirm` with `single_resource`: Routes to VMS handoff
- `override`: Uses corrected verdict for routing

**Classification Result:**
Creates or updates `classification_result` record tracking:
- `ai_verdict` - Original AI classification
- `confirmed_verdict` - Final confirmed classification
- `overridden` - Boolean flag indicating if verdict was overridden
- `confidence_score` - AI confidence score
- `rationale_inputs` - JSONB with rationale metadata

---

## Seed Data

The seed script creates 6 sample cases demonstrating different workflow states:

### Cases with Extraction Review
- **CASE-2026-00004** - State: `extraction_pending`, Action: `extraction_review_required`
  - Pending extraction review with generated attributes
  - Use this case to test extraction review decisions

### Cases with Classification Review
- **CASE-2026-00006** - State: `classification_pending`, Action: `classification_review_required`
  - Pending classification review with AI verdict: `it_service`
  - Use this case to test classification review decisions

### Other States
- **CASE-2026-00001** - State: `intake_normalized` (complete intake)
- **CASE-2026-00002** - State: `intake_normalized` (complete intake)
- **CASE-2026-00003** - State: `intake_pending` (incomplete intake)
- **CASE-2026-00005** - State: `extraction_approved`, Action: `classification_pending` (extraction approved, ready for classification)

## Seed Credentials

**Reviewer Account:**
- Email: `reviewer@example.com`
- Password: `reviewer123`
- Role: `reviewer`

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`
- Role: `admin`

## Database Schema

### classification_result Table
- `id` (INTEGER PRIMARY KEY) - Auto-increment identifier
- `case_id` (INTEGER UNIQUE FK) - Foreign key to need_case.id
- `ai_verdict` (VARCHAR 50) - AI classification verdict
- `confirmed_verdict` (VARCHAR 50) - Final confirmed verdict
- `confidence_score` (FLOAT) - AI confidence score
- `rationale_inputs` (TEXT) - JSONB rationale metadata
- `overridden` (BOOLEAN) - Override flag
- `requirement_tags` (TEXT) - Requirement traceability
- `created_at` (DATETIME) - Record creation timestamp

### Migration
- **004_add_classification_result_table.py** - Creates classification_result table with indexes

## Review Decisions and Logging

### Extraction Review (REQ-DOMAIN-003)
The system logs:
- Chosen action (`approve`, `edit`, `reject`)
- Resulting attribute set (final_payload in hitl_review)
- Workflow events and audit logs
- Generated-versus-final distinction preserved

### Classification Review (REQ-DOMAIN-005)
The system records:
- Original AI verdict
- Override action (if applicable)
- Final confirmed classification
- Classification result in dedicated table
- Final classification controls downstream routing

## Workflow States

### After Extraction Review
- **Approved/Edited** → `extraction_approved`, triggers classification
- **Rejected** → Remains in review state, requires rework

### After Classification Review
- **Confirmed as it_service** → Routes to evidence retrieval (`evidence_retrieval_pending`)
- **Confirmed as single_resource** → Routes to VMS handoff (`vms_handoff_pending`)
- **Overridden** → Uses corrected verdict for routing

## Testing

Run integration tests:
```bash
cd /repos/deutsche-telekom-repo/backend
.venv/bin/python -m pytest tests/test_reviews_integration.py -v
```

Test coverage includes:
- Extraction review: approve without modification
- Extraction review: edit with corrected attributes
- Extraction review: reject for rework
- Classification review: accept AI verdict
- Classification review: override with corrected verdict
- Downstream routing based on confirmed classification
- Validation of required fields per decision type

## Implementation Files

**Models:**
- `/repos/deutsche-telekom-repo/backend/app/models/classification_result.py`

**Routers:**
- `/repos/deutsche-telekom-repo/backend/app/routers/reviews.py`

**Services:**
- `/repos/deutsche-telekom-repo/backend/app/services/workflow/orchestrator_service.py` (extended)
- `/repos/deutsche-telekom-repo/backend/app/services/agents/agn1_service.py` (classify_need method)

**Migrations:**
- `/repos/deutsche-telekom-repo/backend/alembic/versions/004_add_classification_result_table.py`

**Tests:**
- `/repos/deutsche-telekom-repo/backend/tests/test_reviews_integration.py`

**Seed:**
- `/repos/deutsche-telekom-repo/backend/app/seed.py` (extended with classification-review case)
