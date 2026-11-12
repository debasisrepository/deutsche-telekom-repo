# TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch

## Endpoints Added

### Lock Endpoint
POST /api/v1/cases/{caseId}/lock

### Dispatch Endpoint
POST /api/v1/cases/{caseId}/dispatch

## Request/Response Shapes

### Lock Request
```json
{
  "actor_id": "user-123"  // optional, defaults to current_user.id
}
```

### Lock Response
```json
{
  "locked_longlist_id": 1,
  "case_id": 1,
  "source_proposal_id": 1,
  "lock_status": "locked",
  "locked_by": "user-123",
  "locked_at": "2026-11-12T12:00:00+00:00",
  "locked_suppliers": [
    {
      "locked_supplier_id": 1,
      "supplier_id": 1,
      "final_rank_position": 1
    }
  ],
  "total_suppliers": 3
}
```

### Dispatch Request
```json
{
  "actor_id": "user-123"  // optional, defaults to current_user.id
}
```

### Dispatch Response
```json
{
  "dispatch_id": 1,
  "dispatch_batch_ref": "BATCH-1-20261112120000",
  "dispatch_status": "success",  // or "partial_failure", "failed"
  "dispatched_by": "user-123",
  "dispatched_at": "2026-11-12T12:00:00+00:00",
  "recipients": [
    {
      "recipient_id": 1,
      "supplier_id": 1,
      "delivery_status": "success",  // or "failed"
      "external_delivery_ref": "TENDER-BATCH-1-20261112120000-SUP-1"
    }
  ],
  "total_recipients": 3
}
```

## Preconditions

### Lock Precondition
- Latest supplier-count validation result must be `valid` (3-6 suppliers)
- Validation must exist via POST /api/v1/cases/{caseId}/validations/supplier-count

If precondition not met:
- HTTP 409 with error message indicating validation requirement

### Dispatch Precondition
- Locked longlist must exist via POST /api/v1/cases/{caseId}/lock

If precondition not met:
- HTTP 409 with error message indicating lock requirement

## Database Schema

### Tables Created

#### locked_longlist
- id (PK, autoincrement)
- case_id (FK need_case.id, unique)
- source_proposal_id (FK longlist_proposal.id)
- lock_status (varchar 50: locked, unlocked)
- locked_by (varchar 50)
- locked_at (timestamp with timezone)
- requirement_tags (text)

#### locked_supplier
- id (PK, autoincrement)
- locked_longlist_id (FK locked_longlist.id)
- supplier_id (FK supplier.id)
- final_rank_position (integer)
- requirement_tags (text)
- created_at (timestamp with timezone)

#### tender_dispatch
- id (PK, autoincrement)
- locked_longlist_id (FK locked_longlist.id, unique)
- dispatch_batch_ref (varchar 100, unique)
- dispatch_status (varchar 50: success, partial_failure, failed)
- dispatched_by (varchar 50)
- dispatched_at (timestamp with timezone)
- requirement_tags (text)

#### tender_dispatch_recipient
- id (PK, autoincrement)
- dispatch_id (FK tender_dispatch.id)
- supplier_id (FK supplier.id)
- delivery_status (varchar 50: success, failed)
- external_delivery_ref (varchar 200, nullable)
- last_attempt_at (timestamp with timezone)
- requirement_tags (text)

## Services

### AGN3Service Extended
- `lock_longlist(case_id, actor_id)` - ATS11: Creates immutable supplier snapshot
- `dispatch_tender(case_id, actor_id)` - ATS12: Invokes TOL6 adapter, records outcomes

### LonglistPolicyService Extended
- `assert_lock_preconditions(case_id)` - Validates lock requirements
- `assert_dispatch_preconditions(case_id)` - Validates dispatch requirements

### TOL6TenderDispatchAdapter (New)
- `dispatch_tender(case_id, locked_suppliers, dispatch_batch_ref)` - Returns per-supplier outcomes
- Stub implementation: 90% success rate for simulation
- Stub-to-live seam documented for production integration

## Repositories

### LockRepository (New)
- `create_locked_longlist()` - Create lock record
- `create_locked_supplier()` - Create locked supplier snapshot
- `get_locked_longlist_by_case()` - Retrieve lock by case ID
- `list_locked_suppliers()` - List suppliers in locked set

### DispatchRepository (New)
- `create_tender_dispatch()` - Create dispatch record
- `create_dispatch_recipient()` - Create per-supplier outcome
- `get_tender_dispatch_by_locked_longlist()` - Retrieve dispatch by lock ID
- `list_dispatch_recipients()` - List recipients for dispatch

## Seed Data

Created locked longlists and dispatch records for demonstration:

### Locked Cases
- **CASE-2026-00002**: Locked but not yet dispatched
  - Has locked_longlist record
  - Has locked_supplier records
  - No tender_dispatch record

- **CASE-2026-00004**: Locked and dispatched successfully
  - Has locked_longlist record
  - Has locked_supplier records
  - Has tender_dispatch record with status "success"
  - All recipients have delivery_status "success"

## Workflow Integration

### Lock Action
1. Policy service validates preconditions (supplier count validation = valid)
2. AGN3 service creates locked_longlist record
3. AGN3 service copies proposal_supplier records to locked_supplier table (immutable snapshot)
4. Lock event recorded with actor and timestamp

### Dispatch Action
1. Policy service validates preconditions (locked longlist exists)
2. AGN3 service retrieves locked suppliers
3. TOL6 adapter invoked with locked supplier set
4. Tender dispatch record created with batch reference
5. Per-supplier delivery outcomes recorded in tender_dispatch_recipient
6. Overall dispatch status determined (success/partial_failure/failed)

## Error Handling

### Lock Errors
- Case not found: HTTP 404
- No longlist proposal: HTTP 400
- Already locked: HTTP 400
- Validation precondition not met: HTTP 409

### Dispatch Errors
- Case not found: HTTP 404
- Not locked: HTTP 409
- Already dispatched: HTTP 400
- No locked suppliers: HTTP 400

## Testing

### Lock Tests (test_lock_integration.py)
- Lock creates immutable snapshot
- Lock precondition requires valid validation
- Lock prevents duplicate locks
- Lock endpoint returns snapshot
- Lock endpoint blocks without validation
- Locked suppliers preserve rank positions

### Dispatch Tests (test_dispatch_integration.py)
- Dispatch creates per-supplier recipients
- Dispatch precondition requires lock
- Dispatch prevents duplicate dispatches
- Dispatch endpoint returns recipients
- Dispatch endpoint blocks without lock
- Dispatch records unique batch reference
- Dispatch status reflects outcomes (success/partial_failure/failed)

## Migration

Migration 009 creates all four tables with proper indexes and foreign keys.
Apply with: `cd backend && alembic upgrade head`

## Requirements Coverage

- REQ-DOMAIN-010: Record Locking Before Tender Dispatch
- REQ-INT-004: Tender Dispatch to Finalized Suppliers
- FR-024: Lock action with preconditions
- FR-026: Dispatch action with per-supplier outcomes
