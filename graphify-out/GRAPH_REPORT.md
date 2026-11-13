# Graph Report - deutsche-telekom-repo  (2026-11-13)

## Corpus Check
- 236 files · ~83,336 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 47 file(s) not represented in the graph (top: .scss 28, (none) 8, .ini 2)

## Summary
- 1697 nodes · 3669 edges · 109 communities (66 shown, 43 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 192 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `73e6c3b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Deutsche Telekom IT Procurement Supplier Selection Workflow
- sqlalchemy_orm
- auth-context.tsx
- error_middleware.py
- test_pipeline_migration_parity.py
- compilerOptions
- ValidationAndAdjustmentPage.tsx
- test_smoke.py
- ResearchAndProposalPage.tsx
- need_review_service.py
- package.json
- compilerOptions
- auth.py
- eslint.config.js
- niche_research_service.py
- utils.ts
- deutsche-telekom-procurement-backend
- vite
- scripts
- @playwright/test
- steps
- setup.ts
- typing
- TASK-3 Handoff: Backend Intake and Review Features
- FastAPI
- environment
- panel_mapping_service.py
- TOL1IntakeAdapter
- environment
- Key Files
- Need
- VmsHandoffService
- AuditEventRepository
- SupplierEvidenceService
- SupplierCountValidation
- sqlalchemy_orm
- TASK-8 Handoff: Backend Feature B6 - Finalize longlist and lock record, Assemble and dispatch tender
- @carbon/react
- test_intake_integration.py
- TASK-5 Handoff: Evidence Retrieval and Supplier Count Validation
- niche_research_service.py
- need_ingestion_service.py
- TASK-7 Handoff: Longlist Proposal and Adjustment Features
- Task 6 Handoff: Panel Mapping and Niche Research (ATS6, ATS7)
- json
- Longlist
- tender_dispatch_service.py
- ClassificationReviewPage.tsx
- EvidenceAndPanelPage.tsx
- need_review_service.py
- main.py
- .map_need_to_panels
- VmsHandoffRepository
- request_logging_middleware.py
- start.sh
- NeedRepository
- test_evidence_integration.py
- need.py
- TOL5VmsAdapter
- api-client.ts
- UUID
- @carbon/react
- pytest
- LonglistProposal
- docker-entrypoint.sh
- stop.sh
- devDependencies
- AttributeReviewPage.tsx
- SupplierEvidenceItem
- LonglistAdjustmentService
- test_longlist_lock_service.py
- SupplierCountValidationService
- App.tsx
- classification_decision_service.py
- supplier_evidence_service.py
- VmsHandoffListPage.tsx
- test_longlist_integration.py
- PanelMatch
- supplier_count_validation_service.py
- dependencies
- reviews.py
- TOL2EvidenceAdapter
- auth_client
- query_evidence
- capture_longlist_adjustment
- 002_add_users_table.py
- 298825281f7d_add_evidence_fields.py

## God Nodes (most connected - your core abstractions)
1. `Need` - 112 edges
2. `Longlist` - 42 edges
3. `@carbon/react` - 38 edges
4. `AuditEvent` - 37 edges
5. `Base` - 34 edges
6. `NeedRepository` - 30 edges
7. `AuditEventRepository` - 29 edges
8. `NeedAttributes` - 28 edges
9. `SupplierEvidenceItem` - 28 edges
10. `react` - 25 edges

## Surprising Connections (you probably didn't know these)
- `execute_vms_handoff()` --uses--> `VmsHandoffRequest`  [INFERRED]
  backend/app/routers/api/v1/integrations.py → backend/app/schemas/vms_schemas.py
- `NeedIntakeRequest` --uses--> `NeedAttributesRequest`  [INFERRED]
  backend/app/schemas/intake_schemas.py → backend/app/schemas/review_schemas.py
- `VmsHandoffService` --uses--> `VmsHandoffResponse`  [INFERRED]
  backend/app/services/vms_handoff_service.py → backend/app/schemas/vms_schemas.py
- `VmsHandoffService` --uses--> `VmsHandoffListItem`  [INFERRED]
  backend/app/services/vms_handoff_service.py → backend/app/schemas/vms_schemas.py
- `review_need_classification()` --uses--> `ClassificationReviewRequest`  [INFERRED]
  backend/app/routers/api/v1/reviews.py → backend/app/schemas/vms_schemas.py

## Import Cycles
- None detected.

## Communities (109 total, 43 thin omitted)

### Community 0 - "Deutsche Telekom IT Procurement Supplier Selection Workflow"
Cohesion: 0.06
Nodes (35): API Documentation, Architecture, Backend, Backend Structure, Backend Tests, Contributing, Database Migrations, Default Credentials (+27 more)

### Community 1 - "sqlalchemy_orm"
Cohesion: 0.13
Nodes (11): run_migrations_offline(), run_migrations_online(), upgrade(), downgrade(), upgrade(), upgrade(), Base, LonglistRankedSupplier (+3 more)

### Community 2 - "auth-context.tsx"
Cohesion: 0.22
Nodes (13): LoginForm(), RequireAuth(), AuthContext, AuthContextType, useAuth(), LoginPage(), ApiError, LoginRequest (+5 more)

### Community 4 - "test_pipeline_migration_parity.py"
Cohesion: 0.11
Nodes (18): _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version(), _last_name(), _mapped_columns() (+10 more)

### Community 5 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+11 more)

### Community 6 - "ValidationAndAdjustmentPage.tsx"
Cohesion: 0.15
Nodes (11): AdjustmentForm(), AdjustmentFormProps, CountVisualization(), CountVisualizationProps, headers, ValidationHistory(), ValidationHistoryProps, ValidationRun (+3 more)

### Community 7 - "test_smoke.py"
Cohesion: 0.25
Nodes (3): test_app_starts_without_error(), test_health_endpoint(), test_ready_endpoint()

### Community 8 - "ResearchAndProposalPage.tsx"
Cohesion: 0.22
Nodes (13): CitationBadge(), CitationBadgeProps, NicheCandidateTable(), NicheCandidateTableProps, RankedSupplierTable(), RankedSupplierTableProps, ResearchAndProposalPage(), EvidenceCitation (+5 more)

### Community 9 - "need_review_service.py"
Cohesion: 0.07
Nodes (8): NeedAttributes, NeedAttributesRepository, test_extraction_review_workflow(), test_intake_flow_all_channels(), test_intake_flow_rfp_channel(), test_intake_malformed_rejection(), test_intake_pii_masking(), test_normalization_deterministic()

### Community 10 - "package.json"
Cohesion: 0.12
Nodes (16): postcss@^8.4.49, sass-embedded@^1.108.2, @testing-library/user-event@^14.5.2, @types/react@^18.3.12, @types/react-dom@^18.3.1, engines, node, name (+8 more)

### Community 11 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowSyntheticDefaultImports, composite, lib, module, moduleResolution, noEmit, resolveJsonModule (+4 more)

### Community 12 - "auth.py"
Cohesion: 0.11
Nodes (9): create_access_token(), decode_access_token(), hash_password(), verify_password(), jwt_middleware(), login(), LoginRequest, LoginResponse (+1 more)

### Community 19 - "eslint.config.js"
Cohesion: 0.17
Nodes (10): eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^17.14.0, @typescript-eslint/eslint-plugin@^8.15.0, @typescript-eslint/parser@^8.15.0, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals (+2 more)

### Community 20 - "niche_research_service.py"
Cohesion: 0.08
Nodes (6): ProviderCandidate, ProviderCandidateRepository, research_niche_providers(), NicheResearchDossierItem, NicheResearchRequest, NicheResearchResponse

### Community 21 - "utils.ts"
Cohesion: 0.20
Nodes (4): clsx@^2.1.1, tailwind-merge@^2.5.4, clsx, tailwind-merge

### Community 23 - "vite"
Cohesion: 0.40
Nodes (4): vite@^6.0.1, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 24 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test

### Community 26 - "steps"
Cohesion: 0.06
Nodes (35): name, runs-on, services, steps, DATABASE_URL, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER (+27 more)

### Community 28 - "typing"
Cohesion: 0.24
Nodes (6): LonglistAdjustmentRequest, LonglistAdjustmentResponse, LonglistLockRequest, LonglistLockResponse, SupplierCountValidationRequest, SupplierCountValidationResponse

### Community 29 - "TASK-3 Handoff: Backend Intake and Review Features"
Cohesion: 0.12
Nodes (15): ATS1 Intake Flow, ATS2 Review Flow, Backend Flows, Endpoints Added, GET /api/v1/intake/needs, GET /api/v1/intake/needs/{need_id}, Need, NeedAttributes (+7 more)

### Community 30 - "FastAPI"
Cohesion: 0.11
Nodes (8): AuditEventItem, AuditEventsResponse, LonglistLockRequest, LonglistLockResponse, SupplierContactItem, SupplierDispatchDetail, TenderDispatchRequest, TenderDispatchResponse

### Community 37 - "environment"
Cohesion: 0.06
Nodes (33): INSTALL_SPEC, build, depends_on, environment, args, context, dockerfile, postgres (+25 more)

### Community 38 - "panel_mapping_service.py"
Cohesion: 0.07
Nodes (6): TOL3PanelAdapter, PanelMatchRepository, map_need_to_panels(), CandidateSupplier, PanelMappingRequest, PanelMappingResponse

### Community 41 - "environment"
Cohesion: 0.09
Nodes (23): build, environment, ports, volumes, x-preview-port, context, dockerfile, CORS_ORIGINS (+15 more)

### Community 42 - "Key Files"
Cohesion: 0.09
Nodes (21): Adapters, ATS3: Classification Review, ATS4: VMS Handoff, Backend Flows, Classification Reviews, classification_reviews table, Database Schema, Implemented Endpoints (+13 more)

### Community 43 - "Need"
Cohesion: 0.09
Nodes (14): Need, test_classification_uses_structured_attributes(), test_classification_verdict_and_confidence_recorded(), test_low_confidence_held_for_review(), test_only_single_resource_and_it_service_allowed(), test_reviewer_can_approve_modify_reject(), test_single_resource_blocked_from_ats5_12(), test_single_resource_vms_handoff() (+6 more)

### Community 44 - "VmsHandoffService"
Cohesion: 0.23
Nodes (6): VmsHandoffRequest, VmsHandoffService, test_successful_vms_handoff(), test_vms_handoff_blocks_ats5_12_workflow(), test_vms_handoff_requires_correct_workflow_status(), test_vms_handoff_requires_single_resource_verdict()

### Community 46 - "SupplierEvidenceService"
Cohesion: 0.20
Nodes (5): SupplierEvidenceService, test_query_evidence_multiple_suppliers(), test_query_evidence_with_filters(), test_query_evidence_with_no_seed_data(), test_query_evidence_with_tol2_unavailable()

### Community 48 - "sqlalchemy_orm"
Cohesion: 0.08
Nodes (7): get_db(), AuditEvent, create_longlist_proposal(), EvidenceCitation, LonglistProposalRequest, LonglistProposalResponse, RankedSupplierResponse

### Community 49 - "TASK-8 Handoff: Backend Feature B6 - Finalize longlist and lock record, Assemble and dispatch tender"
Cohesion: 0.10
Nodes (20): ATS11: Longlist Lock Flow, ATS12: Tender Dispatch Flow, Audit Events, AuditEvent (existing, used by all operations), Authentication, Backend Flows, Data Models, GET /api/v1/workflows/{need_id}/audit-events (+12 more)

### Community 50 - "@carbon/react"
Cohesion: 0.09
Nodes (23): DispatchStatusBadge(), DispatchStatusBadgeProps, DispatchTable(), DispatchTableProps, headers, LockDetail(), LockDetailProps, LockAndDispatchPage() (+15 more)

### Community 51 - "test_intake_integration.py"
Cohesion: 0.17
Nodes (5): test_create_need_endpoint(), test_create_need_invalid_channel(), test_get_need_endpoint(), test_get_need_not_found(), test_list_needs_endpoint()

### Community 52 - "TASK-5 Handoff: Evidence Retrieval and Supplier Count Validation"
Cohesion: 0.13
Nodes (14): API Endpoints Added, ATS5: Evidence Retrieval Flow, ATS9: Count Validation Flow, Backend Flows, Database Tables, Evidence Records, POST /api/v1/evidence/queries, POST /api/v1/longlists/{proposal_id}/validate-count (+6 more)

### Community 53 - "niche_research_service.py"
Cohesion: 0.18
Nodes (6): NicheResearchService, test_research_niche_providers_creates_audit_event(), test_research_niche_providers_need_not_found(), test_research_niche_providers_no_approved_sources(), test_research_niche_providers_success(), test_research_niche_providers_wrong_classification()

### Community 54 - "need_ingestion_service.py"
Cohesion: 0.12
Nodes (8): create_need(), NeedDetailResponse, NeedIntakeRequest, NeedIntakeResponse, NeedIngestionService, test_ingest_need_creates_audit_event(), test_ingest_need_invalid_channel(), test_ingest_need_success()

### Community 55 - "TASK-7 Handoff: Longlist Proposal and Adjustment Features"
Cohesion: 0.10
Nodes (19): Acceptance Tests (test_longlist_acceptance.py), ATS10: Capture Adjustment, ATS8: Generate Proposal, Backend Flows, Error Scenarios, Implemented Endpoints, Integration Tests (test_longlist_integration.py), Key Behaviors (+11 more)

### Community 56 - "Task 6 Handoff: Panel Mapping and Niche Research (ATS6, ATS7)"
Cohesion: 0.10
Nodes (19): ATS6 Panel Mapping Flow, ATS7 Niche Research Flow, Audit Trail, Backend Flows, Coverage Gap Detection, Database Schema, Frontend Integration Notes, Implemented Endpoints (+11 more)

### Community 57 - "json"
Cohesion: 0.06
Nodes (17): test_j03_complete_finalization_and_dispatch_journey(), test_j03_journey_with_adjustment(), test_j03_validation_failure_blocks_lock(), test_j03_validation_too_many_suppliers_blocks_lock(), test_j01_attribute_review_modification(), test_j01_classification_low_confidence_hold(), test_j01_complete_it_service_journey(), test_j01_complete_single_resource_journey() (+9 more)

### Community 58 - "Longlist"
Cohesion: 0.18
Nodes (8): Longlist, LonglistAdjustmentService, test_capture_adjustment_add_supplier(), test_capture_adjustment_invalid_action_rejected(), test_capture_adjustment_longlist_not_found(), test_capture_adjustment_remove_supplier(), test_capture_adjustment_unknown_supplier_rejected(), test_capture_adjustment_validation_fails()

### Community 59 - "tender_dispatch_service.py"
Cohesion: 0.05
Nodes (6): TOL6DispatchAdapter, TenderDispatch, LonglistRepository, TenderDispatchRepository, dispatch_tender(), TenderDispatchService

### Community 60 - "ClassificationReviewPage.tsx"
Cohesion: 0.14
Nodes (15): ClassificationCard(), ClassificationCardProps, Exemplar, ExemplarTable(), ExemplarTableProps, ClassificationReviewPage(), Exemplar, QueueRow (+7 more)

### Community 61 - "EvidenceAndPanelPage.tsx"
Cohesion: 0.24
Nodes (11): CoverageGapCard(), CoverageGapCardProps, EvidenceTable(), EvidenceTableProps, PanelMatchTable(), PanelMatchTableProps, EvidenceAndPanelPage(), CandidateSupplier (+3 more)

### Community 62 - "need_review_service.py"
Cohesion: 0.15
Nodes (9): AttributeReviewRequest, AttributeReviewResponse, NeedAttributesRequest, NeedAttributesResponse, NeedReviewService, test_review_approve(), test_review_creates_audit_event(), test_review_modify() (+1 more)

### Community 63 - "main.py"
Cohesion: 0.12
Nodes (5): Settings, health(), lifespan(), ready(), seed_data()

### Community 65 - ".map_need_to_panels"
Cohesion: 0.23
Nodes (5): PanelMappingService, test_map_need_to_panels_creates_audit_event(), test_map_need_to_panels_need_not_found(), test_map_need_to_panels_success(), test_map_need_to_panels_with_coverage_gap()

### Community 69 - "start.sh"
Cohesion: 0.48
Nodes (6): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), start.sh script

### Community 71 - "NeedRepository"
Cohesion: 0.12
Nodes (4): NeedRepository, get_need(), list_needs(), test_ingest_need_masks_pii()

### Community 72 - "test_evidence_integration.py"
Cohesion: 0.11
Nodes (9): test_evidence_query_endpoint_multiple_suppliers(), test_evidence_query_endpoint_with_correlation_id(), test_evidence_query_endpoint_with_filters(), test_evidence_query_endpoint_with_no_data(), test_evidence_query_endpoint_with_seed_data(), test_evidence_query_validates_required_fields(), test_validation_endpoint_fail_with_2_suppliers(), test_validation_endpoint_fail_with_7_suppliers() (+1 more)

### Community 73 - "need.py"
Cohesion: 0.17
Nodes (5): get_audit_events(), WorkflowQueryService, test_get_audit_events_empty(), test_get_audit_events_need_not_found(), test_get_audit_events_success()

### Community 75 - "api-client.ts"
Cohesion: 0.22
Nodes (6): apiClient, ApiClientError, request(), HandoffAttemptRow, VmsHandoffPage(), vitest

### Community 76 - "UUID"
Cohesion: 0.10
Nodes (11): test_attribute_confidence_and_validation(), test_niche_research_endpoint_no_approved_sources(), test_niche_research_endpoint_not_found(), test_niche_research_endpoint_success(), test_niche_research_endpoint_wrong_classification(), test_panel_mappings_endpoint_not_found(), test_panel_mappings_endpoint_success(), test_review_attributes_approve() (+3 more)

### Community 77 - "@carbon/react"
Cohesion: 0.28
Nodes (11): ChannelHealthTable(), ChannelHealthTableProps, NeedRecordDetail(), NeedRecordDetailProps, NeedTable(), NeedTableProps, NeedIntakePage(), ChannelHealth (+3 more)

### Community 78 - "pytest"
Cohesion: 0.14
Nodes (8): LonglistProposalService, test_generate_proposal_need_not_found(), test_generate_proposal_rejects_uncited_suppliers(), test_generate_proposal_success(), test_generate_proposal_with_niche_candidates(), test_dispatch_tender_empty_longlist(), test_dispatch_tender_longlist_not_locked(), test_dispatch_tender_missing_contacts()

### Community 82 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, jsdom@^25.0.1, @playwright/test@^1.48.0, tailwindcss@^3.4.15, @testing-library/jest-dom@^6.6.3, @types/node@^26.6.6 (+9 more)

### Community 83 - "AttributeReviewPage.tsx"
Cohesion: 0.22
Nodes (11): AttributeTable(), AttributeTableProps, ConfidenceBar(), ConfidenceBarProps, SourceComparison(), SourceComparisonProps, AttributeReviewPage(), AttributeReviewRequest (+3 more)

### Community 86 - "test_longlist_lock_service.py"
Cohesion: 0.23
Nodes (5): LonglistLockService, test_lock_longlist_already_locked(), test_lock_longlist_not_found(), test_lock_longlist_success(), test_lock_longlist_validation_fails()

### Community 87 - "SupplierCountValidationService"
Cohesion: 0.21
Nodes (7): SupplierCountValidationService, test_validate_count_creates_validation_record(), test_validate_count_fail_with_2_suppliers(), test_validate_count_fail_with_7_suppliers(), test_validate_count_pass_with_3_suppliers(), test_validate_count_pass_with_5_suppliers(), test_validate_count_pass_with_6_suppliers()

### Community 88 - "App.tsx"
Cohesion: 0.13
Nodes (14): App(), AuthProvider(), Dashboard(), DispatchPage(), LockDispatchListPage(), Need, NeedsPage(), headers (+6 more)

### Community 89 - "classification_decision_service.py"
Cohesion: 0.06
Nodes (14): ClassificationReview, ClassificationReviewRepository, execute_vms_handoff(), list_vms_handoffs(), ClassificationReviewRequest, ClassificationReviewResponse, VmsHandoffListItem, VmsHandoffListResponse (+6 more)

### Community 90 - "supplier_evidence_service.py"
Cohesion: 0.26
Nodes (3): EvidenceItem, EvidenceQueryRequest, EvidenceQueryResponse

### Community 91 - "VmsHandoffListPage.tsx"
Cohesion: 0.15
Nodes (13): Header(), Layout(), Sidebar(), EvidenceListPage(), headers, Need, NeedsResponse, headers (+5 more)

### Community 92 - "test_longlist_integration.py"
Cohesion: 0.17
Nodes (5): test_capture_longlist_adjustment_add(), test_capture_longlist_adjustment_invalid_action(), test_capture_longlist_adjustment_remove(), test_create_longlist_proposal_endpoint(), test_create_longlist_proposal_rejects_uncited()

### Community 93 - "PanelMatch"
Cohesion: 0.12
Nodes (9): PanelMatch, test_adjustment_actions_limited_to_add_remove(), test_adjustment_maintains_change_history(), test_adjustment_records_required_fields(), test_adjustment_reruns_validation(), test_every_ranked_supplier_carries_cited_evidence(), test_proposal_contains_required_fields(), test_proposal_includes_supplier_specific_rationale() (+1 more)

### Community 95 - "dependencies"
Cohesion: 0.20
Nodes (9): dependencies, @carbon/icons-react@^11.59.0, @carbon/react@^1.72.0, @carbon/styles@^1.72.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @carbon/styles (+1 more)

### Community 98 - "auth_client"
Cohesion: 0.29
Nodes (4): auth_client(), client(), db_session(), _fresh_schema()

### Community 102 - "capture_longlist_adjustment"
Cohesion: 0.32
Nodes (3): capture_longlist_adjustment(), lock_longlist(), validate_supplier_count()

## Knowledge Gaps
- **2 isolated node(s):** `deutsche-telekom-procurement-backend`, `DATABASE_URL`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 804 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Need` connect `Need` to `sqlalchemy_orm`, `need_review_service.py`, `VmsHandoffService`, `test_intake_integration.py`, `niche_research_service.py`, `need_ingestion_service.py`, `json`, `Longlist`, `need_review_service.py`, `main.py`, `.map_need_to_panels`, `NeedRepository`, `need.py`, `UUID`, `pytest`, `test_longlist_lock_service.py`, `classification_decision_service.py`, `test_longlist_integration.py`, `PanelMatch`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **What connects `deutsche-telekom-procurement-backend`, `DATABASE_URL` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Deutsche Telekom IT Procurement Supplier Selection Workflow` be split into smaller, more focused modules?**
  _Cohesion score 0.05555555555555555 - nodes in this community are weakly interconnected._
- **Why does `AuditEvent` connect `sqlalchemy_orm` to `sqlalchemy_orm`, `.map_need_to_panels`, `panel_mapping_service.py`, `need_review_service.py`, `need.py`, `VmsHandoffService`, `AuditEventRepository`, `niche_research_service.py`, `LonglistAdjustmentService`, `test_longlist_lock_service.py`, `need_ingestion_service.py`, `niche_research_service.py`, `classification_decision_service.py`, `Longlist`, `tender_dispatch_service.py`, `need_review_service.py`, `main.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `sqlalchemy_orm` be split into smaller, more focused modules?**
  _Cohesion score 0.12549019607843137 - nodes in this community are weakly interconnected._
- **Why does `ClassificationReview` connect `classification_decision_service.py` to `sqlalchemy_orm`, `json`, `main.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `test_pipeline_migration_parity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._