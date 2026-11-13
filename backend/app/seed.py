import json
import uuid
from datetime import UTC, datetime, timedelta

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.audit_event import AuditEvent
from app.models.classification_review import ClassificationReview
from app.models.longlist import Longlist
from app.models.longlist_proposal import LonglistProposal
from app.models.longlist_ranked_supplier import LonglistRankedSupplier
from app.models.need import Need
from app.models.need_attributes import NeedAttributes
from app.models.panel_match import PanelMatch
from app.models.provider_candidate import ProviderCandidate
from app.models.supplier_count_validation import SupplierCountValidation
from app.models.supplier_evidence_item import SupplierEvidenceItem
from app.models.tender_dispatch import TenderDispatch
from app.models.user import User
from app.models.vms_handoff import VmsHandoff


def seed_data():
    """Idempotent seed data loader for local development."""
    session = SessionLocal()

    try:
        print("Loading seed data...")
        now = datetime.now(UTC)

        # Seed users with role-specific passwords (always check and seed if missing)
        existing_users = session.query(User).count()
        if existing_users == 0:
            print("Seeding users...")
            users = [
                User(
                    email="procurement.reviewer@telekom.de",
                    hashed_password=hash_password("Review-pass-1"),
                    role="procurement_reviewer",
                    is_active=True,
                ),
                User(
                    email="longlist.finalization@telekom.de",
                    hashed_password=hash_password("Finalize-pass-1"),
                    role="longlist_finalization_owner",
                    is_active=True,
                ),
                User(
                    email="business.collaborator@telekom.de",
                    hashed_password=hash_password("Collab-pass-1"),
                    role="business_unit_collaborator",
                    is_active=True,
                ),
            ]
            for user in users:
                session.add(user)
            session.commit()
            print(f"Created {len(users)} users")
        else:
            print(f"Users already exist ({existing_users}), skipping user creation...")

        # Check if other seed data already exists
        existing_need = session.query(Need).first()
        if existing_need:
            # Update existing needs with classification_verdict if missing
            needs_without_verdict = session.query(Need).filter(
                Need.classification_verdict.is_(None)
            ).all()
            
            if needs_without_verdict:
                print(f"Updating {len(needs_without_verdict)} needs with classification_verdict...")
                
                # Map of need UUIDs to their classification verdicts
                verdict_map = {
                    uuid.UUID("00000000-0000-0000-0000-000000000001"): ("it_service", 0.92),
                    uuid.UUID("00000000-0000-0000-0000-000000000002"): ("single_resource", 0.94),
                    uuid.UUID("00000000-0000-0000-0000-000000000003"): ("it_service", 0.88),
                    uuid.UUID("00000000-0000-0000-0000-000000000004"): ("it_service", 0.91),
                    uuid.UUID("00000000-0000-0000-0000-000000000005"): ("single_resource", 0.96),
                    uuid.UUID("00000000-0000-0000-0000-000000000008"): ("it_service", 0.87),
                }
                
                for need in needs_without_verdict:
                    if need.id in verdict_map:
                        verdict, confidence = verdict_map[need.id]
                        need.classification_verdict = verdict
                        need.classification_confidence = confidence
                        print(f"  Updated need {need.id} with verdict={verdict}")
                
                session.commit()
                print("Classification verdict updates complete")
            else:
                print("Needs already exist with classification_verdict, skipping need creation...")
            
            return

        # Seed Need 1: IT service need (classified, with evidence and longlist)
        need_1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        need_1 = Need(
            id=need_1_id,
            business_unit_id="BU-NORTH-001",
            channel_type="rfp",
            arrival_timestamp=now - timedelta(days=10),
            raw_artifact_ref="s3://intake/rfp-2024-001.pdf",
            normalized_payload_json=json.dumps({"title": "Cloud Infrastructure Services"}),
            status="classified_it_service",
            classification_verdict="it_service",
            classification_confidence=0.92,
            correlation_id="CORR-001",
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=5),
        )
        session.add(need_1)

        # Need 1 attributes
        need_1_attrs = NeedAttributes(
            id=uuid.uuid4(),
            need_id=need_1_id,
            service_type="Cloud Infrastructure",
            scope_description="Multi-cloud infrastructure management and optimization",
            estimated_volume_duration="24 months, 5-10 FTE",
            required_skills=json.dumps(["AWS", "Azure", "Kubernetes", "Terraform"]),
            budget_indication="€500K-€800K annually",
            delivery_location="Germany (remote possible)",
            field_confidence=json.dumps({"service_type": 0.95, "scope_description": 0.88}),
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        )
        session.add(need_1_attrs)

        # Need 1 classification
        classification_1 = ClassificationReview(
            id=uuid.uuid4(),
            need_id=need_1_id,
            classification_verdict="it_service",
            classification_confidence=0.92,
            rationale="Multi-cloud service requiring team, not single resource",
            review_decision="approve",
            reviewer_id="procurement.reviewer@telekom.de",
            escalation_required=False,
            exemplars_referenced=json.dumps(["EXEMPLAR-IT-001", "EXEMPLAR-IT-005"]),
            created_at=now - timedelta(days=9),
            updated_at=now - timedelta(days=9),
        )
        session.add(classification_1)

        # Need 1 evidence including required seed suppliers
        evidence_items = [
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-001",
                evidence_type="historical_project",
                source_system="SEED",
                source_reference="TOL2/project/PRJ-2023-045",
                service_category="Cloud Infrastructure",
                business_unit_id="BU-NORTH-001",
                delivery_period="18 months",
                quality_rating=4.5,
                citation_text="Cloud migration for manufacturing division, 18-month engagement",
                is_seed_data=True,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                evidence_limited_flag=False,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-002",
                evidence_type="historical_sow",
                source_system="SEED",
                source_reference="TOL2/sow/SOW-2022-112",
                service_category="Cloud Infrastructure",
                business_unit_id="BU-NORTH-001",
                delivery_period=None,
                quality_rating=4.2,
                citation_text="AWS infrastructure services for financial sector client",
                is_seed_data=True,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                evidence_limited_flag=False,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-003",
                evidence_type="quality_rating",
                source_system="SEED",
                source_reference="TOL2/rating/2023-Q4",
                service_category="Cloud Infrastructure",
                business_unit_id=None,
                delivery_period=None,
                citation_text="Consistent 4.3 rating across 8 cloud projects",
                quality_rating=4.3,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0231",
                evidence_type="historical_sow",
                source_system="SEED",
                source_reference="SOW-2022-0871",
                citation_text="IT infrastructure services SoW, 24-month engagement",
                quality_rating=4.4,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0231",
                evidence_type="historical_order",
                source_system="SEED",
                source_reference="ORD-2023-4410",
                citation_text="Cloud services order, delivered on schedule with high quality",
                quality_rating=4.6,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0118",
                evidence_type="historical_sow",
                source_system="SEED",
                source_reference="SOW-2021-0522",
                citation_text="Enterprise application services SoW",
                quality_rating=4.1,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0307",
                evidence_type="supplier_service_match",
                source_system="SEED",
                source_reference="PANEL-MATCH-2024-001",
                citation_text="Panel-qualified cloud services provider",
                quality_rating=4.0,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0045",
                evidence_type="supplier_service_match",
                source_system="SEED",
                source_reference="PANEL-MATCH-2024-002",
                citation_text="Panel-qualified infrastructure services provider",
                quality_rating=3.9,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
            SupplierEvidenceItem(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0412",
                evidence_type="supplier_service_match",
                source_system="SEED",
                source_reference="PANEL-MATCH-2024-003",
                citation_text="Panel-qualified network and cloud services provider",
                quality_rating=4.2,
                evidence_limited_flag=False,
                evidence_snapshot_timestamp=now - timedelta(days=8),
                is_seed_data=True,
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=8),
            ),
        ]
        for item in evidence_items:
            session.add(item)

        # Need 1 panel matches
        panel_matches = [
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-001",
                panel_source="IT-CLOUD-PANEL-A",
                functional_group="Multi-Cloud Services",
                provenance_ref="TOL3/panel/IT-CLOUD-PANEL-A/2024-Q1",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-002",
                panel_source="IT-CLOUD-PANEL-A",
                functional_group="AWS Specialists",
                provenance_ref="TOL3/panel/IT-CLOUD-PANEL-A/2024-Q1",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-003",
                panel_source="IT-INFRA-PANEL-B",
                functional_group="Infrastructure Management",
                provenance_ref="TOL3/panel/IT-INFRA-PANEL-B/2024-Q1",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-CLOUD-004",
                panel_source="IT-CLOUD-PANEL-A",
                functional_group="Azure Specialists",
                provenance_ref="TOL3/panel/IT-CLOUD-PANEL-A/2024-Q1",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            # Task 6 required seed data: panel matches for SUP-0231, SUP-0118, SUP-0307, SUP-0045, SUP-0412
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0231",
                panel_source="Cloud and hosting panel",
                functional_group="Cloud Infrastructure",
                provenance_ref="Panel registry entry 2024-03-15",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0118",
                panel_source="Platform engineering panel",
                functional_group="Platform Services",
                provenance_ref="Panel registry entry 2024-02-10",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0307",
                panel_source="Managed services panel",
                functional_group="Managed Operations",
                provenance_ref="Panel registry entry 2024-01-20",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0045",
                panel_source="Cloud and hosting panel",
                functional_group="Hybrid Cloud Solutions",
                provenance_ref="Panel registry entry 2024-03-15",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
            PanelMatch(
                id=uuid.uuid4(),
                need_id=need_1_id,
                supplier_id="SUP-0412",
                panel_source="Managed services panel",
                functional_group="Network and Cloud Services",
                provenance_ref="Panel registry entry 2024-01-20",
                coverage_gap_flag=False,
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(days=7),
            ),
        ]
        for match in panel_matches:
            session.add(match)

        # Need 1 longlist proposal
        proposal_1_id = uuid.UUID("00000000-0000-0000-0000-000000000011")
        proposal_1 = LonglistProposal(
            id=proposal_1_id,
            need_id=need_1_id,
            ranked_suppliers=json.dumps([
                "SUP-CLOUD-001", "SUP-CLOUD-002", "SUP-CLOUD-003", "SUP-CLOUD-004"
            ]),
            evidence_limited_flag=False,
            review_status="approved",
            reviewer_notes="Strong panel coverage, well-cited",
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=5),
        )
        session.add(proposal_1)

        # Need 1 ranked suppliers
        ranked_suppliers = [
            LonglistRankedSupplier(
                id=uuid.uuid4(),
                proposal_id=proposal_1_id,
                supplier_id="SUP-CLOUD-001",
                rank=1,
                panel_source="IT-CLOUD-PANEL-A",
                evidence_citations=json.dumps(["TOL2/project/PRJ-2023-045"]),
                rank_rationale="Strongest multi-cloud experience and highest quality rating",
                confidence=0.88,
                created_at=now - timedelta(days=6),
                updated_at=now - timedelta(days=6),
            ),
            LonglistRankedSupplier(
                id=uuid.uuid4(),
                proposal_id=proposal_1_id,
                supplier_id="SUP-CLOUD-002",
                rank=2,
                panel_source="IT-CLOUD-PANEL-A",
                evidence_citations=json.dumps(["TOL2/sow/SOW-2022-112"]),
                rank_rationale="Solid AWS track record",
                confidence=0.82,
                created_at=now - timedelta(days=6),
                updated_at=now - timedelta(days=6),
            ),
            LonglistRankedSupplier(
                id=uuid.uuid4(),
                proposal_id=proposal_1_id,
                supplier_id="SUP-CLOUD-003",
                rank=3,
                panel_source="IT-INFRA-PANEL-B",
                evidence_citations=json.dumps(["TOL2/rating/2023-Q4"]),
                rank_rationale="Consistent performer across infrastructure projects",
                confidence=0.79,
                created_at=now - timedelta(days=6),
                updated_at=now - timedelta(days=6),
            ),
            LonglistRankedSupplier(
                id=uuid.uuid4(),
                proposal_id=proposal_1_id,
                supplier_id="SUP-CLOUD-004",
                rank=4,
                panel_source="IT-CLOUD-PANEL-A",
                evidence_citations=json.dumps(["TOL3/panel/IT-CLOUD-PANEL-A/2024-Q1"]),
                rank_rationale="Azure specialist, panel-only citation",
                confidence=0.71,
                created_at=now - timedelta(days=6),
                updated_at=now - timedelta(days=6),
            ),
        ]
        for supplier in ranked_suppliers:
            session.add(supplier)

        # Need 1 validation (pass)
        validation_1 = SupplierCountValidation(
            id=uuid.uuid4(),
            proposal_id=proposal_1_id,
            supplier_count=4,
            validation_verdict="pass",
            violations=None,
            triggered_by="ATS9",
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=5),
        )
        session.add(validation_1)

        # Need 1 locked longlist
        longlist_1_id = uuid.UUID("00000000-0000-0000-0000-000000000021")
        longlist_1 = Longlist(
            id=longlist_1_id,
            need_id=need_1_id,
            proposal_id=proposal_1_id,
            suppliers=json.dumps(["SUP-CLOUD-001", "SUP-CLOUD-002", "SUP-CLOUD-003", "SUP-CLOUD-004"]),
            locked=True,
            locked_at=now - timedelta(days=4),
            locked_by="longlist.finalization@telekom.de",
            validation_verdict_at_lock="pass",
            change_history=json.dumps([]),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=4),
        )
        session.add(longlist_1)

        # Need 1 tender dispatches
        batch_id_1 = "BATCH-2024-001"
        dispatches = [
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_1_id,
                dispatch_batch_id=batch_id_1,
                supplier_id="SUP-CLOUD-001",
                supplier_contact="contact@supcloud1.example.com",
                dispatch_status="delivered",
                retry_count=0,
                delivery_confirmation_ref="TOL6/conf/CONF-001-001",
                error_detail=None,
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=3),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_1_id,
                dispatch_batch_id=batch_id_1,
                supplier_id="SUP-CLOUD-002",
                supplier_contact="sales@supcloud2.example.com",
                dispatch_status="delivered",
                retry_count=0,
                delivery_confirmation_ref="TOL6/conf/CONF-001-002",
                error_detail=None,
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=3),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_1_id,
                dispatch_batch_id=batch_id_1,
                supplier_id="SUP-CLOUD-003",
                supplier_contact="tenders@supcloud3.example.com",
                dispatch_status="retrying",
                retry_count=2,
                delivery_confirmation_ref=None,
                error_detail="Temporary network timeout",
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=2),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_1_id,
                dispatch_batch_id=batch_id_1,
                supplier_id="SUP-CLOUD-004",
                supplier_contact="procurement@supcloud4.example.com",
                dispatch_status="delivered",
                retry_count=1,
                delivery_confirmation_ref="TOL6/conf/CONF-001-004",
                error_detail=None,
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=3),
            ),
        ]
        for dispatch in dispatches:
            session.add(dispatch)

        # Seed Need 2: Single resource need (VMS routed)
        need_2_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
        need_2 = Need(
            id=need_2_id,
            business_unit_id="BU-SOUTH-002",
            channel_type="email",
            arrival_timestamp=now - timedelta(days=7),
            raw_artifact_ref="email://inbox/msg-2024-456.eml",
            normalized_payload_json=json.dumps({"title": "Java Developer for 6 months"}),
            status="vms_routed_terminal",
            classification_verdict="single_resource",
            classification_confidence=0.94,
            correlation_id="CORR-002",
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=6),
        )
        session.add(need_2)

        need_2_attrs = NeedAttributes(
            id=uuid.uuid4(),
            need_id=need_2_id,
            service_type="Software Development",
            scope_description="Java backend developer, 6-month contract",
            estimated_volume_duration="6 months, 1 FTE",
            required_skills=json.dumps(["Java", "Spring Boot", "REST APIs"]),
            budget_indication="€60K-€75K total",
            delivery_location="Berlin office",
            field_confidence=json.dumps({"service_type": 0.91, "scope_description": 0.93}),
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=7),
        )
        session.add(need_2_attrs)

        classification_2 = ClassificationReview(
            id=uuid.uuid4(),
            need_id=need_2_id,
            classification_verdict="single_resource",
            classification_confidence=0.94,
            rationale="Single developer, fixed term, clearly single resource",
            review_decision="approve",
            reviewer_id="procurement.reviewer@telekom.de",
            escalation_required=False,
            exemplars_referenced=json.dumps(["EXEMPLAR-SR-003"]),
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=6),
        )
        session.add(classification_2)

        vms_handoff = VmsHandoff(
            id=uuid.uuid4(),
            need_id=need_2_id,
            handover_confirmation=True,
            vms_reference_id="VMS-REF-2024-789",
            workflow_status="vms_routed_terminal",
            request_payload_json=json.dumps({"need_id": str(need_2_id)}),
            response_payload_json=json.dumps({"confirmation": True, "vms_ref": "VMS-REF-2024-789"}),
            error_detail=None,
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=6),
        )
        session.add(vms_handoff)

        # Seed Need 3: IT service with evidence_limited_flag
        need_3_id = uuid.UUID("00000000-0000-0000-0000-000000000003")
        need_3 = Need(
            id=need_3_id,
            business_unit_id="BU-WEST-003",
            channel_type="phone",
            arrival_timestamp=now - timedelta(days=5),
            raw_artifact_ref="phone://notes/2024-11-08-001.txt",
            normalized_payload_json=json.dumps({"title": "AI/ML Model Development"}),
            status="evidence_retrieved",
            classification_verdict="it_service",
            classification_confidence=0.89,
            correlation_id="CORR-003",
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=3),
        )
        session.add(need_3)

        need_3_attrs = NeedAttributes(
            id=uuid.uuid4(),
            need_id=need_3_id,
            service_type="AI/ML Development",
            scope_description="Machine learning model development and deployment",
            estimated_volume_duration="12 months, 3-5 specialists",
            required_skills=json.dumps(["Python", "TensorFlow", "MLOps", "Data Science"]),
            budget_indication="€300K-€450K annually",
            delivery_location="Remote (EU-based)",
            field_confidence=json.dumps({"service_type": 0.87, "scope_description": 0.84}),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=5),
        )
        session.add(need_3_attrs)

        classification_3 = ClassificationReview(
            id=uuid.uuid4(),
            need_id=need_3_id,
            classification_verdict="it_service",
            classification_confidence=0.89,
            rationale="Multi-specialist AI/ML service team requirement",
            review_decision="approve",
            reviewer_id="procurement.reviewer@telekom.de",
            escalation_required=False,
            exemplars_referenced=json.dumps(["EXEMPLAR-IT-007"]),
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=4),
        )
        session.add(classification_3)

        # Need 3 evidence with limited flag
        evidence_3 = SupplierEvidenceItem(
            id=uuid.uuid4(),
            need_id=need_3_id,
            supplier_id="SUP-AI-001",
            evidence_type="fallback_seed",
                source_system="SEED",
            source_reference="SEED/representative-ai-providers",
            citation_text="Representative AI/ML provider (TOL2 unavailable, using fallback)",
            quality_rating=None,
            evidence_limited_flag=True,
            evidence_snapshot_timestamp=now - timedelta(days=3),
            is_seed_data=True,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3),
        )
        session.add(evidence_3)

        # Need 3 panel with coverage gap
        panel_3 = PanelMatch(
            id=uuid.uuid4(),
            need_id=need_3_id,
            supplier_id="SUP-AI-001",
            panel_source="IT-DATA-PANEL-C",
            functional_group="Data Science",
            provenance_ref="TOL3/panel/IT-DATA-PANEL-C/2024-Q1",
            coverage_gap_flag=True,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3),
        )
        session.add(panel_3)

        # Need 3 niche research candidates
        niche_candidates = [
            ProviderCandidate(
                id=uuid.uuid4(),
                need_id=need_3_id,
                candidate_name="DeepTech AI Solutions",
                supplier_id="SUP-AI-NICHE-001",
                capability_gap="Specialized MLOps automation not covered by panel",
                source_citations=json.dumps(["GOV-SOURCE/ai-directory-2024", "GOV-SOURCE/certified-ml-providers"]),
                review_status="accepted",
                reviewer_notes="Approved for inclusion, meets governed source requirements",
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            ),
            # Task 6 required seed data: provider candidates SUP-0518 and SUP-0533 with source citations
            ProviderCandidate(
                id=uuid.uuid4(),
                need_id=need_3_id,
                candidate_name="CloudTech Solutions GmbH",
                supplier_id="SUP-0518",
                capability_gap="Specialized quantum-resistant encryption for ML models",
                source_citations=json.dumps([
                    "Gaia-X participant registry 2024-08-15",
                    "ISO 27001 certified provider",
                ]),
                review_status="pending",
                reviewer_notes=None,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=2),
            ),
            ProviderCandidate(
                id=uuid.uuid4(),
                need_id=need_3_id,
                candidate_name="SecureOps AG",
                supplier_id="SUP-0533",
                capability_gap="Advanced security compliance for AI/ML workloads",
                source_citations=json.dumps([
                    "BSI C5 attestation 2024-06-20",
                    "Federal approved supplier list",
                ]),
                review_status="accepted",
                reviewer_notes="Approved after security review",
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            ),
        ]
        for candidate in niche_candidates:
            session.add(candidate)

        # Seed Need 4: Validation failure example (unlocked longlist)
        need_4_id = uuid.UUID("00000000-0000-0000-0000-000000000004")
        need_4 = Need(
            id=need_4_id,
            business_unit_id="BU-EAST-004",
            channel_type="supplier_offer",
            arrival_timestamp=now - timedelta(days=4),
            raw_artifact_ref="supplier://offers/2024-offer-123.pdf",
            normalized_payload_json=json.dumps({"title": "Network Security Assessment"}),
            status="proposal_reviewed",
            classification_verdict="it_service",
            classification_confidence=0.85,
            correlation_id="CORR-004",
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=1),
        )
        session.add(need_4)

        need_4_attrs = NeedAttributes(
            id=uuid.uuid4(),
            need_id=need_4_id,
            service_type="Security Assessment",
            scope_description="Network security audit and penetration testing",
            estimated_volume_duration="3 months engagement",
            required_skills=json.dumps(["Security Auditing", "Penetration Testing", "Network Security"]),
            budget_indication="€120K-€180K",
            delivery_location="Hybrid (on-site + remote)",
            field_confidence=json.dumps({"service_type": 0.90, "scope_description": 0.86}),
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=4),
        )
        session.add(need_4_attrs)

        classification_4 = ClassificationReview(
            id=uuid.uuid4(),
            need_id=need_4_id,
            classification_verdict="it_service",
            classification_confidence=0.85,
            rationale="Security assessment requiring specialized team",
            review_decision="approve",
            reviewer_id="procurement.reviewer@telekom.de",
            escalation_required=False,
            exemplars_referenced=json.dumps(["EXEMPLAR-IT-010"]),
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3),
        )
        session.add(classification_4)

        # Need 4 proposal with only 2 suppliers (will fail validation)
        proposal_4_id = uuid.UUID("00000000-0000-0000-0000-000000000014")
        proposal_4 = LonglistProposal(
            id=proposal_4_id,
            need_id=need_4_id,
            ranked_suppliers=json.dumps(["SUP-SEC-001", "SUP-SEC-002"]),
            evidence_limited_flag=False,
            review_status="approved",
            reviewer_notes="Only 2 qualified suppliers found in panels",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=1),
        )
        session.add(proposal_4)

        # Need 4 validation (fail - too few suppliers)
        validation_4 = SupplierCountValidation(
            id=uuid.uuid4(),
            proposal_id=proposal_4_id,
            supplier_count=2,
            validation_verdict="fail",
            violations=json.dumps(["Supplier count 2 below minimum threshold of 3"]),
            triggered_by="ATS9",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )
        session.add(validation_4)

        # Need 4 unlocked longlist (cannot lock due to validation failure)
        longlist_4_id = uuid.UUID("00000000-0000-0000-0000-000000000024")
        longlist_4 = Longlist(
            id=longlist_4_id,
            need_id=need_4_id,
            proposal_id=proposal_4_id,
            suppliers=json.dumps(["SUP-SEC-001", "SUP-SEC-002"]),
            locked=False,
            locked_at=None,
            locked_by=None,
            validation_verdict_at_lock=None,
            change_history=json.dumps([]),
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )
        session.add(longlist_4)

        # TASK-8 seed: Locked longlist LL-2024-0402 with 5 suppliers and adjustments
        need_8_id = uuid.UUID("00000000-0000-0000-0000-000000000008")
        need_8 = Need(
            id=need_8_id,
            business_unit_id="BU-TASK8-001",
            channel_type="rfp",
            arrival_timestamp=now - timedelta(days=20),
            raw_artifact_ref="s3://intake/rfp-2024-0402.pdf",
            normalized_payload_json=json.dumps({"title": "IT Service Management Platform"}),
            status="tender_dispatched",
            classification_verdict="it_service",
            classification_confidence=0.90,
            correlation_id="CORR-LL-2024-0402",
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=1),
        )
        session.add(need_8)

        # Locked longlist LL-2024-0402
        longlist_8_id = uuid.UUID("00000000-0000-0000-0000-000000000402")
        longlist_8 = Longlist(
            id=longlist_8_id,
            need_id=need_8_id,
            proposal_id=None,
            suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0045", "SUP-0518", "SUP-0412"]),
            locked=True,
            locked_at=now - timedelta(days=2),
            locked_by="longlist.finalization@telekom.de",
            validation_verdict_at_lock="pass",
            change_history=json.dumps([
                {
                    "action": "add",
                    "timestamp": (now - timedelta(days=3)).isoformat(),
                    "actor": "business.collaborator@telekom.de",
                    "supplier_id": "SUP-0518",
                    "reason": "Added niche provider with quantum-resistant encryption capability",
                },
                {
                    "action": "remove",
                    "timestamp": (now - timedelta(days=3)).isoformat(),
                    "actor": "business.collaborator@telekom.de",
                    "supplier_id": "SUP-0307",
                    "reason": "Removed due to overlapping capability with SUP-0412",
                },
                {
                    "action": "lock",
                    "timestamp": (now - timedelta(days=2)).isoformat(),
                    "actor": "longlist.finalization@telekom.de",
                    "supplier_ids": ["SUP-0231", "SUP-0118", "SUP-0045", "SUP-0518", "SUP-0412"],
                    "validation_verdict": "pass",
                },
            ]),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=2),
        )
        session.add(longlist_8)

        # TASK-8 seed: Tender dispatches for LL-2024-0402
        batch_id_8 = "DSP-2024-0402-01"
        dispatches_8 = [
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_8_id,
                dispatch_batch_id=batch_id_8,
                supplier_id="SUP-0231",
                supplier_contact="tenders@sup0231.example.com",
                dispatch_status="delivered",
                retry_count=0,
                delivery_confirmation_ref="CONF-0402-001",
                error_detail=None,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(days=1),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_8_id,
                dispatch_batch_id=batch_id_8,
                supplier_id="SUP-0118",
                supplier_contact="rfp@sup0118.example.com",
                dispatch_status="delivered",
                retry_count=0,
                delivery_confirmation_ref="CONF-0402-002",
                error_detail=None,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(days=1),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_8_id,
                dispatch_batch_id=batch_id_8,
                supplier_id="SUP-0045",
                supplier_contact="procurement@sup0045.example.com",
                dispatch_status="delivered",
                retry_count=0,
                delivery_confirmation_ref="CONF-0402-003",
                error_detail=None,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(days=1),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_8_id,
                dispatch_batch_id=batch_id_8,
                supplier_id="SUP-0518",
                supplier_contact="sales@sup0518.example.com",
                dispatch_status="retrying",
                retry_count=2,
                delivery_confirmation_ref=None,
                error_detail="Temporary email server unavailable, retrying",
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(hours=6),
            ),
            TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_8_id,
                dispatch_batch_id=batch_id_8,
                supplier_id="SUP-0412",
                supplier_contact="tenders@sup0412.example.com",
                dispatch_status="escalated",
                retry_count=4,
                delivery_confirmation_ref=None,
                error_detail="Retry exhausted after 4 attempts, escalated to manual intervention",
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(hours=2),
            ),
        ]
        for dispatch in dispatches_8:
            session.add(dispatch)

        # Seed Need 5: Validation failure with too many suppliers (7)
        need_5_id = uuid.UUID("00000000-0000-0000-0000-000000000005")
        need_5 = Need(
            id=need_5_id,
            business_unit_id="BU-CENTRAL-005",
            channel_type="rfp",
            arrival_timestamp=now - timedelta(days=3),
            raw_artifact_ref="s3://intake/rfp-2024-002.pdf",
            normalized_payload_json=json.dumps({"title": "Data Analytics Platform"}),
            status="proposal_reviewed",
            classification_verdict="it_service",
            classification_confidence=0.88,
            correlation_id="CORR-005",
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(hours=12),
        )
        session.add(need_5)

        proposal_5_id = uuid.UUID("00000000-0000-0000-0000-000000000015")
        proposal_5 = LonglistProposal(
            id=proposal_5_id,
            need_id=need_5_id,
            ranked_suppliers=json.dumps([
                "SUP-DATA-001", "SUP-DATA-002", "SUP-DATA-003", "SUP-DATA-004",
                "SUP-DATA-005", "SUP-DATA-006", "SUP-DATA-007"
            ]),
            evidence_limited_flag=False,
            review_status="approved",
            reviewer_notes="7 qualified suppliers identified",
            created_at=now - timedelta(hours=18),
            updated_at=now - timedelta(hours=12),
        )
        session.add(proposal_5)

        # Need 5 validation (fail - too many suppliers)
        validation_5 = SupplierCountValidation(
            id=uuid.uuid4(),
            proposal_id=proposal_5_id,
            supplier_count=7,
            validation_verdict="fail",
            violations=json.dumps(["Supplier count 7 exceeds maximum allowed 6"]),
            triggered_by="ATS9",
            created_at=now - timedelta(hours=12),
            updated_at=now - timedelta(hours=12),
        )
        session.add(validation_5)

        # Sample audit events
        audit_events = [
            AuditEvent(
                id=uuid.uuid4(),
                need_id=need_1_id,
                correlation_id="CORR-001",
                step_code="ATS1",
                agent_code="AGN5",
                tool_code="TOL1",
                actor_type="system",
                actor_id="intake-service",
                outcome="success",
                severity="info",
                payload_ref="Need normalized successfully",
                created_at=now - timedelta(days=10),
            ),
            AuditEvent(
                id=uuid.uuid4(),
                need_id=need_1_id,
                correlation_id="CORR-001",
                step_code="ATS3",
                agent_code="AGN1",
                tool_code=None,
                actor_type="human",
                actor_id="procurement.reviewer@telekom.de",
                outcome="approved",
                severity="info",
                payload_ref="Classification approved: it_service",
                created_at=now - timedelta(days=9),
            ),
            AuditEvent(
                id=uuid.uuid4(),
                need_id=need_1_id,
                correlation_id="CORR-001",
                step_code="ATS11",
                agent_code="AGN3",
                tool_code="TOL4",
                actor_type="human",
                actor_id="longlist.finalization@telekom.de",
                outcome="locked",
                severity="info",
                payload_ref="Longlist locked with 4 suppliers",
                created_at=now - timedelta(days=4),
            ),
            AuditEvent(
                id=uuid.uuid4(),
                need_id=need_2_id,
                correlation_id="CORR-002",
                step_code="ATS4",
                agent_code="AGN1",
                tool_code="TOL5",
                actor_type="system",
                actor_id="vms-handoff-service",
                outcome="success",
                severity="info",
                payload_ref="VMS handoff confirmed: VMS-REF-2024-789",
                created_at=now - timedelta(days=6),
            ),
            AuditEvent(
                id=uuid.uuid4(),
                need_id=need_4_id,
                correlation_id="CORR-004",
                step_code="ATS9",
                agent_code="AGN5",
                tool_code="TOL4",
                actor_type="system",
                actor_id="validation-service",
                outcome="fail",
                severity="warning",
                payload_ref="Count validation failed: 2 suppliers below minimum 3",
                created_at=now - timedelta(days=1),
            ),
        ]
        for event in audit_events:
            session.add(event)

        session.commit()
        print("✓ Seed data loaded successfully")
        print("\nDefault credentials:")
        print("  - procurement.reviewer@telekom.de / Review-pass-1")
        print("  - longlist.finalization@telekom.de / Finalize-pass-1")
        print("  - business.collaborator@telekom.de / Collab-pass-1")

    except Exception as e:
        session.rollback()
        print(f"Error loading seed data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
