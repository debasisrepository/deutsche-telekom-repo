# TASK-3 Handoff: Backend Intake and Review Features

## Endpoints Added

### POST /api/v1/intake/needs
Creates a new need intake submission (ATS1).

**Request:**
```json
{
  "business_unit_id": "string",
  "channel_type": "rfp|email|phone|supplier_offer",
  "raw_artifact_ref": "string (optional)",
  "normalized_payload_json": "string (optional)"
}
```

**Response (201):**
```json
{
  "need_id": "uuid",
  "status": "normalized",
  "correlation_id": "string"
}
```

### GET /api/v1/intake/needs
Lists all needs for intake monitoring table (ordered by arrival_timestamp descending).

**Query Parameters:**
- `limit`: integer (optional, default 100)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "business_unit_id": "string",
    "channel_type": "rfp|email|phone|supplier_offer",
    "arrival_timestamp": "datetime",
    "raw_artifact_ref": "string",
    "normalized_payload_json": "string",
    "status": "string",
    "classification_verdict": "string",
    "classification_confidence": "number",
    "evidence_limited_flag": "boolean",
    "correlation_id": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### GET /api/v1/intake/needs/{need_id}
Retrieves need workflow state and normalized intake view.

**Response (200):**
```json
{
  "id": "uuid",
  "business_unit_id": "string",
  "channel_type": "rfp|email|phone|supplier_offer",
  "arrival_timestamp": "datetime",
  "raw_artifact_ref": "string",
  "normalized_payload_json": "string",
  "status": "string",
  "classification_verdict": "string",
  "classification_confidence": "number",
  "evidence_limited_flag": "boolean",
  "correlation_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### POST /api/v1/reviews/needs/{need_id}/attributes
Captures ATS2 reviewer decision on extracted attributes.

**Request:**
```json
{
  "review_decision": "approve|modify|reject",
  "need_attributes": {
    "service_type": "string (optional)",
    "scope_description": "string (optional)",
    "estimated_volume_duration": "string (optional)",
    "required_skills": "string (JSON, optional)",
    "budget_indication": "string (optional)",
    "delivery_location": "string (optional)",
    "field_confidence": "string (JSON, optional)"
  },
  "reviewer_notes": "string (optional)"
}
```

**Response (200):**
```json
{
  "need_id": "uuid",
  "review_decision": "approve|modify|reject",
  "next_workflow_status": "string",
  "need_attributes_id": "uuid"
}
```

## Request/Response Shapes

### Need
- `id` (need_id): UUID
- `business_unit_id`: string
- `channel_type`: rfp | email | phone | supplier_offer
- `arrival_timestamp`: datetime (ISO 8601)
- `raw_artifact_ref`: string (optional)
- `normalized_payload_json`: string (PII masked)
- `status`: normalized | extraction_review_pending | classification_review_pending | error
- `classification_verdict`: string (optional)
- `classification_confidence`: number (optional)
- `evidence_limited_flag`: boolean (default false)
- `correlation_id`: string
- `created_at`: datetime
- `updated_at`: datetime

### NeedAttributes
- `id` (need_attributes_id): UUID
- `need_id`: UUID (FK to needs.id)
- `service_type`: string (optional)
- `scope_description`: text (optional)
- `estimated_volume_duration`: string (optional)
- `required_skills`: JSON string (optional)
- `budget_indication`: string (optional)
- `delivery_location`: string (optional)
- `field_confidence`: JSON string (optional)
- `schema_valid`: boolean (default true)
- `review_status`: approved | modified_approved | rejected (optional)
- `reviewed_by`: string (optional)
- `reviewed_at`: datetime (optional)
- `created_at`: datetime
- `updated_at`: datetime

### Review Decision Flow
- **approve**: Advances to `classification_review_pending`
- **modify**: Updates/creates attributes, advances to `classification_review_pending`
- **reject**: Returns to `extraction_review_pending` for remediation

## Seed Data

Seed needs are created with the following IDs (deterministic):

- **NEED-2024-0418**: RFP channel, normalized status
- **NEED-2024-0417**: Email channel, extraction_review_pending status
- **NEED-2024-0412**: Phone channel, error status
- **NEED-2024-0416**: Supplier offer channel, normalized status

Additional seed records cover each channel type and various workflow states.

## Backend Flows

### ATS1 Intake Flow
1. Validate request schema (channel_type enum, required fields)
2. Mask PII in `normalized_payload_json` (emails, phone numbers)
3. Create Need record with `status="normalized"`, `evidence_limited_flag=false`
4. Write AuditEvent with `step_code="ATS1"`, `agent_code="AGN5"`, `outcome="success"`
5. Commit transaction
6. Return need_id, status, correlation_id

**Error Handling:**
- Schema validation failure → 400 Bad Request
- Audit write failure → rollback, re-raise
- Unhandled exception → 500 Internal Server Error

### ATS2 Review Flow
1. Retrieve Need and NeedAttributes by need_id
2. Apply review decision:
   - **approve**: Mark `review_status="approved"`, advance to `classification_review_pending`
   - **modify**: Create/update attributes with modified values, mark `review_status="modified_approved"`, advance to `classification_review_pending`
   - **reject**: Mark `review_status="rejected"`, return to `extraction_review_pending`
3. Set `reviewed_by` (reviewer_id) and `reviewed_at` (current UTC)
4. Write AuditEvent with `step_code="ATS2"`, `actor_type="human"`, `outcome=review_decision`
5. Commit transaction
6. Return need_id, review_decision, next_workflow_status, need_attributes_id

**Error Handling:**
- Need not found → 400 Bad Request
- No attributes to approve → 400 Bad Request
- Modify without attributes payload → 400 Bad Request
- Invalid review_decision → 400 Bad Request
- Unhandled exception → 500 Internal Server Error

## Notes
- All endpoints use `/api/v1` prefix as per architecture contract
- Correlation IDs are propagated through audit events for tracing
- PII masking uses regex patterns to replace emails and phone numbers with `[EMAIL_MASKED]` and `[PHONE_MASKED]`
- Auth middleware is placeholder - currently does not enforce authentication (TODO for frontend integration)
- TOL1 adapter is stub implementation - production would integrate with actual intake channels
