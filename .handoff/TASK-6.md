# Task 6 Handoff: Panel Mapping and Niche Research (ATS6, ATS7)

## Implemented Endpoints

### POST /api/v1/panel-mappings
Maps a classified need to candidate suppliers from the panel and functional-group catalog.

**Request:**
```json
{
  "need_id": "uuid",
  "need_category": "string"
}
```

**Response:**
```json
{
  "need_id": "uuid",
  "candidate_suppliers": [
    {
      "panel_match_id": "uuid",
      "supplier_id": "string",
      "panel_source": "string",
      "functional_group": "string",
      "provenance_ref": "string"
    }
  ],
  "coverage_gap_flag": boolean,
  "correlation_id": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request or need state
- 404: Need not found
- 500: Mapping failure

### POST /api/v1/niche-research
Researches additional providers for niche needs using governed sources when panel mapping identifies a coverage gap.

**Request:**
```json
{
  "need_id": "uuid",
  "capability_gap": "string",
  "approved_source_list": ["string"],
  "existing_panel_matches": ["string"] // optional
}
```

**Response:**
```json
{
  "need_id": "uuid",
  "niche_research_dossier": [
    {
      "provider_candidate_id": "uuid",
      "candidate_name": "string",
      "supplier_id": "string",
      "capability_gap": "string",
      "source_citations": ["string"],
      "review_status": "string",
      "review_notes": "string | null"
    }
  ],
  "review_required": boolean,
  "correlation_id": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request, wrong need type (must be it_service), or no approved sources
- 404: Need not found
- 500: Research failure

## Seed Records

### Panel Matches (panel_matches table)
- **SUP-0231**: Cloud and hosting panel, Cloud Infrastructure functional group
- **SUP-0118**: Platform engineering panel, Platform Services functional group
- **SUP-0307**: Managed services panel, Managed Operations functional group
- **SUP-0045**: Cloud and hosting panel, Hybrid Cloud Solutions functional group
- **SUP-0412**: Managed services panel, Network and Cloud Services functional group

All panel matches include:
- `panel_source`: Name of the panel registry
- `functional_group`: Functional specialization within the panel
- `provenance_ref`: Panel registry entry date/reference
- `coverage_gap_flag`: False for standard coverage, True when niche research needed

### Provider Candidates (provider_candidates table)
- **SUP-0518** (CloudTech Solutions GmbH):
  - Source citations: "Gaia-X participant registry 2024-08-15", "ISO 27001 certified provider"
  - Review status: pending
  - Capability gap: Specialized quantum-resistant encryption for ML models

- **SUP-0533** (SecureOps AG):
  - Source citations: "BSI C5 attestation 2024-06-20", "Federal approved supplier list"
  - Review status: accepted
  - Capability gap: Advanced security compliance for AI/ML workloads

## Backend Flows

### ATS6 Panel Mapping Flow
1. Accepts `need_id` and `need_category` from POST /api/v1/panel-mappings
2. Validates need exists in database
3. Queries TOL3 panel catalog adapter with need details
4. TOL3 returns candidate suppliers with panel/functional-group metadata and coverage_gap_flag
5. Creates PanelMatch records for each candidate supplier
6. Writes AuditEvent with step_code="ATS6", agent_code="AGN2", tool_code="TOL3"
7. Returns candidate suppliers list with panel provenance and coverage gap indicator
8. When `coverage_gap_flag=true` and need is classified `it_service`, triggers ATS7

### ATS7 Niche Research Flow
1. Accepts `need_id`, `capability_gap`, `approved_source_list` from POST /api/v1/niche-research
2. Validates need exists and is classified as `it_service` (rejects `single_resource` needs)
3. Validates `approved_source_list` is not empty (hard requirement for governed research)
4. Simulates niche provider research using governed external sources (Gaia-X, BSI C5, etc.)
5. Filters out candidates already in `existing_panel_matches` to avoid duplicates
6. Creates ProviderCandidate records with `source_citations` from governed sources
7. Sets `review_status="pending"` - all candidates require reviewer approval
8. Writes AuditEvent with step_code="ATS7", agent_code="AGN2"
9. Returns research dossier with `review_required=true`
10. Reviewers must accept/modify/reject candidates before they are eligible for ranking

### Coverage Gap Detection
- Panel mapping sets `coverage_gap_flag=true` when registry lacks adequate coverage
- Missing coverage surfaces explicitly - no implicit supplier recommendations
- ATS7 invoked **only when**:
  - `coverage_gap_flag=true` from ATS6, **AND**
  - Need classified as `it_service` (not `single_resource`)
- Without approved governed sources, ATS7 halts and surfaces the gap rather than fabricating providers

### Audit Trail
Both ATS6 and ATS7 write immutable audit events:
- `need_id`: Links audit to workflow case
- `correlation_id`: Request tracing across services
- `step_code`: "ATS6" or "ATS7"
- `agent_code`: "AGN2" (Procurement Analyst agent)
- `tool_code`: "TOL3" (Panel catalog connector)
- `actor_type`: "system" (deterministic execution)
- `outcome`: "mapped", "coverage_gap_detected", or "research_completed"

## Testing Notes

### Unit Tests
- `test_panel_mapping_service.py`: Tests PanelMappingService logic
  - Success case with multiple candidates
  - Coverage gap detection for niche categories
  - Need not found error
  - Audit event creation

- `test_niche_research_service.py`: Tests NicheResearchService logic
  - Success case with approved sources
  - Need not found error
  - Wrong classification type (single_resource) rejection
  - No approved sources error
  - Audit event creation

### Integration Tests
- `test_panel_integration.py`: Tests API endpoints end-to-end
  - Panel mappings endpoint success
  - Panel mappings endpoint not found
  - Niche research endpoint success
  - Niche research endpoint not found
  - Niche research wrong classification rejection
  - Niche research no approved sources rejection

## Frontend Integration Notes

When building UI for these endpoints:

1. **Panel Mapping (ATS6)**:
   - Display candidate suppliers table with columns: supplier_id, panel_source, functional_group, provenance_ref
   - Show coverage gap indicator prominently when `coverage_gap_flag=true`
   - Provide navigation to ATS7 niche research when gap detected

2. **Niche Research (ATS7)**:
   - Only enable for needs classified as `it_service` with `coverage_gap_flag=true`
   - Display research dossier with source citations visible for each candidate
   - Show review status (pending/accepted/rejected) with color coding
   - Provide reviewer actions: accept, modify (with notes), reject
   - Block candidates with `review_status="pending"` or `"rejected"` from longlist ranking

3. **Review Workflow**:
   - Reviewers must explicitly accept/modify/reject niche candidates
   - Display `source_citations` array for governance transparency
   - Allow adding `reviewer_notes` when modifying or rejecting
   - Only `review_status="accepted"` candidates proceed to ATS8 ranking

## Database Schema

### panel_matches
- `id`: UUID primary key
- `need_id`: UUID foreign key to needs
- `supplier_id`: varchar(128) indexed
- `panel_source`: varchar(128) - panel registry name
- `functional_group`: varchar(128) - specialization within panel
- `provenance_ref`: text - registry entry reference
- `coverage_gap_flag`: boolean default false - triggers ATS7 when true
- `created_at`, `updated_at`: timestamptz

### provider_candidates
- `id`: UUID primary key
- `need_id`: UUID foreign key to needs
- `candidate_name`: varchar(255) - provider company name
- `supplier_id`: varchar(128) indexed
- `capability_gap`: text - gap description
- `source_citations`: jsonb (stored as text in SQLite) - array of governed source citations
- `review_status`: varchar(16) - pending/accepted/rejected
- `review_notes`: text nullable - reviewer comments
- `created_at`, `updated_at`: timestamptz
