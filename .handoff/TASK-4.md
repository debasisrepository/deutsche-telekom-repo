# TASK-4 Handoff: Classification Review and VMS Handoff

## Implemented Endpoints

### POST /api/v1/reviews/needs/{need_id}/classification
ATS3 classification review endpoint.

**Request:**
```json
{
  "review_decision": "approve|modify|reject",
  "classification_verdict": "single_resource|it_service",
  "classification_confidence": 0.85,
  "rationale": "Clear single-resource need based on scope",
  "exemplars_referenced": ["EX-001", "EX-002"],
  "escalation_required": false
}
```

**Response (200):**
```json
{
  "classification_review_id": "uuid",
  "need_id": "uuid",
  "review_decision": "approve",
  "classification_verdict": "single_resource",
  "classification_confidence": 0.85,
  "rationale": "Clear single-resource need based on scope",
  "exemplars_referenced": ["EX-001", "EX-002"],
  "escalation_required": false,
  "next_workflow_status": "classified_single_resource",
  "reviewed_by": "reviewer@example.com",
  "reviewed_at": "2024-11-13T10:30:00Z"
}
```

**Behavior:**
- Enforces allowed verdicts: `single_resource` | `it_service` only
- Low confidence (< 0.70) automatically triggers escalation
- Escalation holds case in `classification_review_pending` status
- Approve/modify with single_resource → status `classified_single_resource`
- Approve/modify with it_service → status `classified_it_service`
- Reject → status `classification_review_pending`
- Logs decision with rationale, exemplars_referenced, escalation_required
- Creates immutable audit event with step_code=ATS3

---

### POST /api/v1/integrations/vms/handoffs
ATS4 VMS handoff execution endpoint.

**Request:**
```json
{
  "need_id": "uuid",
  "classification_verdict": "single_resource",
  "request_payload_json": {
    "contractor_name": "John Doe",
    "skill_set": "Python Developer",
    "duration": "6 months"
  }
}
```

**Response (201):**
```json
{
  "vms_handoff_id": "uuid",
  "need_id": "uuid",
  "handover_confirmation": true,
  "vms_reference_id": "VMS-2024-A3F8E1",
  "response_payload_json": {
    "status": "accepted",
    "vms_ticket_id": "VMS-2024-A3F8E1",
    "received_at": "2024-11-13T10:35:00Z",
    "estimated_processing_time": "2-3 business days"
  },
  "sent_at": "2024-11-13T10:35:00Z",
  "correlation_id": "uuid",
  "workflow_status": "vms_routed_terminal"
}
```

**Behavior:**
- Executes ONLY for reviewed `single_resource` verdict
- Validates need status is `classified_single_resource`
- Validates need classification_verdict is `single_resource`
- Calls TOL5 VMS adapter stub
- Records handover_confirmation and vms_reference_id
- Stores request_payload_json and response_payload_json for audit
- Marks workflow status as `vms_routed_terminal` on success
- Marks workflow status as `vms_handoff_failed` on failure
- Blocks ATS5-ATS12 for this need (terminal routing)
- Creates immutable audit event with step_code=ATS4, tool_code=TOL5
- Failed handoff surfaces with error_detail and escalation

---

## Seed Data

### Classification Reviews
- **NEED-2024-0418**: classified as `it_service`, confidence 0.88, status `classified_it_service`
- **NEED-2024-0391**: classified as `single_resource`, confidence 0.92, status `classified_single_resource`, followed by VMS handoff

### VMS Handoffs
- **NEED-2024-0391**: Successful handoff with vms_reference_id `VMS-2024-118302`, status `vms_routed_terminal`

### Workflow States
- `classification_review_pending`: Need awaiting classification review
- `classified_single_resource`: Need classified as single_resource, eligible for VMS handoff
- `classified_it_service`: Need classified as it_service, continues to ATS5 (evidence retrieval)
- `vms_routed_terminal`: Single-resource need successfully handed off to VMS, blocked from ATS5-12
- `vms_handoff_failed`: VMS handoff failed, escalation required

