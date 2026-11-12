# TASK-9 Handoff: Backend Feature B7 - Supplier Adjustments and Count Validation

## Completed Scope

This task implemented supplier adjustment capture (ATS10) and supplier-count validation (ATS9) with database schema, adapters, services, repositories, endpoints, tests, and seed data.

## Database Schema

### Tables Created

**supplier_adjustment**
- `id` (PK)
- `case_id` (FK → need_case.id)
- `supplier_id` (FK → supplier.id)
- `change_type` (VARCHAR: 'add' or 'remove')
- `rationale` (TEXT, nullable)
- `actor_id` (VARCHAR: User ID or system identifier)
- `created_at` (TIMESTAMP with timezone)
- `resulting_supplier_count` (INTEGER)
- `requirement_tags` (TEXT, nullable)
- Indexes: case_id, supplier_id, created_at

**policy_validation**
- `id` (PK)
- `case_id` (FK → need_case.id)
- `validation_type` (VARCHAR: e.g., 'supplier_count')
- `supplier_count` (INTEGER)
- `validation_result` (VARCHAR: 'valid', 'invalid_low', 'invalid_high')
- `rule_snapshot` (TEXT: JSONB snapshot of rules applied)
- `validated_at` (TIMESTAMP with timezone)
- `requirement_tags` (TEXT, nullable)
- Indexes: case_id, validated_at

Migration: `008_add_adjustment_and_validation_tables.py`

## API Endpoints

### POST /api/v1/cases/{caseId}/adjustments

**Purpose:** Capture supplier adjustment (add or remove supplier)

**Request Body:**
```json
{
  "supplier_id": 123,
  "change_type": "add",  // or "remove"
  "rationale": "Business unit requested additional supplier"
}
```

**Response (200 OK):**
```json
{
  "adjustment_id": 456,
  "case_id": 1,
  "supplier_id": 123,
  "change_type": "add",
  "rationale": "Business unit requested additional supplier",
  "actor_id": "1",
  "resulting_supplier_count": 4,
  "created_at": "2026-11-12T10:30:00Z"
}
```

**Behavior:**
- Records every supplier addition or removal as a structured adjustment entry
- Captures actor (current user ID), timestamp, change type, and rationale
- Recalculates resulting supplier count after each change
- Adjustment history remains visible before and after finalization
- Returns 400 for invalid change_type (not 'add' or 'remove')
- Returns 404 if case not found
- Returns 400 if case has no longlist proposal

### POST /api/v1/cases/{caseId}/validations/supplier-count

**Purpose:** Validate supplier count against the 3-6 rule

**Request Body:** None (POST triggers validation)

**Response (200 OK):**
```json
{
  "validation_id": 789,
  "case_id": 1,
  "validation_type": "supplier_count",
  "supplier_count": 4,
  "validation_result": "valid",
  "rule_snapshot": "{\"rule_type\":\"supplier_count_band\",\"min_suppliers\":3,\"max_suppliers\":6,\"applied_count\":4,\"rule_version\":\"1.0\"}",
  "validation_message": "Longlist has 4 supplier(s), within valid range of 3-6",
  "validated_at": "2026-11-12T10:35:00Z"
}
```

**Validation Results:**
- `valid`: 3-6 suppliers (target band)
- `invalid_low`: < 3 suppliers (blocks finalization)
- `invalid_high`: > 6 suppliers (flags against target-band rule)

**Behavior:**
- Invokes AGN5 rule engine with TOL4 adapter to enforce 3-6 supplier count rule
- Creates policy_validation record with validation result and rule snapshot
- Validation outcomes stored and visible to user
- Returns 404 if case not found
- Returns 400 if case has no longlist proposal

## Architecture Components

### Adapters

**TOL4LonglistValidationAdapter** (`app/adapters/tol4_longlist_validation_adapter.py`)
- Deterministic supplier-count rule validator
- Implements 3-6 supplier count rule (FR-021)
- Returns validation result with rule snapshot for audit compliance
- No AI behavior - pure deterministic logic

### Services

