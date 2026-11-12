# Graph Report - deutsche-telekom-repo  (2026-11-12)

## Corpus Check
- 195 files · ~66,323 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 35 file(s) not represented in the graph (top: .css 15, (none) 11, .example 2)

## Summary
- 1668 nodes · 3422 edges · 119 communities (70 shown, 49 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 288 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `73e6c3b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- NeedCase
- WorkflowOrchestratorService
- test_pipeline_migration_parity.py
- Deutsche Telekom Procurement Backend
- react
- .validate_supplier_count
- test_smoke.py
- ClassificationReviewPage.tsx
- compilerOptions
- deutsche-telekom-procurement
- Deutsche Telekom IT Procurement - Frontend
- compilerOptions
- auth.ts
- scripts
- PolicyValidation
- tsconfig.json
- LonglistAdjustmentsPage.tsx
- AGN5RuleEngine
- test_cases_integration.py
- devDependencies
- eslint.config.js
- @vitejs/plugin-react
- @playwright/test
- LonglistPolicyService
- EvidenceRepository
- AGN1Service
- TASK-8 Handoff: Backend Feature B6 - Panel Mapping and Longlist Proposal Generation
- Task 4 Handoff: Case Status Initialization & Attribute Extraction
- TASK-5 Handoff: Extraction and Classification Review Endpoints
- HITLReview
- engine
- TASK-9 Handoff: Backend Feature B7 - Supplier Adjustments and Count Validation
- Deutsche Telekom IT Procurement Supplier Selection Workflow
- TASK-6 Handoff: Classification Verdict and VMS Routing
- IntakeQueuePage.tsx
- auth.py
- CaseRepository
- with
- test_dispatch_integration.py
- longlist_schemas.py
- backend
- Acceptance Checks
- EvidenceMappingPage.tsx
- longlists.py
- TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch
- MappingRepository
- typing
- test_agn5_rule_engine.py
- Base
- 005_add_vms_handoff_table.py
- .resolve_mappings
- database
- TASK-3 Backend Implementation Handoff
- case_schemas.py
- LockRepository
- AGN2Service
- .dispatch_tender
- LonglistRepository
- apply_classification_review_decision
- .calculate_completeness_score
- NormalizedNeedResponse
- App.tsx
- TOL4LonglistValidationAdapter
- ClassificationReviewDecisionRequest
- test_adjustments_integration.py
- sqlalchemy
- AGN3Service
- Supplier
- AdjustmentRepository
- WorkflowStepper.tsx
- .validate_supplier_count_with_tol4
- AuditRepository
- sqlalchemy_orm
- TOL2SupplierKBAdapter
- TOL1IngestAdapter
- .validate_lock_preconditions
- TOL5VMSHandoverAdapter
- start.sh
- CaseDetail
- LockRequest
- .validate_dispatch_preconditions
- generic_exception_handler
- AdjustmentRequest
- test_evidence_integration.py
- HITLReviewResponse
- docker-entrypoint.sh
- stop.sh
- VmsRoutingPage.tsx
- @testing-library/jest-dom

## God Nodes (most connected - your core abstractions)
1. `NeedCase` - 77 edges
2. `Base` - 54 edges
3. `HITLReview` - 39 edges
4. `NormalizedNeed` - 38 edges
5. `Supplier` - 33 edges
6. `AGN3Service` - 30 edges
7. `WorkflowOrchestratorService` - 28 edges
8. `AGN5RuleEngine` - 27 edges
9. `AGN1Service` - 25 edges
10. `User` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Classification Verdict Generation` --references--> `HITLReview`  [INFERRED]
  .handoff/TASK-6.md → backend/app/models/hitl_review.py
- `Workflow Orchestrator Method` --references--> `NeedCase`  [INFERRED]
  .handoff/TASK-6.md → backend/app/models/need_case.py
- `AGN5 Rule Engine Method` --references--> `VMSHandoff`  [INFERRED]
  .handoff/TASK-6.md → backend/app/models/vms_handoff.py
- `Cases` --references--> `CaseDetail`  [INFERRED]
  .handoff/TASK-3.md → backend/app/schemas/case_schemas.py
- `Repositories` --references--> `LonglistRepository`  [INFERRED]
  .handoff/TASK-8.md → backend/app/repositories/longlist_repository.py

## Import Cycles
- None detected.

## Communities (119 total, 49 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.13
Nodes (14): @carbon/styles@^1.72.0, jsdom@^25.0.1, tailwindcss@^3.4.17, @types/node@^22.10.2, engines, node, name, private (+6 more)

### Community 1 - "NeedCase"
Cohesion: 0.07
Nodes (15): NormalizedNeed, seed_cases(), seeded_case_without_lock(), test_create_longlist_proposal_endpoint(), test_longlist_proposal_response_shape(), test_longlist_repository(), case_with_high_count(), case_with_low_count() (+7 more)

### Community 2 - "WorkflowOrchestratorService"
Cohesion: 0.08
Nodes (17): ClassificationResult, NeedCase, WorkflowOrchestratorService, test_case_retains_vms_reference(), test_classification_confidence_metadata_stored(), test_classification_rationale_viewable(), test_routed_cases_distinguishable_in_work_queues(), test_supplier_selection_workflow_terminated_after_vms_handoff() (+9 more)

### Community 3 - "test_pipeline_migration_parity.py"
Cohesion: 0.11
Nodes (18): _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version(), _last_name(), _mapped_columns() (+10 more)

### Community 4 - "Deutsche Telekom Procurement Backend"
Cohesion: 0.22
Nodes (8): API Documentation, Database Migrations, Deutsche Telekom Procurement Backend, Environment Variables, Prerequisites, Project Structure, Running Tests, Setup

### Community 5 - "react"
Cohesion: 0.15
Nodes (15): RequireAuth(), RequireAuthProps, Header(), HeaderProps, Layout(), LayoutProps, navigationItems, Sidebar() (+7 more)

### Community 6 - ".validate_supplier_count"
Cohesion: 0.25
Nodes (3): test_supplier_count_invalid_high(), test_supplier_count_invalid_low(), test_supplier_count_valid()

### Community 8 - "ClassificationReviewPage.tsx"
Cohesion: 0.16
Nodes (14): ClassificationReviewCard(), ClassificationReviewCardProps, getVerdictTag(), ExtractionReviewTable(), ExtractionReviewTableProps, formatAttributeValue(), getProvenanceTag(), ClassificationRationaleInput (+6 more)

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 13 - "Deutsche Telekom IT Procurement - Frontend"
Cohesion: 0.12
Nodes (16): API Integration, Build for Production, Default Login Credentials (Development), Deutsche Telekom IT Procurement - Frontend, E2E Tests, Environment Variables, Install Dependencies, Lint (+8 more)

### Community 14 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowSyntheticDefaultImports, composite, lib, module, moduleResolution, noEmit, skipLibCheck (+4 more)

### Community 15 - "auth.ts"
Cohesion: 0.22
Nodes (6): LoginRequest, LoginResponse, User, ErrorResponse, MessageResponse, PaginationWrapper

### Community 16 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test, type-check

### Community 17 - "PolicyValidation"
Cohesion: 0.11
Nodes (6): PolicyValidation, ValidationRepository, test_lock_endpoint_returns_snapshot(), test_lock_precondition_requires_valid_validation(), test_lock_prevents_duplicate_lock(), test_locked_supplier_preserves_rank_position()

### Community 18 - "tsconfig.json"
Cohesion: 0.33
Nodes (5): compilerOptions, composite, tsBuildInfoFile, files, references

### Community 22 - "LonglistAdjustmentsPage.tsx"
Cohesion: 0.15
Nodes (20): AdjustmentForm(), AdjustmentFormProps, DispatchStatus(), DispatchStatusProps, LonglistTable(), LonglistTableProps, ValidationBand(), ValidationBandProps (+12 more)

### Community 24 - "AGN5RuleEngine"
Cohesion: 0.13
Nodes (6): AGN5RuleEngine, test_retrieve_evidence(), test_retrieve_evidence_normalizes_fields(), test_vms_routing_it_service(), test_vms_routing_single_resource(), test_agn5_retrieve_evidence_method()

### Community 25 - "test_cases_integration.py"
Cohesion: 0.09
Nodes (10): test_case_has_source_artifact(), test_case_normalization_completeness(), test_create_case_email(), test_create_case_phone_note(), test_create_case_rfp_document(), test_create_case_supplier_offer(), test_get_case_by_id(), test_get_case_not_found() (+2 more)

### Community 26 - "devDependencies"
Cohesion: 0.12
Nodes (16): devDependencies, autoprefixer@^10.4.20, eslint@^9.17.0, @playwright/test@^1.49.1, postcss@^8.4.49, @testing-library/react@^16.1.0, @types/react@^18.3.18, @types/react-dom@^18.3.5 (+8 more)

### Community 27 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.17.0, eslint-plugin-react-hooks@^5.1.0, eslint-plugin-react-refresh@^0.4.16, globals@^15.14.0, typescript-eslint@^8.18.2, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 28 - "@vitejs/plugin-react"
Cohesion: 0.25
Nodes (6): vite@^6.0.5, @vitejs/plugin-react@^4.3.4, vitest@^2.1.8, vite, @vitejs/plugin-react, vitest

### Community 30 - "LonglistPolicyService"
Cohesion: 0.23
Nodes (3): dispatch_tender(), lock_longlist(), LonglistPolicyService

### Community 31 - "EvidenceRepository"
Cohesion: 0.05
Nodes (21): test_evidence_repository_get_or_create_supplier(), Adapters, Backend Implementation, Database Schema, Endpoint Details, Evidence-Grounding Rule, Evidence Item Structure, Evidence Retrieval (+13 more)

### Community 39 - "AGN1Service"
Cohesion: 0.07
Nodes (18): AGN1Service, test_classification_includes_rationale(), test_classify_need_creates_pending_review(), test_classify_need_it_service_verdict(), test_classify_need_single_resource_verdict(), test_extract_attributes_creates_pending_review(), test_extract_attributes_persisted(), test_extraction_lineage_metadata() (+10 more)

### Community 40 - "TASK-8 Handoff: Backend Feature B6 - Panel Mapping and Longlist Proposal Generation"
Cohesion: 0.07
Nodes (27): case_mapping, Case Mappings, Citation Completeness, Database Schema, functional_group, Functional Groups, Implemented Endpoints, Key Implementation Notes (+19 more)

### Community 41 - "Task 4 Handoff: Case Status Initialization & Attribute Extraction"
Cohesion: 0.08
Nodes (23): AGN1Service (`app/services/agents/agn1_service.py`), Backend Endpoints Added, Case List with Workflow State Filter, CaseRepository Extended, Data Model Additions, Frontend Integration Points, hitl_review Table, HITLService (`app/services/reviews/hitl_service.py`) (+15 more)

### Community 42 - "TASK-5 Handoff: Extraction and Classification Review Endpoints"
Cohesion: 0.09
Nodes (21): After Classification Review, After Extraction Review, API Endpoints, Cases with Classification Review, Cases with Extraction Review, classification_result Table, Classification Review (REQ-DOMAIN-005), Database Schema (+13 more)

### Community 43 - "HITLReview"
Cohesion: 0.09
Nodes (4): HITLReview, ReviewRepository, HITLService, Next Steps for UI Task

### Community 44 - "engine"
Cohesion: 0.25
Nodes (6): auth_client(), client(), db_session(), _fresh_schema(), engine(), engine_with_session()

### Community 45 - "TASK-9 Handoff: Backend Feature B7 - Supplier Adjustments and Count Validation"
Cohesion: 0.11
Nodes (17): Adjustment Capture, API Endpoints, Completed Scope, Database Schema, Integration Tests, Policy Validations, POST /api/v1/cases/{caseId}/adjustments, POST /api/v1/cases/{caseId}/validations/supplier-count (+9 more)

### Community 52 - "Deutsche Telekom IT Procurement Supplier Selection Workflow"
Cohesion: 0.06
Nodes (33): API Documentation, Backend (`backend/.env`), Backend Development, Backend Tests, Building Images, Contributing, Database, Database Migration Errors (+25 more)

### Community 53 - "TASK-6 Handoff: Classification Verdict and VMS Routing"
Cohesion: 0.15
Nodes (12): Acceptance Criteria Verification, AGN5 Rule Engine Method, Classification Verdict Generation, Database Schema, Migration, Seed Cases with Classifications, TASK-6 Handoff: Classification Verdict and VMS Routing, VMS Handoff Endpoint (+4 more)

### Community 54 - "IntakeQueuePage.tsx"
Cohesion: 0.17
Nodes (12): CaseListTable(), CaseListTableProps, IntakeForm(), IntakeFormProps, apiClient, IntakeQueuePage(), CaseDetail, CaseListItem (+4 more)

### Community 55 - "auth.py"
Cohesion: 0.07
Nodes (16): Settings, login(), LoginRequest, LoginResponse, UserResponse, hash_password(), create_access_token(), decode_access_token() (+8 more)

### Community 56 - "CaseRepository"
Cohesion: 0.10
Nodes (10): CaseRepository, create_case(), get_case(), list_cases(), trigger_vms_handoff(), create_adjustment(), create_longlist_proposal(), get_case_evidence() (+2 more)

### Community 57 - "with"
Cohesion: 0.08
Nodes (27): defaults, name, runs-on, steps, run, defaults, name, runs-on (+19 more)

### Community 58 - "test_dispatch_integration.py"
Cohesion: 0.09
Nodes (6): LockedLonglist, TenderDispatch, DispatchRepository, test_dispatch_endpoint_blocks_without_lock(), test_dispatch_endpoint_returns_recipients(), test_lock_endpoint_blocks_without_validation()

### Community 59 - "longlist_schemas.py"
Cohesion: 0.25
Nodes (3): CaseEvidenceResponse, EvidenceItemResponse, SupplierResponse

### Community 60 - "backend"
Cohesion: 0.09
Nodes (22): BACKEND_HOST, build, environment, ports, volumes, x-preview-port, args, context (+14 more)

### Community 62 - "Acceptance Checks"
Cohesion: 0.10
Nodes (19): 1. README.md quick start instructions match actual ./start.sh behavior, 2. backend/README.md setup instructions match actual backend structure, 3. frontend/README.md setup instructions match actual frontend structure, 4. backend/dev.env lists all env vars backend reads with correct defaults, 5. frontend/.env.example lists VITE_API_URL commented out (no absolute URL default), 6. start.sh printed seed credentials match backend/app/seed.py created users, 7. Frontend login form hints or defaults match seed credentials exactly, 8. shared_config.json api_base_path matches backend router prefix and frontend api-client path construction (+11 more)

### Community 63 - "EvidenceMappingPage.tsx"
Cohesion: 0.25
Nodes (6): CaseDetail, CaseMapping, EvidenceItem, EvidenceResponse, MappingResponse, Supplier

### Community 64 - "longlists.py"
Cohesion: 0.07
Nodes (8): get_db(), health_check(), lifespan(), get_current_user(), User, UserRepository, ExtractionReviewDecisionRequest, test_user()

### Community 65 - "TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch"
Cohesion: 0.06
Nodes (35): AGN3Service Extended, Database Schema, Dispatch Action, Dispatch Endpoint, Dispatch Errors, Dispatch Precondition, Dispatch Request, Dispatch Response (+27 more)

### Community 66 - "MappingRepository"
Cohesion: 0.09
Nodes (7): MappingRepository, PanelMappingService, test_mapping_repository_idempotency(), test_store_and_list_mappings(), Panel Mapping Service, Repositories, Services and Adapters

### Community 68 - "test_agn5_rule_engine.py"
Cohesion: 0.13
Nodes (7): test_initial_workflow_state_below_threshold(), test_initial_workflow_state_high_completeness(), test_initial_workflow_state_low_completeness(), test_initial_workflow_state_threshold_completeness(), test_supplier_count_with_tol4(), test_supplier_count_with_tol4_invalid_high(), test_supplier_count_with_tol4_invalid_low()

### Community 69 - "Base"
Cohesion: 0.07
Nodes (19): Base, CaseMapping, CommissionedSoW, FunctionalGroup, HistoricalOrder, LockedSupplier, Panel, SourceArtifact (+11 more)

### Community 71 - ".resolve_mappings"
Cohesion: 0.29
Nodes (3): test_resolve_mappings(), test_resolve_mappings_different_categories(), AGN5 Rule Engine Extensions

### Community 72 - "database"
Cohesion: 0.11
Nodes (18): PIP_TARGET, build, depends_on, environment, args, environment, image, ports (+10 more)

### Community 74 - "TASK-3 Backend Implementation Handoff"
Cohesion: 0.20
Nodes (9): CaseDetail, CaseListItem, Overview, Response Shapes, Seed Data, TASK-3 Backend Implementation Handoff, Technical Notes, Testing (+1 more)

### Community 75 - "case_schemas.py"
Cohesion: 0.15
Nodes (7): DispatchRequest, CaseListItem, CaseListResponse, CreateCaseRequest, SourceArtifactResponse, ErrorResponse, MessageResponse

### Community 76 - "LockRepository"
Cohesion: 0.15
Nodes (4): LockRepository, test_lock_longlist_creates_snapshot(), LockRepository (New), Repositories

### Community 77 - "AGN2Service"
Cohesion: 0.27
Nodes (4): AGN2Service, test_agn2_citation_completeness(), test_agn2_empty_evidence(), test_agn2_generate_ranked_longlist()

### Community 78 - ".dispatch_tender"
Cohesion: 0.12
Nodes (6): test_dispatch_creates_recipients(), test_dispatch_precondition_requires_lock(), test_dispatch_prevents_duplicate_dispatch(), test_dispatch_records_batch_reference(), test_dispatch_status_reflects_outcomes(), DispatchRepository (New)

### Community 80 - "apply_classification_review_decision"
Cohesion: 0.22
Nodes (3): apply_classification_review_decision(), apply_extraction_review_decision(), ReviewDecisionResponse

### Community 81 - ".calculate_completeness_score"
Cohesion: 0.20
Nodes (4): test_completeness_score_all_filled(), test_completeness_score_empty(), test_completeness_score_empty_dict(), test_completeness_score_partial_filled()

### Community 83 - "App.tsx"
Cohesion: 0.13
Nodes (15): App(), LoginPage(), CaseHeader(), CaseHeaderProps, WorkflowStepper(), AuthProvider(), formatDateTime(), getStatusBadgeColor() (+7 more)

### Community 87 - "TOL4LonglistValidationAdapter"
Cohesion: 0.13
Nodes (3): TOL3PanelMappingAdapter, TOL4LonglistValidationAdapter, TOL3 Panel Mapping Adapter

### Community 89 - "test_adjustments_integration.py"
Cohesion: 0.18
Nodes (5): test_adjustment_captures_actor_and_timestamp(), test_adjustment_case_not_found(), test_adjustment_history_remains_visible(), test_capture_adjustment_add(), test_capture_adjustment_remove()

### Community 90 - "sqlalchemy"
Cohesion: 0.07
Nodes (13): run_migrations_offline(), run_migrations_online(), upgrade(), downgrade(), upgrade(), upgrade(), upgrade(), downgrade() (+5 more)

### Community 91 - "AGN3Service"
Cohesion: 0.20
Nodes (7): AGN3Service, test_capture_adjustment_add_duplicate_supplier(), test_capture_adjustment_add_new_supplier(), test_capture_adjustment_invalid_change_type(), test_capture_adjustment_no_proposal(), test_capture_adjustment_remove_existing_supplier(), test_capture_adjustment_remove_non_existent_supplier()

### Community 92 - "Supplier"
Cohesion: 0.13
Nodes (8): LonglistProposal, ProposalSupplier, Supplier, test_adjustment_invalid_change_type(), test_case_with_proposal(), test_case_setup(), seeded_locked_case(), seeded_case_with_proposal()

### Community 94 - "WorkflowStepper.tsx"
Cohesion: 0.17
Nodes (10): dependencies, @carbon/icons-react@^11.54.0, @carbon/react@^1.72.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, WorkflowStep, WorkflowStepperProps (+2 more)

### Community 95 - ".validate_supplier_count_with_tol4"
Cohesion: 0.16
Nodes (4): Adapters, Architecture Components, Repositories, Services

### Community 97 - "sqlalchemy_orm"
Cohesion: 0.17
Nodes (3): AuditLog, WorkflowEvent, AuditService

### Community 100 - ".validate_lock_preconditions"
Cohesion: 0.25
Nodes (3): test_lock_preconditions_invalid_count(), test_lock_preconditions_missing_citations(), test_lock_preconditions_valid()

### Community 101 - "TOL5VMSHandoverAdapter"
Cohesion: 0.15
Nodes (3): TOL5VMSHandoverAdapter, test_route_single_resource_case(), test_route_single_resource_case_without_session()

### Community 102 - "start.sh"
Cohesion: 0.39
Nodes (6): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), start.sh script

