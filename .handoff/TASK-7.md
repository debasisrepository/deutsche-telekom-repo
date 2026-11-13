# TASK-7 Handoff: Longlist Proposal and Adjustment Features

## Implemented Endpoints

### POST /api/v1/longlist-proposals
Generate ranked longlist proposal (ATS8).

**Request:**
```json
{
  "need_id": "uuid",
  "matched_panels": ["uuid", "uuid"],
  "evidence_items": ["uuid", "uuid"],
  "approved_niche_candidates": ["uuid"],
  "supplier_count_rules": {}
}
```

**Response (201):**
```json
{
  "proposal_id": "uuid",
  "need_id": "uuid",
  "ranked_suppliers": [
    {
      "ranked_supplier_id": "uuid",
      "supplier_id": "SUP-0231",
      "rank": 1,
      "panel_source": "Cloud and hosting",
      "evidence_citations": [
        {
          "source_reference": "SOW-2022-0871",
          "citation_text": "IT infrastructure services SoW..."
        }
      ],
      "rank_rationale": "Panel match: Cloud and hosting; Evidence: historical_sow (SEED); ",
      "confidence": 0.8
    }
  ],
  "evidence_limited_flag": false,
  "proposal_status": "pending",
  "reviewed_by": null,
  "reviewed_at": null,
  "correlation_id": "..."
}
```

### POST /api/v1/longlists/{longlist_id}/adjustments
Capture business-unit longlist adjustments (ATS10).

**Request:**
```json
{
  "longlist_id": "uuid",
  "supplier_id": "SUP-0045",
  "action": "add",
  "reason": "BU requested additional supplier for diversity",
  "actor": "bu.cloudops.lead",
  "timestamp": "2026-11-13T12:00:00Z"
}
```

**Response (201):**
```json
{
  "adjustment_id": "uuid",
  "longlist_id": "uuid",
  "updated_suppliers": ["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
  "validation_verdict": "pass",
  "change_history_count": 1,
  "correlation_id": "..."
}
```

## Seed Records

### Proposal Example: PRP-2024-0418-01
- Proposal ID: `00000000-0000-0000-0000-000000000011`
- Need ID: `00000000-0000-0000-0000-000000000001`
- 4 ranked suppliers with evidence citations
- Evidence limited flag: false
- Review status: approved

### Ranked Suppliers in Seed Proposal
1. **SUP-CLOUD-001** (rank 1)
   - Panel source: IT-CLOUD-PANEL-A
   - Evidence: TOL2/project/PRJ-2023-045
   - Confidence: 0.88

2. **SUP-CLOUD-002** (rank 2)
   - Panel source: IT-CLOUD-PANEL-A
   - Evidence: TOL2/sow/SOW-2022-112
   - Confidence: 0.82

3. **SUP-CLOUD-003** (rank 3)
   - Panel source: IT-INFRA-PANEL-B
   - Evidence: TOL2/rating/2023-Q4
   - Confidence: 0.79

4. **SUP-CLOUD-004** (rank 4)
   - Panel source: IT-CLOUD-PANEL-A
   - Evidence: TOL3/panel/IT-CLOUD-PANEL-A/2024-Q1
   - Confidence: 0.71

### Referenced Suppliers in Seed Data
- **SUP-0231**: Cloud and hosting panel, historical SoW SOW-2022-0871, order ORD-2023-4410
- **SUP-0118**: Platform engineering panel, historical SoW SOW-2021-0522
- **SUP-0307**: Managed services panel, supplier service match PANEL-MATCH-2024-001
- **SUP-0045**: Cloud and hosting panel (Hybrid Cloud Solutions), supplier service match PANEL-MATCH-2024-002
- **SUP-0518**: CloudTech Solutions (niche candidate with Gaia-X citations)

### Longlist for Adjustments: LL-2024-0418
- Longlist ID: `00000000-0000-0000-0000-000000000021`
- Initial suppliers: SUP-CLOUD-001, SUP-CLOUD-002, SUP-CLOUD-003, SUP-CLOUD-004
- Locked: true
- Validation verdict at lock: pass

## Backend Flows