**AGN3Service** (`app/services/agents/agn3_service.py`)
- Longlist Finalization and Tender Agent (ATS10, ATS11, ATS12)
- `capture_adjustment()` method records add/remove actions and recalculates count
- Validates change_type ('add' or 'remove')
- Returns adjustment result with resulting_supplier_count

**LonglistPolicyService** (`app/services/policy/longlist_policy_service.py`)
- `validate_citation_coverage()` checks all suppliers have citations
- `validate_supplier_count()` invokes AGN5/TOL4 and creates policy_validation record
- Returns validation result with supplier_count, validation_result, rule_snapshot

**AGN5RuleEngine** (updated in `app/services/rules/agn5_rule_engine.py`)
- Added `validate_supplier_count_with_tol4()` method
- Invokes TOL4 adapter and returns full validation result dictionary
- Integrates TOL4 adapter into deterministic rule engine

### Repositories

**AdjustmentRepository** (`app/repositories/adjustment_repository.py`)
- `get_by_id()` - Get adjustment by ID
- `list_by_case()` - List all adjustments for a case (ordered by created_at desc)
- `create()` - Create new adjustment record

**ValidationRepository** (`app/repositories/validation_repository.py`)
- `get_by_id()` - Get validation by ID
- `get_latest_by_case()` - Get latest validation for a case by type
- `list_by_case()` - List all validations for a case (ordered by validated_at desc)
- `create()` - Create new validation record

## Seed Data

### Supplier Adjustments

**CASE-2026-00001:**
- Adjustment 1: Remove SUP-CLOUD-001 (rationale: "Supplier temporarily suspended due to compliance review")
- Adjustment 2: Add SUP-CLOUD-001 back (rationale: "Compliance review completed, supplier reinstated")

**CASE-2026-00002:**
- Adjustment 3: Add SUP-SEC-002 (rationale: "Business unit requested additional security specialist")

### Policy Validations

**CASE-2026-00002:** invalid_low (2 suppliers, below minimum of 3)
**CASE-2026-00001:** valid (supplier count within 3-6 range)
**CASE-2026-00004:** invalid_high (8 suppliers, above maximum of 6)

All validation results seeded: `valid`, `invalid_low`, `invalid_high`

## Test Coverage

### Integration Tests

**test_adjustments_integration.py** (7 tests)
- Add adjustment for new supplier
- Remove adjustment for existing supplier
- Adjustment history remains visible
- Adjustment captures actor and timestamp
- Invalid change_type rejected
- Case not found returns 404
- No proposal returns 400

**test_validation_integration.py** (6 tests)
- Valid supplier count (3-6)
- Invalid low supplier count (< 3)
- Invalid high supplier count (> 6)
- Validation outcome stored in database
- Rule snapshot captured for audit
- Case not found returns 404

**test_agn3_service.py** (7 tests)
- Capture adjustment add new supplier
- Capture adjustment remove existing supplier
- Add duplicate supplier (no count change)
- Remove non-existent supplier (no count change)
- Invalid change_type raises ValueError
- No proposal raises ValueError

Total: 20 tests

## Workflow Impact

### Adjustment Capture
- Every supplier addition or removal is recorded as structured adjustment entry
- Adjustment captures actor, timestamp, change type, and rationale
- System recalculates resulting supplier count after each change
- Adjustment history remains visible before and after finalization

### Supplier-Count Validation
- System blocks finalization when longlist contains fewer than 3 suppliers
- System identifies 3-6 suppliers as valid target range
- System flags longlists with more than 6 suppliers as invalid against target-band rule
- Validation outcomes stored and displayed to user

## Requirements Traceability

- **REQ-DOMAIN-008**: Structured Capture of Add/Remove Supplier Adjustments ✓
- **REQ-DOMAIN-009**: Supplier-Count Rule Validation ✓
- **FR-020**: Business-unit supplier adjustment capture ✓
- **FR-021**: Supplier-count validation before finalization ✓

## Related Tasks

- Builds on TASK-8 (Panel Mapping and Longlist Proposal Generation)
- Prepares for TASK-10+ (Locking and Tender Dispatch)
