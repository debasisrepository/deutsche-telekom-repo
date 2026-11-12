"""Idempotent seed data for local development."""
import json
import sys
from datetime import date

import bcrypt
from sqlalchemy.orm import Session

from app.database import engine
from app.models.case_evidence import CaseEvidence
from app.models.case_mapping import CaseMapping
from app.models.classification_result import ClassificationResult
from app.models.commissioned_sow import CommissionedSoW
from app.models.functional_group import FunctionalGroup
from app.models.historical_order import HistoricalOrder
from app.models.hitl_review import HITLReview
from app.models.longlist_proposal import LonglistProposal
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.panel import Panel
from app.models.policy_validation import PolicyValidation
from app.models.proposal_supplier import ProposalSupplier
from app.models.source_artifact import SourceArtifact
from app.models.supplier import Supplier
from app.models.supplier_adjustment import SupplierAdjustment
from app.models.user import User
from app.models.vms_handoff import VMSHandoff


def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def seed_users(session: Session) -> None:
    """Seed default users for development."""
    users_data = [
        ("admin@example.com", "admin", "admin123", "admin"),
        ("reviewer@example.com", "reviewer", "reviewer123", "reviewer"),
        ("manager@example.com", "manager", "manager123", "manager"),
    ]
    
    for email, username, password, role in users_data:
        existing = session.query(User).filter_by(email=email).first()
        if not existing:
            user = User(
                email=email,
                username=username,
                hashed_password=hash_password(password),
                role=role,
                is_active=True
            )
            session.add(user)
            print(f"Created user: {email}")
        else:
            print(f"User already exists: {email}")