### Community 103 - "CaseDetail"
Cohesion: 0.40
Nodes (4): CaseDetail, Authentication, Cases, Implemented Endpoints

### Community 108 - "test_evidence_integration.py"
Cohesion: 0.14
Nodes (8): CaseEvidence, EvidenceService, test_evidence_found_flag(), test_evidence_linked_to_case(), test_evidence_service_list_evidence(), test_evidence_service_store_evidence(), test_get_case_evidence_endpoint(), test_get_case_evidence_endpoint_not_found()

### Community 128 - "VmsRoutingPage.tsx"
Cohesion: 0.25
Nodes (5): ApiError, request(), AuditEvent, CaseDetail, VMSHandoff

## Knowledge Gaps
- **2 isolated node(s):** `DATABASE_URL`, `deutsche-telekom-procurement`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 836 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NeedCase` connect `WorkflowOrchestratorService` to `longlists.py`, `NeedCase`, `sqlalchemy_orm`, `typing`, `test_agn5_rule_engine.py`, `Base`, `TOL5VMSHandoverAdapter`, `AGN1Service`, `MappingRepository`, `HITLReview`, `test_evidence_integration.py`, `AGN2Service`, `TASK-6 Handoff: Classification Verdict and VMS Routing`, `CaseRepository`, `test_dispatch_integration.py`, `AGN3Service`, `Supplier`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `NeedCase` (e.g. with `CaseRepository` and `Workflow Orchestrator Method`) actually correct?**
  _`NeedCase` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DATABASE_URL`, `deutsche-telekom-procurement` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch` connect `TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch` to `LockRepository`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Should `NeedCase` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._
- **Why does `Repositories` connect `LockRepository` to `TASK-10 Handoff: Backend Feature B8 - Lock and Tender Dispatch`, `.dispatch_tender`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._