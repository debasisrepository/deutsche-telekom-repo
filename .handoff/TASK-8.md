# TASK-8 Handoff: Backend Feature B6 - Panel Mapping and Longlist Proposal Generation

## Implemented Endpoints

### Panel Mapping
- `GET /api/v1/cases/{caseId}/mapping`
  - Returns panel and functional-group mappings for a case
  - Response includes panel code/name, functional group code/name, mapping status, rationale inputs
  - Used to review proposed mappings before longlist generation

### Longlist Proposal Generation
- `POST /api/v1/cases/{caseId}/longlist-proposals`
  - Generates ranked supplier longlist proposal via AGN2 service
  - Combines historical evidence and panel mappings
  - Returns `{items, total}` wrapper format with ranked suppliers
  - Each supplier includes: rank position, ranking score, citation_complete flag

## Response Shapes

### Panel Mapping Response
```json
{
  "case_id": 1,
  "case_number": "CASE-2026-00001",
  "mappings": [
    {
      "id": 1,
      "panel_code": "PANEL-CLOUD-001",
      "panel_name": "Cloud Infrastructure & Platform Services",
      "functional_group_code": "FG-INFRA-001",
      "functional_group_name": "Infrastructure Modernization",
      "mapping_status": "proposed",
      "rationale_inputs": "Service category 'cloud infrastructure' matches panel specialization",
      "created_at": "2026-11-12T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Longlist Proposal Response
```json
{
  "items": [
    {
      "supplier_id": 1,
      "supplier_code": "SUP-CLOUD-001",
      "supplier_name": "CloudTech Solutions",
      "rank_position": 1,
      "ranking_score": 0.95,
      "citation_complete": true,
      "evidence_citations": [
        {
          "citation_label": "Cloud Migration - 2025 Q3",
          "citation_ref": "order/ORD-2025-1234",
          "evidence_summary": "Successfully completed cloud infrastructure migration for similar scope"
        }
      ]
    }
  ],
  "total": 1,
  "proposal_id": 1,
  "version_no": 1,
  "proposal_status": "draft",
  "created_at": "2026-11-12T10:05:00Z"
}
```

## Database Schema

### New Tables

#### panel
- `id` (Integer, PK)
- `panel_code` (String(50), unique, indexed)
- `panel_name` (String(255))
- `requirement_tags` (Text)
- `created_at` (DateTime with timezone)

#### functional_group
- `id` (Integer, PK)
- `functional_group_code` (String(50), unique, indexed)
- `functional_group_name` (String(255))
- `requirement_tags` (Text)
- `created_at` (DateTime with timezone)

#### case_mapping
- `id` (Integer, PK)
- `case_id` (Integer, FK to need_case.id, indexed)
- `panel_id` (Integer, FK to panel.id, indexed)
- `functional_group_id` (Integer, FK to functional_group.id, indexed)
- `mapping_status` (String(50))
- `rationale_inputs` (Text)
- `requirement_tags` (Text)
- `created_at` (DateTime with timezone)

#### longlist_proposal
- `id` (Integer, PK)
- `case_id` (Integer, FK to need_case.id, indexed)
- `version_no` (Integer)
- `proposal_status` (String(50))
- `generation_inputs` (Text/JSONB)
- `generated_by_agent_run_id` (String(100))
- `requirement_tags` (Text)
- `created_at` (DateTime with timezone)

#### proposal_supplier
- `id` (Integer, PK)
- `proposal_id` (Integer, FK to longlist_proposal.id, indexed)
- `supplier_id` (Integer, FK to supplier.id, indexed)
- `rank_position` (Integer)
- `recommendation_status` (String(50))
- `ranking_score` (Float)
- `citation_complete` (Boolean)
- `requirement_tags` (Text)
- `created_at` (DateTime with timezone)

## Seed Data

### Panels
- `PANEL-CLOUD-001`: Cloud Infrastructure & Platform Services
- `PANEL-SEC-002`: Security & Risk Management Services
- `PANEL-APP-003`: Application Development & Integration

### Functional Groups
- `FG-INFRA-001`: Infrastructure Modernization
- `FG-SEC-001`: Cybersecurity Services
- `FG-APP-001`: Custom Application Development

### Case Mappings
- Case 1 (CASE-2026-00001) → PANEL-CLOUD-001 + FG-INFRA-001
- Case 2 (CASE-2026-00002) → PANEL-SEC-002 + FG-SEC-001
- Case 4 (CASE-2026-00004) → PANEL-APP-003 + FG-APP-001

### Longlist Proposals
- Case 1: 1 ranked supplier (SUP-CLOUD-001, rank 1, score 0.95, citation complete)
- Case 2: 1 ranked supplier (SUP-SEC-002, rank 1, score 0.92, citation complete)
- Case 4: 1 ranked supplier (SUP-APP-003, rank 1, score 0.90, citation complete)

## Services and Adapters

### AGN5 Rule Engine Extensions
- `resolve_mappings()`: Coordinates panel/functional-group lookup via TOL3 adapter

### TOL3 Panel Mapping Adapter
- `query_panel_mappings()`: Queries enterprise system for relevant panel/functional-group mappings
- Stub implementation returns sample mappings based on service category patterns
- Stub-to-live seam documented for future enterprise integration

### Panel Mapping Service
- `store_mappings()`: Retrieves and stores panel/functional-group mappings for a case
- `list_mappings()`: Lists all mappings for a case

### AGN2 Service
- `generate_ranked_longlist()`: Generates ranked supplier longlist proposal (ATS8)
- Combines evidence-derived suppliers with panel-based eligibility
- Returns ranked suppliers with citation completeness flags

### Repositories
- `MappingRepository`: Data access for panels, functional groups, and case mappings
- `LonglistRepository`: Data access for longlist proposals and proposal suppliers

## Workflow Integration

### Panel Mapping Flow
1. Case reaches extraction_approved state with confirmed attributes
2. AGN5 rule engine invokes TOL3 adapter with confirmed attributes
3. TOL3 returns relevant panel/functional-group mapping candidates
4. Mapping service stores mappings via mapping repository
5. Mappings available via GET /api/v1/cases/{caseId}/mapping

### Longlist Proposal Flow
1. Case has confirmed attributes and evidence retrieval complete
2. POST /api/v1/cases/{caseId}/longlist-proposals triggers AGN2 service
3. AGN2 retrieves case evidence and mapping info
4. AGN2 ranks suppliers based on evidence quality and relevance
5. AGN2 creates longlist proposal with ranked suppliers
6. Each supplier includes rank position, ranking score, citation_complete flag
7. Proposal returned in {items, total} wrapper format

## Key Implementation Notes

### Citation Completeness
- `citation_complete` flag tracks whether supplier has supporting evidence
- Derived from `evidence_found` flag in case_evidence records
- Used by validation logic to enforce evidence-grounding requirement (FR-017)

### Ranking Logic
- Stub implementation uses evidence order and quality for ranking
- Production implementation would use LLM-based intelligent ranking
- Ranking score decreases with rank position in stub

### Response Format
- Longlist proposals return `{items, total}` wrapper per standard pagination interface
- Each supplier in `items` array includes full ranking metadata
- Proposal metadata (proposal_id, version_no, status, created_at) at top level

## Migration

Migration `007_add_mapping_and_longlist_tables.py` creates:
- panel table with unique index on panel_code
- functional_group table with unique index on functional_group_code
- case_mapping table with FKs to need_case, panel, functional_group
- longlist_proposal table with FK to need_case
- proposal_supplier table with FKs to longlist_proposal and supplier