### ATS8: Generate Proposal
1. Accept need_id, matched_panels, evidence_items, approved_niche_candidates
2. Retrieve Need record and validate existence
3. Retrieve panel matches, evidence items, and niche candidates from database
4. Rank suppliers based on:
   - Panel matches (+50 score)
   - Evidence items (+30 * quality_rating score, add citations)
   - Niche candidates (+40 score, add source citations)
5. Enforce citation requirement: reject uncited suppliers before persistence
6. Create LonglistProposal record
7. Create LonglistRankedSupplier records for each ranked supplier
8. Write AuditEvent with step_code=ATS8, agent_code=AGN2
9. Return proposal with ranked suppliers including evidence_citations

**Citation Enforcement:**
- Every ranked supplier MUST have at least one citation
- Citations come from evidence items or niche research
- Uncited suppliers trigger ValueError and rollback

**Reviewer Workflow:**
- Proposals created with review_status="pending"
- Reviewers can accept, modify, or reject before finalization
- Reviewer notes stored in proposal record

### ATS10: Capture Adjustment
1. Accept longlist_id, supplier_id, action (add|remove), reason, actor, timestamp
2. Retrieve Longlist record and validate existence
3. Validate supplier_id exists in supplier universe (basic check: length >= 3)
4. Parse current suppliers list from JSON
5. Apply adjustment:
   - Add: append supplier if not already present
   - Remove: remove supplier if present
6. Create LonglistAdjustment record
7. Update Longlist.suppliers with new list
8. Update Longlist.change_history with adjustment details
9. Rerun ATS9 validation using TOL4ValidationUtil
10. Write AuditEvent with step_code=ATS10, agent_code=AGN3, actor_type=human
11. Return updated_suppliers, validation_verdict, change_history_count

**Validation Rerun:**
- After every adjustment, supplier count is revalidated
- Pass: 3 ≤ count ≤ 6
- Fail: count < 3 or count > 6
- Validation verdict returned in response

**Change History:**
- Immutable record of all adjustments
- Each entry includes: adjustment_id, action, supplier_id, actor, timestamp, reason
- Full history attached to evolving longlist

## Key Behaviors

1. **Citation Coverage**: Every ranked supplier must carry evidence_citations or approved research citations
2. **Uncited Rejection**: Suppliers without citations are rejected before persistence with auditable error
3. **Evidence Limited Flag**: Set to true when TOL2 unavailable or no evidence items exist
4. **Supplier Ranking**: Based on panel matches (50), evidence (30 * quality), niche research (40)
5. **Adjustment Validation**: Supplier IDs validated before adjustment (rejects unknown with error)
6. **Action Governance**: Only "add" and "remove" actions allowed (enforced at schema level)
7. **Validation Rerun**: ATS9 validation automatically reruns after every adjustment
8. **Change History**: Full immutable audit trail of all adjustments maintained

## Error Scenarios

1. **Need Not Found**: ValueError "Need {uuid} not found"
2. **Uncited Suppliers**: ValueError "Uncited suppliers rejected: {supplier_ids}..."
3. **Unknown Supplier**: ValueError "Unknown supplier: {supplier_id}..."
4. **Invalid Action**: ValueError "Invalid action: {action}. Must be 'add' or 'remove'."
5. **Longlist Not Found**: ValueError "Longlist {uuid} not found"

## Testing Coverage

### Unit Tests (test_longlist_proposal_service.py)
- Successful proposal generation with panel matches and evidence
- Rejection of uncited suppliers
- Proposal with niche candidates
- Need not found error

### Unit Tests (test_longlist_adjustment_service.py)
- Add supplier adjustment
- Remove supplier adjustment
- Validation failure after adjustment
- Unknown supplier rejection
- Invalid action rejection
- Longlist not found error

### Integration Tests (test_longlist_integration.py)
- POST /api/v1/longlist-proposals endpoint success
- Uncited supplier rejection via API
- POST /api/v1/longlists/{id}/adjustments add action
- POST /api/v1/longlists/{id}/adjustments remove action
- Invalid action rejected at schema validation

### Acceptance Tests (test_longlist_acceptance.py)
- Proposal contains required fields
- Ranked supplier includes all required fields
- Every ranked supplier carries cited evidence
- Proposal includes supplier-specific rationale
- Adjustment records required fields
- Adjustment actions limited to add/remove
- Change history maintained
- Validation reruns after adjustment
