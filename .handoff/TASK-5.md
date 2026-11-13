# TASK-5 Handoff: Evidence Retrieval and Supplier Count Validation

## API Endpoints Added

### POST /api/v1/evidence/queries
Query historical supplier and project evidence (ATS5).

**Request:**
```json
{
  "need_id": "uuid-string",
  "service_type": "Cloud Infrastructure",
  "required_skills": ["AWS", "Azure", "Kubernetes"],
  "business_unit_id": "BU-NORTH-001",
  "panel_filters": ["IT-CLOUD-PANEL-A"]
}
```

**Response:**
```json
{
  "evidence_items": [
    {
      "supplier_id": "SUP-0231",
      "evidence_type": "historical_sow",
      "source_system": "SEED",
      "source_reference": "SOW-2022-0871",
      "service_category": "historical_sow",
      "business_unit": null,
      "delivery_period": null,
      "quality_rating": 4.4,
      "citation_text": "IT infrastructure services SoW, 24-month engagement",
      "is_seed_data": true,
      "snapshot_timestamp": "2026-11-05T10:30:00Z"
    }
  ],
  "evidence_limited_flag": true,
  "evidence_snapshot_timestamp": "2026-11-13T10:30:00Z",
  "correlation_id": "CORR-001"
}
```

**Notes:**
- Returns evidence from TOL2 when available
- Falls back to seed data when TOL2 unavailable (sets `evidence_limited_flag: true`)
- Never fabricates suppliers or evidence
- Returns empty `evidence_items` array when no evidence available

### POST /api/v1/longlists/{proposal_id}/validate-count
Validate supplier count against 3-6 business rule (ATS9).

**URL Pattern:** `/api/v1/longlists/{proposal_id}/validate-count` where `{proposal_id}` is the UUID of the proposal

**Request:**
```json
{
  "proposal_or_longlist_id": "uuid-string",
  "supplier_ids": ["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005"]
}
```

**Response (pass):**
```json
{
  "proposal_id": "uuid-string",
  "supplier_count": 5,
  "validation_verdict": "pass",
  "violations": [],
  "validated_at": "2026-11-13T10:30:00Z",
  "correlation_id": "CORR-001"
}
```

**Response (fail - too few):**
```json
{
  "proposal_id": "uuid-string",
  "supplier_count": 2,
  "validation_verdict": "fail",
  "violations": ["Supplier count 2 is below minimum required 3"],
  "validated_at": "2026-11-13T10:30:00Z",
  "correlation_id": "CORR-001"
}
```

**Response (fail - too many):**
```json
{
  "proposal_id": "uuid-string",
  "supplier_count": 7,
  "validation_verdict": "fail",
  "violations": ["Supplier count 7 exceeds maximum allowed 6"],
  "validated_at": "2026-11-13T10:30:00Z",
  "correlation_id": "CORR-001"
}
```

**Notes:**
- Pass verdict: 3 ≤ supplier_count ≤ 6
- Fail verdict: supplier_count < 3 or supplier_count > 6
- Creates immutable validation record in database
- Rerun after adjustments (ATS10) and before finalization (ATS11)

## Seed Data

### Evidence Records
The following seed evidence records exist in the database:

**SUP-0231:**
- SOW-2022-0871: IT infrastructure services SoW, 24-month engagement
- ORD-2023-4410: Cloud services order, delivered on schedule with high quality

**SUP-0118:**
- SOW-2021-0522: Enterprise application services SoW

**SUP-0307:**
- PANEL-MATCH-2024-001: Panel-qualified cloud services provider

**SUP-0045:**
- PANEL-MATCH-2024-002: Panel-qualified infrastructure services provider

**SUP-0412:**
- PANEL-MATCH-2024-003: Panel-qualified network and cloud services provider

### Validation Examples
Seed data includes three validation scenarios:

1. **Pass with 4 suppliers** (Need 1, proposal 00000000-0000-0000-0000-000000000011)
2. **Fail with 2 suppliers** (Need 4, proposal 00000000-0000-0000-0000-000000000014)
3. **Fail with 7 suppliers** (Need 5, proposal 00000000-0000-0000-0000-000000000015)

## Backend Flows

### ATS5: Evidence Retrieval Flow
1. Receive evidence query request with need_id and optional filters
2. Attempt to query TOL2 evidence adapter
3. If TOL2 available and returns data:
   - Convert TOL2 items to response format
   - Set `evidence_limited_flag: false`
   - Return evidence with TOL2 snapshot timestamp
4. If TOL2 unavailable or returns empty:
   - Query seed evidence items from database for the need_id
   - Set `evidence_limited_flag: true`
   - Return seed evidence (or empty list if none exists)
5. Never fabricate suppliers, SoWs, or performance history

### ATS9: Count Validation Flow
1. Receive validation request with proposal_id and supplier_ids array
2. Count suppliers in array
3. Apply TOL4 validation utility rule (3-6 range):
   - If 3 ≤ count ≤ 6: verdict = "pass", violations = []
   - If count < 3: verdict = "fail", violations = ["...below minimum..."]
   - If count > 6: verdict = "fail", violations = ["...exceeds maximum..."]
4. Create immutable SupplierCountValidation record with verdict and violations
5. Return validation response with verdict and violations

## Database Tables

### supplier_evidence_items
Evidence items retrieved from TOL2 or fallback seed data.

**Key columns:**
- `evidence_item_id` (uuid PK)
- `need_id` (uuid FK → needs.need_id)
- `supplier_id` (varchar 128)
- `evidence_type` (varchar 64): historical_sow, historical_order, quality_rating, etc.
- `source_reference` (text): reference to source system record
- `citation_text` (text): human-readable citation
- `quality_rating` (numeric 3,2): optional quality score
- `is_seed_data` (boolean): true for fallback seed data
- `evidence_snapshot_timestamp` (timestamptz): when evidence was captured

### supplier_count_validations
Validation records for supplier count checks.

**Key columns:**
- `supplier_count_validation_id` (uuid PK)
- `proposal_or_longlist_id` (uuid)
- `supplier_count` (integer): actual count validated
- `validation_verdict` (varchar 8): "pass" or "fail"
- `violations` (jsonb): array of violation messages
- `validated_at` (timestamptz): validation timestamp

## Testing

Run unit tests:
```bash
cd /repos/deutsche-telekom-repo/backend
.venv/bin/python -m pytest tests/test_evidence_service.py tests/test_count_validation_service.py
```

Run integration tests:
```bash
.venv/bin/python -m pytest tests/test_evidence_integration.py
```

All tests verify:
- Evidence retrieval with graceful degradation
- Seed data fallback behavior
- Count validation pass/fail logic
- API endpoint request/response contracts
- Immutable validation record creation
