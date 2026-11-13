# TASK-8 Handoff: Backend Feature B6 - Finalize longlist and lock record, Assemble and dispatch tender

## Implemented Endpoints

### POST /api/v1/longlists/{longlist_id}/lock
Finalize and lock longlist immutably (ATS11).

**Request:**
```json
{
  "expected_validation_verdict": "pass",
  "supplier_ids": ["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
  "finalized_by": "longlist_finalization_owner@example.com"
}
```

**Response (200):**
```json
{
  "longlist_id": "uuid",
  "need_id": "uuid",
  "suppliers": ["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
  "locked": true,
  "locked_at": "2026-11-13T10:00:00Z",
  "change_history": [
    {
      "action": "lock",
      "timestamp": "2026-11-13T10:00:00Z",
      "actor": "longlist_finalization_owner@example.com",
      "supplier_ids": ["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
      "validation_verdict": "pass"
    }
  ],
  "validation_count": 4,
  "correlation_id": "uuid"
}
```

**Behavior:**
- Revalidates supplier set using ATS9 (3-6 supplier rule)
- Locks longlist immutably with locked=true, locked_at timestamp
- Records change_history with lock event
- Writes audit event with step_code=ATS11, agent_code=AGN3, tool_code=TOL4
- Rejects if validation_verdict not "pass"
- Rejects if longlist already locked
- Returns 400 if validation fails, 404 if longlist not found

### POST /api/v1/tenders/dispatch
Dispatch tender to all suppliers on locked longlist (ATS12).

**Request:**
```json
{
  "longlist_id": "uuid",
  "tender_template": "TEMPLATE-001",
  "supplier_contacts": [
    {
      "supplier_id": "SUP-0231",
      "contact_email": "tenders@sup0231.example.com",
      "contact_name": "Tender Team"
    },
    {
      "supplier_id": "SUP-0118",
      "contact_email": "rfp@sup0118.example.com",
      "contact_name": "RFP Manager"
    }
  ]
}
```

**Response (201):**
```json
{
  "dispatch_batch_id": "DSP-2024-11-13-abc12345",
  "longlist_id": "uuid",
  "supplier_dispatches": [
    {
      "dispatch_id": "uuid",
      "supplier_id": "SUP-0231",
      "tender_package_ref": "TND-{longlist_id}-SUP-0231-abc12345",
      "dispatch_status": "delivered",
      "retry_count": 0,
      "delivery_confirmation_ref": "CONF-000001",
      "escalation_opened": false,
      "last_attempt_at": "2026-11-13T10:05:00Z"
    },
    {
      "dispatch_id": "uuid",
      "supplier_id": "SUP-0118",
      "tender_package_ref": "TND-{longlist_id}-SUP-0118-def67890",
      "dispatch_status": "delivered",
      "retry_count": 0,
      "delivery_confirmation_ref": "CONF-000002",
      "escalation_opened": false,
      "last_attempt_at": "2026-11-13T10:05:00Z"
    }
  ],
  "correlation_id": "uuid"
}
```

**Behavior:**
- Blocks dispatch when longlist unlocked, empty, or missing contacts
- Dispatches to every supplier via TOL6 adapter
- Records per-supplier dispatch_status: pending, retrying, delivered, failed, escalated
- Tracks retry_count, delivery_confirmation_ref, tender_package_ref, escalation_opened, last_attempt_at
- Writes audit event with step_code=ATS12, agent_code=AGN3, tool_code=TOL6
- Idempotent retry for failures
- Escalates after MAX_RETRY_COUNT (3) attempts
- Returns 400 if longlist not locked/empty/missing contacts, 404 if longlist not found

### GET /api/v1/workflows/{need_id}/audit-events
Retrieve audit trail for a workflow need.

**Response (200):**
```json
{
  "need_id": "uuid",
  "audit_events": [
    {
      "audit_event_id": "uuid",
      "step_code": "ATS1",
      "agent_code": "AGN5",
      "tool_code": "TOL1",
      "actor_type": "system",
      "actor_id": "intake-service",
      "outcome": "success",
      "payload_ref": "{\"need_id\": \"...\"}",
      "correlation_id": "uuid",
      "created_at": "2026-11-03T10:00:00Z"
    },
    {
      "audit_event_id": "uuid",
      "step_code": "ATS11",
      "agent_code": "AGN3",
      "tool_code": "TOL4",
      "actor_type": "human",
      "actor_id": "longlist_finalization_owner@example.com",
      "outcome": "locked",
      "payload_ref": "{\"longlist_id\": \"...\"}",
      "correlation_id": "uuid",
      "created_at": "2026-11-13T10:00:00Z"
    }
  ],
  "total_count": 2,
  "correlation_id": "uuid"
}
```

**Behavior:**
- Returns all audit events for a need, ordered by created_at
- Includes step_code, agent_code, tool_code, actor_type, actor_id, outcome, payload_ref
- Returns 404 if need not found
- Empty list if no audit events exist

### GET /health
Liveness probe.

**Response (200):**
```json
{
  "status": "healthy"
}
```

### GET /ready
Readiness probe with database connectivity check.

**Response (200):**
```json
{
  "status": "ready"
}
```

**Response (500) when DB unavailable:**
```json
{
  "status": "not ready",
  "error": "connection error details"
}
```

## Seed Data