---

## Backend Flows

### ATS3: Classification Review
1. Reviewer submits classification decision via POST /api/v1/reviews/needs/{need_id}/classification
2. Service validates verdict is `single_resource` or `it_service`
3. If confidence < 0.70, escalation_required set to true automatically
4. If escalation_required and decision is approve/modify, status held at `classification_review_pending`
5. Otherwise:
   - single_resource → status `classified_single_resource`
   - it_service → status `classified_it_service`
6. Creates ClassificationReview record with verdict, confidence, rationale, exemplars_referenced
7. Updates Need with classification_verdict, classification_confidence, status
8. Writes immutable AuditEvent with step_code=ATS3, actor_type=human
9. Returns response with next_workflow_status

### ATS4: VMS Handoff
1. Service receives handoff request via POST /api/v1/integrations/vms/handoffs
2. Validates classification_verdict is `single_resource` (rejects it_service)
3. Validates need.classification_verdict is `single_resource`
4. Validates need.status is `classified_single_resource`
5. Calls TOL5VmsAdapter.send_handoff() with normalized need payload
6. Adapter stub returns handover_confirmation, vms_reference_id, response_payload_json
7. Creates VmsHandoff record with confirmation, reference, payloads, workflow_status
8. Updates Need status to `vms_routed_terminal` (or `vms_handoff_failed` on error)
9. Writes immutable AuditEvent with step_code=ATS4, tool_code=TOL5, actor_type=system
10. Returns response with confirmation and VMS reference
11. Terminal status blocks ATS5-ATS12 from executing for this need

---

## Database Schema

### classification_reviews table
- `id` (uuid, PK)
- `need_id` (uuid, FK needs.id, indexed)
- `classification_verdict` (varchar 50, NOT NULL) - only `single_resource` | `it_service`
- `classification_confidence` (numeric 5,4, nullable)
- `rationale` (text, nullable)
- `review_decision` (varchar 50, nullable) - `approve|modify|reject`
- `reviewer_id` (varchar 100, nullable, indexed)
- `escalation_required` (boolean, NOT NULL, default false)
- `exemplars_referenced` (text, nullable) - JSON array as text
- `created_at` (timestamptz, NOT NULL)
- `updated_at` (timestamptz, NOT NULL)

### vms_handoffs table
- `id` (uuid, PK)
- `need_id` (uuid, FK needs.id, indexed)
- `handover_confirmation` (boolean, NOT NULL, default false)
- `vms_reference_id` (varchar 200, nullable)
- `workflow_status` (varchar 100, NOT NULL, default `vms_routed_terminal`)
- `request_payload_json` (text, nullable)
- `response_payload_json` (text, nullable)
- `error_detail` (text, nullable)
- `created_at` (timestamptz, NOT NULL)
- `updated_at` (timestamptz, NOT NULL)

---

## Key Files

### Services
- `app/services/classification_decision_service.py` - ATS3 classification review service
- `app/services/vms_handoff_service.py` - ATS4 VMS handoff execution service

### Repositories
- `app/repositories/classification_review_repository.py` - ClassificationReview CRUD
- `app/repositories/vms_handoff_repository.py` - VmsHandoff CRUD

### Schemas
- `app/schemas/vms_schemas.py` - Classification and VMS handoff request/response schemas

### Adapters
- `app/adapters/tol5_vms_adapter.py` - TOL5 VMS connector stub (local dev/test)

### Routers
- `app/routers/api/v1/reviews.py` - Extended with classification endpoint
- `app/routers/api/v1/integrations.py` - VMS handoff endpoint

### Tests
- `tests/test_classification_service.py` - ClassificationDecisionService unit tests
- `tests/test_vms_handoff_service.py` - VmsHandoffService unit tests
- `tests/test_vms_integration.py` - Integration tests for both endpoints
- `tests/test_classification_acceptance.py` - FR-003, FR-004 acceptance tests