def seed_cases(session: Session) -> None:
    """Seed sample cases with intake-normalized state."""
    # Get admin user for created_by
    admin = session.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        print("Warning: Admin user not found, skipping case seeding")
        return
    
    # Check if sample cases already exist
    existing_case = session.query(NeedCase).filter_by(case_number="CASE-2026-00001").first()
    if existing_case:
        print("Sample cases already exist")
        return
    
    # Sample case 1: RFP document intake - normalized
    case1 = NeedCase(
        case_number="CASE-2026-00001",
        inbound_channel="rfp_document",
        workflow_state="intake_normalized",
        next_action="Review extracted attributes",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001"
    )
    session.add(case1)
    session.flush()
    
    normalized1 = NormalizedNeed(
        case_id=case1.id,
        mandatory_fields=json.dumps({
            "need_title": "Cloud Infrastructure Modernization",
            "business_unit": "IT Operations",
            "need_description": "Migrate legacy systems to cloud infrastructure"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "rfp-2026-001.pdf",
            "source_channel_metadata": {
                "channel": "rfp_document",
                "submitted_via": "web"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized1)
    
    artifact1 = SourceArtifact(
        case_id=case1.id,
        artifact_type="rfp_document",
        storage_ref="rfp-2026-001.pdf",
        source_channel="rfp_document",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact1)
    
    # Sample case 2: Email intake - normalized
    case2 = NeedCase(
        case_number="CASE-2026-00002",
        inbound_channel="email",
        workflow_state="intake_normalized",
        next_action="Review extracted attributes",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001"
    )
    session.add(case2)
    session.flush()
    
    normalized2 = NormalizedNeed(
        case_id=case2.id,
        mandatory_fields=json.dumps({
            "need_title": "Network Security Assessment",
            "business_unit": "Security",
            "need_description": "Comprehensive security audit of network infrastructure"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "email-2026-002.eml",
            "source_channel_metadata": {
                "channel": "email",
                "submitted_via": "email_gateway"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized2)
    
    artifact2 = SourceArtifact(
        case_id=case2.id,
        artifact_type="email",
        storage_ref="email-2026-002.eml",
        source_channel="email",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact2)
    
    # Sample case 3: Phone note - pending (incomplete)
    case3 = NeedCase(
        case_number="CASE-2026-00003",
        inbound_channel="phone_note",
        workflow_state="intake_pending",
        next_action="Complete missing mandatory fields",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001"
    )
    session.add(case3)
    session.flush()
    
    normalized3 = NormalizedNeed(
        case_id=case3.id,
        mandatory_fields=json.dumps({
            "need_title": "Software License Management",
            "business_unit": "",
            "need_description": ""
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "phone-note-2026-003.txt",
            "source_channel_metadata": {
                "channel": "phone_note",
                "submitted_via": "phone"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=0.33,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized3)
    
    artifact3 = SourceArtifact(
        case_id=case3.id,
        artifact_type="phone_note",
        storage_ref="phone-note-2026-003.txt",
        source_channel="phone_note",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact3)
    
    # Sample case 4: Extraction pending with review
    case4 = NeedCase(
        case_number="CASE-2026-00004",
        inbound_channel="rfp_document",
        workflow_state="extraction_pending",
        next_action="extraction_review_required",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001,REQ-DOMAIN-002"
    )
    session.add(case4)
    session.flush()
    
    normalized4 = NormalizedNeed(
        case_id=case4.id,
        mandatory_fields=json.dumps({
            "need_title": "Application Development Services",
            "business_unit": "Product Development",
            "need_description": "Full-stack application development for customer portal"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "rfp-2026-004.pdf",
            "source_channel_metadata": {
                "channel": "rfp_document",
                "submitted_via": "web"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized4)
    
    artifact4 = SourceArtifact(
        case_id=case4.id,
        artifact_type="rfp_document",
        storage_ref="rfp-2026-004.pdf",
        source_channel="rfp_document",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact4)
    
    # Create pending extraction review
    review4 = HITLReview(
        case_id=case4.id,
        review_type="extraction",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps({
            "service_category": {
                "value": "software_development",
                "source_excerpt": "Inferred from title: 'Application Development Services'",
                "confidence": 0.90,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "12_months",
                "source_excerpt": "Derived from project scope",
                "confidence": 0.75,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Python", "React", "PostgreSQL", "AWS"],
                "source_excerpt": "Extracted from technical requirements",
                "confidence": 0.95,
                "lineage": "directly_sourced"
            }
        }),
        requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
    )
    session.add(review4)
    
    # Sample case 5: Extraction review (approved, classification pending)
    case5 = NeedCase(
        case_number="CASE-2026-00005",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001,REQ-DOMAIN-002"
    )
    session.add(case5)
    session.flush()
    
    normalized5 = NormalizedNeed(
        case_id=case5.id,
        mandatory_fields=json.dumps({
            "need_title": "Database Administrator",
            "business_unit": "IT Operations",
            "need_description": "Senior DBA for Oracle database management"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "email-2026-005.eml",
            "source_channel_metadata": {
                "channel": "email",
                "submitted_via": "email_gateway"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized5)
    
    artifact5 = SourceArtifact(
        case_id=case5.id,
        artifact_type="email",
        storage_ref="email-2026-005.eml",
        source_channel="email",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact5)
    
    # Create approved extraction review for case 5
    reviewer = session.query(User).filter_by(email="reviewer@example.com").first()
    review5 = HITLReview(
        case_id=case5.id,
        review_type="extraction",
        status="approved",
        assigned_role="reviewer",
        decision="approve",
        reviewer_id=reviewer.id if reviewer else None,
        generated_payload=json.dumps({
            "service_category": {
                "value": "database_administration",
                "source_excerpt": "Inferred from title: 'Database Administrator'",
                "confidence": 0.92,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "3_months",
                "source_excerpt": "Standard contract duration",
                "confidence": 0.70,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Oracle", "SQL", "Performance Tuning"],
                "source_excerpt": "Extracted from requirements",
                "confidence": 0.88,
                "lineage": "directly_sourced"
            }
        }),
        final_payload=json.dumps({
            "service_category": {
                "value": "database_administration",
                "source_excerpt": "Inferred from title: 'Database Administrator'",
                "confidence": 0.92,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "3_months",
                "source_excerpt": "Standard contract duration",
                "confidence": 0.70,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Oracle", "SQL", "Performance Tuning"],
                "source_excerpt": "Extracted from requirements",
                "confidence": 0.88,
                "lineage": "directly_sourced"
            }
        }),
        requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
    )
    session.add(review5)
    
    # Sample case 6: Classification pending review
    case6 = NeedCase(
        case_number="CASE-2026-00006",
        inbound_channel="rfp_document",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001,REQ-DOMAIN-004"
    )
    session.add(case6)
    session.flush()
    
    normalized6 = NormalizedNeed(
        case_id=case6.id,
        mandatory_fields=json.dumps({
            "need_title": "Enterprise Software Development Project",
            "business_unit": "Digital Transformation",
            "need_description": "Multi-year enterprise application development initiative"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "rfp-2026-006.pdf",
            "source_channel_metadata": {
                "channel": "rfp_document",
                "submitted_via": "web"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized6)
    
    artifact6 = SourceArtifact(
        case_id=case6.id,
        artifact_type="rfp_document",
        storage_ref="rfp-2026-006.pdf",
        source_channel="rfp_document",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact6)
    
    # Create approved extraction review for case 6
    review6_extraction = HITLReview(
        case_id=case6.id,
        review_type="extraction",
        status="approved",
        assigned_role="reviewer",
        decision="approve",
        reviewer_id=reviewer.id if reviewer else None,
        generated_payload=json.dumps({
            "service_category": {
                "value": "software_development",
                "source_excerpt": "Inferred from title",
                "confidence": 0.95,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "24_months",
                "source_excerpt": "Multi-year initiative",
                "confidence": 0.88,
                "lineage": "directly_sourced"
            },
            "required_skills": {
                "value": ["Java", "Spring", "React", "Kubernetes", "PostgreSQL"],
                "source_excerpt": "Technical requirements",
                "confidence": 0.92,
                "lineage": "directly_sourced"
            }
        }),
        final_payload=json.dumps({
            "service_category": {
                "value": "software_development",
                "source_excerpt": "Inferred from title",
                "confidence": 0.95,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "24_months",
                "source_excerpt": "Multi-year initiative",
                "confidence": 0.88,
                "lineage": "directly_sourced"
            },
            "required_skills": {
                "value": ["Java", "Spring", "React", "Kubernetes", "PostgreSQL"],
                "source_excerpt": "Technical requirements",
                "confidence": 0.92,
                "lineage": "directly_sourced"
            }
        }),
        requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
    )
    session.add(review6_extraction)
    
    # Create pending classification review for case 6
    review6_classification = HITLReview(
        case_id=case6.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps({
            "ai_verdict": "it_service",
            "confidence_score": 0.94,
            "rationale_inputs": {
                "duration_indicator": "24_months",
                "skills_count": 5,
                "complexity_score": 0.90
            },
            "reasoning": "Classified as it_service based on duration (24_months) and skill requirements (5 skills)"
        }),
        requirement_tags="REQ-DOMAIN-004,REQ-DOMAIN-005"
    )
    session.add(review6_classification)
    
    # Sample case 7: Single-resource case with AI-generated classification (pending review)
    case7 = NeedCase(
        case_number="CASE-2026-00007",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001,REQ-DOMAIN-004"
    )
    session.add(case7)
    session.flush()
    
    normalized7 = NormalizedNeed(
        case_id=case7.id,
        mandatory_fields=json.dumps({
            "need_title": "Senior Java Developer",
            "business_unit": "Application Services",
            "need_description": "Contract developer for maintenance work"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "email-2026-007.eml",
            "source_channel_metadata": {
                "channel": "email",
                "submitted_via": "email_gateway"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized7)
    
    artifact7 = SourceArtifact(
        case_id=case7.id,
        artifact_type="email",
        storage_ref="email-2026-007.eml",
        source_channel="email",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact7)
    
    # Approved extraction review for case 7
    review7_extraction = HITLReview(
        case_id=case7.id,
        review_type="extraction",
        status="approved",
        assigned_role="reviewer",
        decision="approve",
        reviewer_id=reviewer.id if reviewer else None,
        generated_payload=json.dumps({
            "service_category": {
                "value": "software_development",
                "confidence": 0.88,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "6_months",
                "confidence": 0.75,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Java"],
                "confidence": 0.90,
                "lineage": "directly_sourced"
            }
        }),
        final_payload=json.dumps({
            "service_category": {
                "value": "software_development",
                "confidence": 0.88,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "6_months",
                "confidence": 0.75,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Java"],
                "confidence": 0.90,
                "lineage": "directly_sourced"
            }
        }),
        requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
    )
    session.add(review7_extraction)
    
    # Pending classification review for case 7 (single_resource verdict)
    review7_classification = HITLReview(
        case_id=case7.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps({
            "ai_verdict": "single_resource",
            "confidence_score": 0.85,
            "rationale_inputs": {
                "duration_indicator": "6_months",
                "skills_count": 1,
                "complexity_score": 0.30
            },
            "reasoning": "Classified as single_resource based on single skill requirement"
        }),
        requirement_tags="REQ-DOMAIN-004,REQ-DOMAIN-005"
    )
    session.add(review7_classification)
    
    # Sample case 8: Confirmed single_resource with VMS handoff
    case8 = NeedCase(
        case_number="CASE-2026-00008",
        inbound_channel="phone_note",
        workflow_state="routed_to_vms",
        next_action="vms_processing",
        final_classification="single_resource",
        created_by=admin.id,
        requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001,REQ-INT-001"
    )
    session.add(case8)
    session.flush()
    
    normalized8 = NormalizedNeed(
        case_id=case8.id,
        mandatory_fields=json.dumps({
            "need_title": "Network Technician",
            "business_unit": "IT Infrastructure",
            "need_description": "Short-term network support contractor"
        }),
        sourced_fields=json.dumps({
            "source_artifact_ref": "phone-note-2026-008.txt",
            "source_channel_metadata": {
                "channel": "phone_note",
                "submitted_via": "phone"
            }
        }),
        derived_fields=json.dumps({}),
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    session.add(normalized8)
    
    artifact8 = SourceArtifact(
        case_id=case8.id,
        artifact_type="phone_note",
        storage_ref="phone-note-2026-008.txt",
        source_channel="phone_note",
        requirement_tags="REQ-DATA-001"
    )
    session.add(artifact8)
    
    # Approved extraction review for case 8
    review8_extraction = HITLReview(
        case_id=case8.id,
        review_type="extraction",
        status="approved",
        assigned_role="reviewer",
        decision="approve",
        reviewer_id=reviewer.id if reviewer else None,
        generated_payload=json.dumps({
            "service_category": {
                "value": "network_support",
                "confidence": 0.92,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "3_months",
                "confidence": 0.80,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Networking"],
                "confidence": 0.95,
                "lineage": "directly_sourced"
            }
        }),
        final_payload=json.dumps({
            "service_category": {
                "value": "network_support",
                "confidence": 0.92,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "3_months",
                "confidence": 0.80,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Networking"],
                "confidence": 0.95,
                "lineage": "directly_sourced"
            }
        }),
        requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
    )
    session.add(review8_extraction)
    
    # Approved classification review for case 8
    review8_classification = HITLReview(
        case_id=case8.id,
        review_type="classification",
        status="approved",
        assigned_role="reviewer",
        decision="confirm",
        reviewer_id=reviewer.id if reviewer else None,
        generated_payload=json.dumps({
            "ai_verdict": "single_resource",
            "confidence_score": 0.90,
            "rationale_inputs": {
                "duration_indicator": "3_months",
                "skills_count": 1,
                "complexity_score": 0.25
            },
            "reasoning": "Classified as single_resource - short-term, single skill requirement"
        }),
        final_payload=json.dumps({
            "ai_verdict": "single_resource",
            "confirmed_verdict": "single_resource",
            "overridden": False
        }),
        requirement_tags="REQ-DOMAIN-004,REQ-DOMAIN-005"
    )
    session.add(review8_classification)
    
    # Classification result for case 8
    classification8 = ClassificationResult(
        case_id=case8.id,
        ai_verdict="single_resource",
        confirmed_verdict="single_resource",
        confidence_score=0.90,
        rationale_inputs=json.dumps({
            "duration_indicator": "3_months",
            "skills_count": 1,
            "complexity_score": 0.25
        }),
        overridden=False,
        requirement_tags="REQ-DOMAIN-004,REQ-DOMAIN-005"
    )
    session.add(classification8)
    
    # VMS handoff record for case 8
    vms_handoff8 = VMSHandoff(
        case_id=case8.id,
        vms_reference_id="VMS-2026-000008",
        handoff_status="success",
        request_snapshot=json.dumps({
            "case_id": case8.id,
            "case_number": "CASE-2026-00008",
            "classification": "single_resource",
            "attributes": {
                "service_category": {"value": "network_support"},
                "estimated_duration": {"value": "3_months"},
                "required_skills": {"value": ["Networking"]}
            }
        }),
        requirement_tags="REQ-INT-001"
    )
    session.add(vms_handoff8)
    
    print("Created 8 sample cases including AI-generated classification verdicts and VMS handoff")


def seed_evidence(session: Session) -> None:
    """Seed suppliers, historical evidence, and case-evidence links."""
    # Check if suppliers already exist
    existing_supplier = session.query(Supplier).filter_by(supplier_code="SUP-CLOUD-001").first()
    if existing_supplier:
        print("Suppliers and evidence already exist")
        return
    
    # Create suppliers
    supplier1 = Supplier(
        supplier_code="SUP-CLOUD-001",
        display_name="CloudTech Solutions GmbH",
        status="active",
        contact_endpoint="procurement@cloudtech.de",
        evidence_source_status="available",
        requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
    )
    session.add(supplier1)
    
    supplier2 = Supplier(
        supplier_code="SUP-SEC-002",
        display_name="SecureNet Services AG",
        status="active",
        contact_endpoint="contracts@securenet.de",
        evidence_source_status="available",
        requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
    )
    session.add(supplier2)
    
    supplier3 = Supplier(
        supplier_code="SUP-APP-003",
        display_name="AppDev Partners GmbH",
        status="active",
        contact_endpoint="sales@appdevpartners.de",
        evidence_source_status="available",
        requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
    )
    session.add(supplier3)
    
    session.flush()
    
    # Create historical orders
    order1 = HistoricalOrder(
        external_order_id="ORD-2025-1234",
        service_domain="cloud_infrastructure",
        completion_date=date(2025, 9, 15),
        requirement_tags="REQ-INT-002"
    )
    session.add(order1)
    
    order2 = HistoricalOrder(
        external_order_id="ORD-2025-9012",
        service_domain="application_development",
        completion_date=date(2025, 6, 30),
        requirement_tags="REQ-INT-002"
    )
    session.add(order2)
    
    session.flush()
    
    # Create commissioned SoWs
    sow1 = CommissionedSoW(
        external_sow_id="SOW-2024-5678",
        scope_summary="Comprehensive security audit with remediation roadmap. Scope included penetration testing and compliance assessment.",
        signed_date=date(2024, 11, 20),
        requirement_tags="REQ-INT-002"
    )
    session.add(sow1)
    
    session.flush()
    
    # Link evidence to case 1 (Cloud Infrastructure Modernization)
    case1 = session.query(NeedCase).filter_by(case_number="CASE-2026-00001").first()
    if case1:
        evidence1 = CaseEvidence(
            case_id=case1.id,
            supplier_id=supplier1.id,
            historical_order_id=order1.id,
            citation_label="Cloud Migration - 2025 Q3",
            citation_ref="order/ORD-2025-1234",
            evidence_summary="Successfully completed cloud infrastructure migration for similar scope in Q3 2025. Delivered on time with 99.9% uptime SLA compliance.",
            evidence_found=True,
            requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
        )
        session.add(evidence1)
    
    # Link evidence to case 2 (Network Security Assessment)
    case2 = session.query(NeedCase).filter_by(case_number="CASE-2026-00002").first()
    if case2:
        evidence2 = CaseEvidence(
            case_id=case2.id,
            supplier_id=supplier2.id,
            commissioned_sow_id=sow1.id,
            citation_label="Network Security Assessment - 2024",
            citation_ref="sow/SOW-2024-5678",
            evidence_summary="Delivered comprehensive security audit with remediation roadmap. Scope included penetration testing and compliance assessment.",
            evidence_found=True,
            requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
        )
        session.add(evidence2)
    
    # Link evidence to case 4 (Application Development Services)
    case4 = session.query(NeedCase).filter_by(case_number="CASE-2026-00004").first()
    if case4:
        evidence3 = CaseEvidence(
            case_id=case4.id,
            supplier_id=supplier3.id,
            historical_order_id=order2.id,
            citation_label="Application Development - 2025 Q2",
            citation_ref="order/ORD-2025-9012",
            evidence_summary="Developed custom enterprise application with agile methodology. Delivered 3 major releases with full documentation.",
            evidence_found=True,
            requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
        )
        session.add(evidence3)
    
    print("Created 3 suppliers, 2 historical orders, 1 commissioned SoW, and 3 case-evidence links")


def seed_mappings_and_proposals(session: Session) -> None:
    """Seed panel mappings, functional groups, and longlist proposals."""
    # Check if panels already exist
    existing_panel = session.query(Panel).filter_by(panel_code="PANEL-CLOUD-001").first()
    if existing_panel:
        print("Panels and mappings already exist")
        return
    
    # Create panels
    panel1 = Panel(
        panel_code="PANEL-CLOUD-001",
        panel_name="Cloud Infrastructure & Platform Services",
        requirement_tags="REQ-INT-003"
    )
    session.add(panel1)
    
    panel2 = Panel(
        panel_code="PANEL-SEC-002",
        panel_name="Security & Risk Management Services",
        requirement_tags="REQ-INT-003"
    )
    session.add(panel2)
    
    panel3 = Panel(
        panel_code="PANEL-APP-003",
        panel_name="Application Development & Integration",
        requirement_tags="REQ-INT-003"
    )
    session.add(panel3)
    session.flush()
    
    # Create functional groups
    fg1 = FunctionalGroup(
        functional_group_code="FG-INFRA-001",
        functional_group_name="Infrastructure Modernization",
        requirement_tags="REQ-INT-003"
    )
    session.add(fg1)
    
    fg2 = FunctionalGroup(
        functional_group_code="FG-SEC-001",
        functional_group_name="Cybersecurity Services",
        requirement_tags="REQ-INT-003"
    )
    session.add(fg2)
    
    fg3 = FunctionalGroup(
        functional_group_code="FG-APP-001",
        functional_group_name="Custom Application Development",
        requirement_tags="REQ-INT-003"
    )
    session.add(fg3)
    session.flush()
    
    # Create case mappings
    case1 = session.query(NeedCase).filter_by(case_number="CASE-2026-00001").first()
    if case1:
        mapping1 = CaseMapping(
            case_id=case1.id,
            panel_id=panel1.id,
            functional_group_id=fg1.id,
            mapping_status="proposed",
            rationale_inputs="Service category 'cloud infrastructure' matches panel specialization",
            requirement_tags="REQ-INT-003"
        )
        session.add(mapping1)
    
    case2 = session.query(NeedCase).filter_by(case_number="CASE-2026-00002").first()
    if case2:
        mapping2 = CaseMapping(
            case_id=case2.id,
            panel_id=panel2.id,
            functional_group_id=fg2.id,
            mapping_status="proposed",
            rationale_inputs="Service category 'security' matches panel specialization",
            requirement_tags="REQ-INT-003"
        )
        session.add(mapping2)
    
    case4 = session.query(NeedCase).filter_by(case_number="CASE-2026-00004").first()
    if case4:
        mapping4 = CaseMapping(
            case_id=case4.id,
            panel_id=panel3.id,
            functional_group_id=fg3.id,
            mapping_status="proposed",
            rationale_inputs="Service category 'software development' matches panel specialization",
            requirement_tags="REQ-INT-003"
        )
        session.add(mapping4)
    session.flush()
    
    # Create longlist proposals with ranked suppliers
    # Proposal for case 1
    if case1:
        proposal1 = LonglistProposal(
            case_id=case1.id,
            version_no=1,
            proposal_status="draft",
            generation_inputs=json.dumps({
                "confirmed_attributes": {"service_category": "cloud_infrastructure"},
                "mapping_info": {"panel": "PANEL-CLOUD-001"},
                "evidence_count": 1,
                "ranking_method": "evidence_quality_based"
            }),
            generated_by_agent_run_id="agn2-run-seed-1",
            requirement_tags="REQ-DOMAIN-006"
        )
        session.add(proposal1)
        session.flush()
        
        # Add ranked suppliers to proposal
        supplier1 = session.query(Supplier).filter_by(supplier_code="SUP-CLOUD-001").first()
        if supplier1:
            ps1 = ProposalSupplier(
                proposal_id=proposal1.id,
                supplier_id=supplier1.id,
                rank_position=1,
                recommendation_status="recommended",
                ranking_score=0.95,
                citation_complete=True,
                requirement_tags="REQ-DOMAIN-006"
            )
            session.add(ps1)
    
    # Proposal for case 2
    if case2:
        proposal2 = LonglistProposal(
            case_id=case2.id,
            version_no=1,
            proposal_status="draft",
            generation_inputs=json.dumps({
                "confirmed_attributes": {"service_category": "security"},
                "mapping_info": {"panel": "PANEL-SEC-002"},
                "evidence_count": 1,
                "ranking_method": "evidence_quality_based"
            }),
            generated_by_agent_run_id="agn2-run-seed-2",
            requirement_tags="REQ-DOMAIN-006"
        )
        session.add(proposal2)
        session.flush()
        
        # Add ranked suppliers to proposal
        supplier2 = session.query(Supplier).filter_by(supplier_code="SUP-SEC-002").first()
        if supplier2:
            ps2 = ProposalSupplier(
                proposal_id=proposal2.id,
                supplier_id=supplier2.id,
                rank_position=1,
                recommendation_status="recommended",
                ranking_score=0.92,
                citation_complete=True,
                requirement_tags="REQ-DOMAIN-006"
            )
            session.add(ps2)
    
    # Proposal for case 4 with multiple ranked suppliers
    if case4:
        proposal4 = LonglistProposal(
            case_id=case4.id,
            version_no=1,
            proposal_status="draft",
            generation_inputs=json.dumps({
                "confirmed_attributes": {"service_category": "software_development"},
                "mapping_info": {"panel": "PANEL-APP-003"},
                "evidence_count": 1,
                "ranking_method": "evidence_quality_based"
            }),
            generated_by_agent_run_id="agn2-run-seed-4",
            requirement_tags="REQ-DOMAIN-006"
        )
        session.add(proposal4)
        session.flush()
        
        # Add ranked suppliers to proposal
        supplier3 = session.query(Supplier).filter_by(supplier_code="SUP-APP-003").first()
        if supplier3:
            ps4_1 = ProposalSupplier(
                proposal_id=proposal4.id,
                supplier_id=supplier3.id,
                rank_position=1,
                recommendation_status="recommended",
                ranking_score=0.90,
                citation_complete=True,
                requirement_tags="REQ-DOMAIN-006"
            )
            session.add(ps4_1)
    
    print("Created 3 panels, 3 functional groups, 3 case mappings, and 3 longlist proposals with ranked suppliers")


def seed_adjustments_and_validations(session: Session) -> None:
    """Seed supplier adjustments and policy validations."""
    # Get cases that have proposals
    case1 = session.query(NeedCase).filter_by(case_number="CASE-2026-00001").first()
    case2 = session.query(NeedCase).filter_by(case_number="CASE-2026-00002").first()
    case4 = session.query(NeedCase).filter_by(case_number="CASE-2026-00004").first()
    
    if not all([case1, case2, case4]):
        print("Warning: Required cases not found for adjustments/validations seeding")
        return
    
    # Type narrowing assertions for mypy
    assert case1 is not None
    assert case2 is not None
    assert case4 is not None
    
    # Check if adjustments already exist
    existing_adjustment = session.query(SupplierAdjustment).filter_by(case_id=case1.id).first()
    if existing_adjustment:
        print("Adjustments and validations already exist")
        return
    
    # Get suppliers
    supplier_cloud1 = session.query(Supplier).filter_by(supplier_code="SUP-CLOUD-001").first()
    supplier_sec2 = session.query(Supplier).filter_by(supplier_code="SUP-SEC-002").first()
    supplier_app3 = session.query(Supplier).filter_by(supplier_code="SUP-APP-003").first()
    
    if not all([supplier_cloud1, supplier_sec2, supplier_app3]):
        print("Warning: Required suppliers not found for adjustments seeding")
        return
    
    # Type narrowing assertions for mypy
    assert supplier_cloud1 is not None
    assert supplier_sec2 is not None
    assert supplier_app3 is not None
    
    # Get admin user for actor_id
    admin = session.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        print("Warning: Admin user not found for adjustments seeding")
        return
    
    # Type narrowing assertion for mypy
    assert admin is not None
    
    # Seed adjustments for case 1 (2 adjustments: remove then add back)
    adjustment1 = SupplierAdjustment(
        case_id=case1.id,
        supplier_id=supplier_cloud1.id,
        change_type="remove",
        rationale="Supplier temporarily suspended due to compliance review",
        actor_id=str(admin.id),
        resulting_supplier_count=1,
        requirement_tags="REQ-DOMAIN-008"
    )
    session.add(adjustment1)
    
    adjustment2 = SupplierAdjustment(
        case_id=case1.id,
        supplier_id=supplier_cloud1.id,
        change_type="add",
        rationale="Compliance review completed, supplier reinstated",
        actor_id=str(admin.id),
        resulting_supplier_count=2,
        requirement_tags="REQ-DOMAIN-008"
    )
    session.add(adjustment2)
    
    # Seed adjustment for case 2 (1 add adjustment)
    adjustment3 = SupplierAdjustment(
        case_id=case2.id,
        supplier_id=supplier_sec2.id,
        change_type="add",
        rationale="Business unit requested additional security specialist",
        actor_id=str(admin.id),
        resulting_supplier_count=2,
        requirement_tags="REQ-DOMAIN-008"
    )
    session.add(adjustment3)
    
    # Seed validations with all three validation results
    # Valid supplier count (case 2: 2 suppliers, within 3-6 range... actually invalid_low!)
    validation1 = PolicyValidation(
        case_id=case2.id,
        validation_type="supplier_count",
        supplier_count=2,
        validation_result="invalid_low",
        rule_snapshot=json.dumps({
            "rule_type": "supplier_count_band",
            "min_suppliers": 3,
            "max_suppliers": 6,
            "applied_count": 2,
            "rule_version": "1.0"
        }),
        requirement_tags="REQ-DOMAIN-009"
    )
    session.add(validation1)
    
    # Let me create a case with valid count (4 suppliers)
    # Get case 1 proposal and check its supplier count
    proposal1 = session.query(LonglistProposal).filter_by(case_id=case1.id).first()
    if proposal1:
        supplier_count1 = session.query(ProposalSupplier).filter_by(proposal_id=proposal1.id).count()
        validation2 = PolicyValidation(
            case_id=case1.id,
            validation_type="supplier_count",
            supplier_count=supplier_count1,
            validation_result="valid" if 3 <= supplier_count1 <= 6 else ("invalid_low" if supplier_count1 < 3 else "invalid_high"),
            rule_snapshot=json.dumps({
                "rule_type": "supplier_count_band",
                "min_suppliers": 3,
                "max_suppliers": 6,
                "applied_count": supplier_count1,
                "rule_version": "1.0"
            }),
            requirement_tags="REQ-DOMAIN-009"
        )
        session.add(validation2)
    
    # Create a case with high supplier count for invalid_high example
    # We need to add more suppliers to case 4 proposal
    proposal4 = session.query(LonglistProposal).filter_by(case_id=case4.id).first()
    if proposal4:
        # For seed purposes, just create a validation with high count
        validation3 = PolicyValidation(
            case_id=case4.id,
            validation_type="supplier_count",
            supplier_count=8,  # Simulated high count
            validation_result="invalid_high",
            rule_snapshot=json.dumps({
                "rule_type": "supplier_count_band",
                "min_suppliers": 3,
                "max_suppliers": 6,
                "applied_count": 8,
                "rule_version": "1.0"
            }),
            requirement_tags="REQ-DOMAIN-009"
        )
        session.add(validation3)
    
    print("Created supplier adjustments and policy validations with all validation results (valid, invalid_low, invalid_high)")


def seed_locked_longlists_and_dispatch(session: Session):
    """Seed locked longlists and tender dispatch records."""
    from app.models.locked_longlist import LockedLonglist
    from app.models.locked_supplier import LockedSupplier
    from app.models.longlist_proposal import LonglistProposal
    from app.models.need_case import NeedCase
    from app.models.proposal_supplier import ProposalSupplier
    from app.models.tender_dispatch import TenderDispatch
    from app.models.tender_dispatch_recipient import TenderDispatchRecipient
    
    # Get cases
    case2 = session.query(NeedCase).filter_by(case_number="CASE-2026-00002").first()
    case4 = session.query(NeedCase).filter_by(case_number="CASE-2026-00004").first()
    
    if not case2 or not case4:
        print("Cases not found for lock/dispatch seeding")
        return
    
    # Create locked longlist for case 2 (locked but not dispatched)
    proposal2 = session.query(LonglistProposal).filter_by(case_id=case2.id).first()
    if proposal2 and not session.query(LockedLonglist).filter_by(case_id=case2.id).first():
        locked_longlist2 = LockedLonglist(
            case_id=case2.id,
            source_proposal_id=proposal2.id,
            lock_status="locked",
            locked_by="1",
            requirement_tags="REQ-DOMAIN-010"
        )
        session.add(locked_longlist2)
        session.flush()
        
        # Create locked suppliers from proposal
        proposal_suppliers2 = session.query(ProposalSupplier).filter_by(proposal_id=proposal2.id).all()
        for ps in proposal_suppliers2:
            locked_supplier = LockedSupplier(
                locked_longlist_id=locked_longlist2.id,
                supplier_id=ps.supplier_id,
                final_rank_position=ps.rank_position,
                requirement_tags="REQ-DOMAIN-010"
            )
            session.add(locked_supplier)
        
        print(f"Created locked longlist for {case2.case_number} with {len(proposal_suppliers2)} locked suppliers")
    
    # Create locked longlist for case 4 (locked and dispatched successfully)
    proposal4 = session.query(LonglistProposal).filter_by(case_id=case4.id).first()
    if proposal4 and not session.query(LockedLonglist).filter_by(case_id=case4.id).first():
        locked_longlist4 = LockedLonglist(
            case_id=case4.id,
            source_proposal_id=proposal4.id,
            lock_status="locked",
            locked_by="1",
            requirement_tags="REQ-DOMAIN-010"
        )
        session.add(locked_longlist4)
        session.flush()
        
        # Create locked suppliers from proposal
        proposal_suppliers4 = session.query(ProposalSupplier).filter_by(proposal_id=proposal4.id).all()
        for ps in proposal_suppliers4:
            locked_supplier = LockedSupplier(
                locked_longlist_id=locked_longlist4.id,
                supplier_id=ps.supplier_id,
                final_rank_position=ps.rank_position,
                requirement_tags="REQ-DOMAIN-010"
            )
            session.add(locked_supplier)
        
        print(f"Created locked longlist for {case4.case_number} with {len(proposal_suppliers4)} locked suppliers")
        
        # Create successful tender dispatch for case 4
        if not session.query(TenderDispatch).filter_by(locked_longlist_id=locked_longlist4.id).first():
            dispatch_batch_ref = f"BATCH-{case4.id}-20261112120000"
            tender_dispatch = TenderDispatch(
                locked_longlist_id=locked_longlist4.id,
                dispatch_batch_ref=dispatch_batch_ref,
                dispatch_status="success",
                dispatched_by="1",
                requirement_tags="REQ-INT-004"
            )
            session.add(tender_dispatch)
            session.flush()
            
            # Create dispatch recipients (all successful)
            locked_suppliers4 = session.query(LockedSupplier).filter_by(
                locked_longlist_id=locked_longlist4.id
            ).all()
            for ls in locked_suppliers4:
                recipient = TenderDispatchRecipient(
                    dispatch_id=tender_dispatch.id,
                    supplier_id=ls.supplier_id,
                    delivery_status="success",
                    external_delivery_ref=f"TENDER-{dispatch_batch_ref}-SUP-{ls.supplier_id}",
                    requirement_tags="REQ-INT-004"
                )
                session.add(recipient)
            
            print(f"Created successful tender dispatch for {case4.case_number} with {len(locked_suppliers4)} recipients")


def main():
    """Run all seed functions."""
    # Import all models to ensure they're registered
    import app.models  # noqa: F401
    
    # Create session
    session = Session(bind=engine)
    
    try:
        seed_users(session)
        seed_cases(session)
        seed_evidence(session)
        seed_mappings_and_proposals(session)
        seed_adjustments_and_validations(session)
        seed_locked_longlists_and_dispatch(session)
        session.commit()
        print("Seed completed successfully")
    except (ValueError, KeyError, TypeError) as e:
        session.rollback()
        print(f"Seed failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == '__main__':
    main()
