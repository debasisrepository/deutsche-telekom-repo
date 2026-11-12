# TASK-7 Handoff: Backend Feature B5 - Historical Evidence Retrieval and Citation

## Implemented Endpoints

### Evidence Retrieval
- **GET /api/v1/cases/{caseId}/evidence** - Retrieve historical supplier evidence for a case

## Endpoint Details

### GET /api/v1/cases/{caseId}/evidence

Returns historical evidence items with supplier details, citations, and evidence summaries.

**Request:**
- Path parameter: `caseId` (integer) - Case identifier
- Authentication: Required (Bearer token)

**Response (200):**
```json
{
  "case_id": 1,
  "case_number": "CASE-2026-00001",
  "evidence_items": [
    {
      "id": 1,
      "case_id": 1,
      "supplier": {
        "id": 1,
        "supplier_code": "SUP-CLOUD-001",
        "display_name": "CloudTech Solutions GmbH",
        "status": "active"
      },
      "citation_label": "Cloud Migration - 2025 Q3",
      "citation_ref": "order/ORD-2025-1234",
      "evidence_summary": "Successfully completed cloud infrastructure migration for similar scope in Q3 2025. Delivered on time with 99.9% uptime SLA compliance.",
      "evidence_found": true,
      "created_at": "2026-11-12T10:30:00Z"
    }
  ],
  "total": 3
}
```

**Error Responses:**
- **404** - Case not found
- **401** - Unauthorized (missing or invalid token)

## Response Shape

### Evidence Item Structure
Each evidence item in the `evidence_items` array contains:
- `id` (integer) - Evidence record identifier
- `case_id` (integer) - Case identifier
- `supplier` (object or null) - Supplier details
  - `id` (integer) - Supplier identifier
  - `supplier_code` (string) - Unique supplier code (e.g., "SUP-CLOUD-001")
  - `display_name` (string) - Supplier display name
  - `status` (string) - Supplier status (e.g., "active")
- `citation_label` (string) - Human-readable citation label
- `citation_ref` (string) - Citation reference path (e.g., "order/ORD-2025-1234")
- `evidence_summary` (string) - Evidence summary text
- `evidence_found` (boolean) - Whether evidence was found (true/false)
- `created_at` (string or null) - ISO 8601 timestamp

## Database Schema

### New Tables

**supplier** - Supplier master data
- `id` (integer, PK)
- `supplier_code` (string, unique) - Unique supplier identifier
- `display_name` (string) - Supplier display name
- `status` (string) - Supplier status (active/inactive)
- `contact_endpoint` (text, nullable) - Contact information
- `evidence_source_status` (string, nullable) - Evidence availability status
- `requirement_tags` (text, nullable)
- `created_at` (datetime)

**historical_order** - Past completed orders for evidence
- `id` (integer, PK)
- `external_order_id` (string, unique) - External order reference
- `service_domain` (string) - Service domain category
- `completion_date` (date) - Order completion date
- `requirement_tags` (text, nullable)
- `created_at` (datetime)

**commissioned_sow** - Past statements of work for evidence
- `id` (integer, PK)
- `external_sow_id` (string, unique) - External SoW reference
- `scope_summary` (text) - Summary of SoW scope
- `signed_date` (date) - SoW signing date
- `requirement_tags` (text, nullable)
- `created_at` (datetime)

**case_evidence** - Evidence records linked to cases
- `id` (integer, PK)
- `case_id` (integer, FK to need_case) - Case identifier
- `supplier_id` (integer, FK to supplier, nullable) - Supplier identifier
- `historical_order_id` (integer, FK to historical_order, nullable) - Historical order link
- `commissioned_sow_id` (integer, FK to commissioned_sow, nullable) - SoW link
- `citation_label` (text) - Human-readable citation label
- `citation_ref` (text) - Citation reference path
- `evidence_summary` (text) - Evidence summary
- `evidence_found` (boolean) - Whether evidence was found
- `requirement_tags` (text, nullable)
- `created_at` (datetime)