### Locked Longlist: LL-2024-0402
- **Longlist ID:** `00000000-0000-0000-0000-000000000402`
- **Need ID:** `00000000-0000-0000-0000-000000000008`
- **Suppliers:** SUP-0231, SUP-0118, SUP-0045, SUP-0518, SUP-0412 (5 suppliers)
- **Locked:** true
- **Locked by:** longlist_finalization_owner@example.com
- **Validation verdict:** pass
- **Change history:**
  - Add SUP-0518 (niche provider with quantum-resistant encryption)
  - Remove SUP-0307 (overlapping capability with SUP-0412)
  - Lock event with validation_count=5

### Tender Dispatches: DSP-2024-0402-01
Batch dispatches for LL-2024-0402:

1. **SUP-0231**
   - Status: delivered
   - Confirmation: CONF-0402-001
   - Retry count: 0

2. **SUP-0118**
   - Status: delivered
   - Confirmation: CONF-0402-002
   - Retry count: 0

3. **SUP-0045**
   - Status: delivered
   - Confirmation: CONF-0402-003
   - Retry count: 0

4. **SUP-0518**
   - Status: retrying
   - Retry count: 2
   - Error: "Temporary email server unavailable, retrying"
   - Escalation: false

5. **SUP-0412**
   - Status: escalated
   - Retry count: 4
   - Error: "Retry exhausted after 4 attempts, escalated to manual intervention"
   - Escalation: true

### Audit Events
Seed data includes audit events for all steps including:
- ATS1 (intake normalization)
- ATS3 (classification review)
- ATS11 (longlist lock)
- ATS4 (VMS handoff for single-resource needs)
- ATS9 (validation failures)

## Backend Flows

### ATS11: Longlist Lock Flow
1. Accept longlist_id, expected_validation_verdict (must be "pass"), supplier_ids, finalized_by
2. Retrieve longlist, verify unlocked
3. Revalidate supplier set using TOL4ValidationUtil (3-6 rule)
4. If validation fails: write audit event, reject with 400
5. Update longlist: locked=true, locked_at, locked_by, validation_verdict_at_lock
6. Append lock event to change_history
7. Commit transaction
8. Write audit event: step_code=ATS11, agent_code=AGN3, outcome=longlist_locked
9. Return longlist_id, need_id, suppliers, locked=true, locked_at, change_history, validation_count

**Error cases:**
- Longlist not found → 404
- Already locked → 400
- Validation verdict not "pass" → 400
- Validation fails (count < 3 or > 6) → 400 with violations

### ATS12: Tender Dispatch Flow
1. Accept longlist_id, tender_template, supplier_contacts array
2. Retrieve longlist, verify locked
3. Parse suppliers from locked longlist JSON
4. Block dispatch if: unlocked, empty, missing contacts
5. Generate dispatch_batch_id
6. For each supplier:
   a. Build tender_package_ref
   b. Call TOL6DispatchAdapter.dispatch_tender()
   c. Record dispatch_status: delivered, retrying, failed
   d. Create TenderDispatch record with all fields
7. Write audit event: step_code=ATS12, agent_code=AGN3, outcome=tender_dispatched
8. Return dispatch_batch_id, longlist_id, supplier_dispatches array

**Retry logic:**
- Failed dispatches tracked with retry_count
- Idempotent retry via retry_failed_dispatch() method
- Escalates after MAX_RETRY_COUNT (3) attempts
- Escalated dispatches marked with escalation_opened=true

**Error cases:**
- Longlist not found → 404
- Longlist not locked → 400
- Empty supplier list → 400
- Missing supplier contacts → 400 with missing supplier IDs

## Data Models

### Longlist (existing, used by ATS11)
- id (UUID, PK)
- need_id (UUID, FK needs.id)
- proposal_id (UUID, FK longlist_proposals.id, nullable)
- suppliers (Text, JSON array)
- **locked** (Boolean, NOT NULL, default false)
- **locked_at** (DateTime with timezone, nullable)
- **locked_by** (String 100, nullable)
- **validation_verdict_at_lock** (String 50, nullable)
- **change_history** (Text, JSON array, nullable)
- created_at (DateTime with timezone)
- updated_at (DateTime with timezone)

### TenderDispatch (existing, used by ATS12)
- id (UUID, PK)
- longlist_id (UUID, FK longlists.id)
- dispatch_batch_id (String 100, indexed)
- supplier_id (String 100, indexed)
- supplier_contact (String 500, nullable)
- dispatch_status (String 50, NOT NULL, default "pending")
- retry_count (Integer, NOT NULL, default 0)
- delivery_confirmation_ref (String 200, nullable)
- error_detail (Text, nullable)
- created_at (DateTime with timezone)
- updated_at (DateTime with timezone)

### AuditEvent (existing, used by all operations)
- id (UUID, PK)
- need_id (UUID, nullable, indexed)
- correlation_id (String 100, indexed)
- step_code (String 50, indexed)
- agent_code (String 50, nullable)
- tool_code (String 50, nullable)
- actor_type (String 50, NOT NULL)
- actor_id (String 100, indexed)
- outcome (String 50, NOT NULL)
- severity (String 50, default "info")
- payload_ref (Text, nullable)
- created_at (DateTime with timezone, indexed)

## Authentication
All endpoints require JWT authentication. Use default seed credentials:
- `longlist_finalization_owner@example.com` / `Password123!` (for lock operations)
- `procurement_reviewer@example.com` / `Password123!` (for viewing audit events)

## Testing
Comprehensive test coverage provided:
- Unit tests: test_longlist_lock_service.py, test_tender_dispatch_service.py, test_workflow_query_service.py
- Integration tests: test_tender_integration.py
- All tests verify error cases, validation rules, and audit event creation
