# TASK-3 Backend Implementation Handoff

## Overview
Backend multi-channel intake and normalization system with authentication, case management, and audit logging.

## Implemented Endpoints

### Authentication
**POST /api/v1/auth/login**
- Request: `{ "email": string, "password": string }`
- Response: `{ "access_token": string, "user": { "id": int, "email": string, "username": string, "role": string, "is_active": bool, "created_at": datetime, "updated_at": datetime } }`
- Returns JWT token for authenticated requests

### Cases
**POST /api/v1/cases**
- Protected: Requires `Authorization: Bearer {token}` header
- Request: `{ "channel": string, "title": string, "business_unit": string, "description": string, "artifact_type": string, "artifact_ref": string, "submitted_via": string }`
- Response: `CaseDetail` object with normalized need and source artifacts
- Creates new case from intake, performs ATS1 normalization
- Supported channels: `rfp_document`, `email`, `phone_note`, `supplier_offer`

**GET /api/v1/cases/{caseId}**
- Protected: Requires `Authorization: Bearer {token}` header
- Response: `CaseDetail` object with full case information including normalized need and source artifacts
- Returns 404 if case not found

**GET /api/v1/cases**
- Protected: Requires `Authorization: Bearer {token}` header
- Query params: `page` (default: 1), `page_size` (default: 20)
- Response: `{ "items": [CaseListItem], "total": int, "page": int, "page_size": int }`
- Lists all cases with pagination

## Response Shapes

### CaseDetail
```json
{
  "id": int,
  "case_number": "CASE-2026-00001",
  "inbound_channel": "rfp_document|email|phone_note|supplier_offer",
  "workflow_state": "intake_normalized|intake_pending",
  "next_action": string,
  "final_classification": string|null,
  "created_by": int,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z",
  "normalized_need": {
    "id": int,
    "mandatory_fields": {
      "need_title": string,
      "business_unit": string,
      "need_description": string
    },
    "sourced_fields": {
      "source_artifact_ref": string,
      "source_channel_metadata": object
    },
    "derived_fields": object,
    "completeness_score": float
  },
  "source_artifacts": [
    {
      "id": int,
      "artifact_type": string,
      "storage_ref": string,
      "source_channel": string,
      "submitted_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

### CaseListItem
```json
{
  "id": int,
  "case_number": "CASE-2026-00001",
  "inbound_channel": string,
  "workflow_state": string,
  "next_action": string,
  "final_classification": string|null,
  "created_at": "2026-01-15T10:30:00Z"
}
```

## Seed Data

Three default users are seeded for development:

1. **Admin User**
   - Email: `admin@example.com`
   - Password: `admin123`
   - Role: `admin`

2. **Reviewer User**
   - Email: `reviewer@example.com`
   - Password: `reviewer123`
   - Role: `reviewer`

3. **Manager User**
   - Email: `manager@example.com`
   - Password: `manager123`
   - Role: `manager`

Three sample cases are seeded:
- `CASE-2026-00001`: RFP document intake, intake_normalized state
- `CASE-2026-00002`: Email intake, intake_normalized state
- `CASE-2026-00003`: Phone note intake, intake_pending state (incomplete)

## Workflow States

Cases follow a deterministic state machine:
- **intake_pending**: Incomplete mandatory fields, next action: "Complete missing mandatory fields"
- **intake_normalized**: Complete normalization, next action: "Review extracted attributes"

Completeness score threshold: ≥ 0.8 for intake_normalized state

## Technical Notes

- JWT tokens expire after 24 hours
- All timestamps in UTC with timezone info
- JSON fields stored as Text in SQLite, parsed automatically in response schemas
- Audit logging creates workflow_event and audit_log records for all material state changes
- Case numbers generated as CASE-YYYY-NNNNN with sequential numbering per year

## Testing

Run backend tests:
```bash
cd /repos/deutsche-telekom-repo/backend
.venv/bin/python -m pytest tests/test_auth_integration.py -v
.venv/bin/python -m pytest tests/test_cases_integration.py -v
.venv/bin/python -m pytest tests/test_agn5_rule_engine.py -v
.venv/bin/python -m pytest tests/test_workflow_service.py -v
```