**supplier_citation** - Links proposal suppliers to evidence (prepared for future tasks)
- `id` (integer, PK)
- `proposal_supplier_id` (integer, FK to proposal_supplier) - Proposal supplier link
- `case_evidence_id` (integer, FK to case_evidence) - Evidence link
- `citation_type` (string) - Citation type
- `citation_ref` (text) - Citation reference
- `requirement_tags` (text, nullable)
- `created_at` (datetime)

## Seed Data

The seed script creates sample evidence for the following cases:

**CASE-2026-00001** (Cloud Infrastructure Modernization)
- Evidence: CloudTech Solutions GmbH - Cloud Migration - 2025 Q3
- Historical Order: ORD-2025-1234

**CASE-2026-00002** (Network Security Assessment)
- Evidence: SecureNet Services AG - Network Security Assessment - 2024
- Commissioned SoW: SOW-2024-5678

**CASE-2026-00004** (Application Development Services)
- Evidence: AppDev Partners GmbH - Application Development - 2025 Q2
- Historical Order: ORD-2025-9012

### Sample Suppliers
- **SUP-CLOUD-001**: CloudTech Solutions GmbH (active)
- **SUP-SEC-002**: SecureNet Services AG (active)
- **SUP-APP-003**: AppDev Partners GmbH (active)

## Backend Implementation

### Services
- **EvidenceService** (`app/services/evidence/evidence_service.py`)
  - `store_evidence(case_id, need_attributes, requirement_tags)` - Store evidence from TOL2 adapter
  - `list_evidence(case_id)` - List evidence with supplier details

### Repositories
- **EvidenceRepository** (`app/repositories/evidence_repository.py`)
  - `get_or_create_supplier()` - Idempotent supplier creation
  - `get_or_create_historical_order()` - Idempotent order creation
  - `get_or_create_commissioned_sow()` - Idempotent SoW creation
  - `create_case_evidence()` - Create evidence record
  - `list_case_evidence()` - Query evidence by case
  - `get_supplier_by_id()` - Retrieve supplier details

### Adapters
- **TOL2SupplierKBAdapter** (`app/adapters/tol2_supplier_kb_adapter.py`)
  - Stub implementation returning sample evidence for testing
  - `query_historical_evidence(case_id, need_attributes)` - Query evidence
  - Stub-to-live seam documented for production integration

### Rule Engine
- **AGN5RuleEngine** (`app/services/rules/agn5_rule_engine.py`)
  - Extended with `retrieve_evidence(case_id, confirmed_attributes)` method
  - Coordinates TOL2 adapter invocation and evidence normalization (ATS5)

## Workflow Impact

Evidence retrieval is a prerequisite for longlist generation:
1. Case reaches extraction_approved state after classification confirmation
2. Evidence retrieval invoked via AGN5 rule engine
3. TOL2 adapter queries historical supplier knowledge base
4. Evidence service stores normalized evidence with supplier links
5. Case can proceed to longlist proposal generation (future task)

## Evidence-Grounding Rule

Every supplier recommendation in a longlist must have at least one evidence citation:
- Evidence retrieved and stored before longlist generation
- `evidence_found` flag tracks whether evidence was successfully retrieved
- Future longlist tasks will enforce citation completeness before finalization

## Testing

Integration tests verify:
- Evidence service stores evidence with supplier and citation links
- Evidence service lists evidence with supplier details
- GET /api/v1/cases/{caseId}/evidence endpoint returns correct response shape
- Evidence repository creates suppliers, orders, and SoWs idempotently
- AGN5 rule engine retrieve_evidence() method normalizes evidence correctly
- Evidence records are properly linked to cases
- `evidence_found` flag is stored and retrieved correctly

Run tests:
```bash
cd /repos/deutsche-telekom-repo/backend
.venv/bin/python -m pytest tests/test_evidence_integration.py -v
```
