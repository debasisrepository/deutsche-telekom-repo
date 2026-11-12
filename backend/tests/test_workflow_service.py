"""Tests for Workflow Orchestrator Service - Extended for Task 4"""
import json

import pytest

from app.models.hitl_review import HITLReview
from app.models.need_case import NeedCase
from app.services.workflow.orchestrator_service import WorkflowOrchestratorService


def test_initialize_workflow_state(db_session, test_user):
    """Test workflow state initialization for existing case"""
    # Create a case first
    orchestrator = WorkflowOrchestratorService(db_session)
    case = orchestrator.create_case_from_intake(
        channel="email",
        raw_content={
            "title": "Test Need",
            "business_unit": "IT",
            "description": "Test description",
            "artifact_type": "email",
            "artifact_ref": "email-001.eml",
            "submitted_via": "email_gateway"
        },
        created_by_user_id=test_user.id
    )
    
    # Initialize workflow state (should return case as-is)
    result = orchestrator.initialize_workflow_state(case.id)
    
    assert result is not None
    assert result.id == case.id
    assert result.workflow_state is not None
    assert result.next_action is not None


def test_advance_to_extraction_creates_review(db_session, test_user):
    """Test advancing case to extraction creates pending HITL review"""
    # Create a case
    orchestrator = WorkflowOrchestratorService(db_session)
    case = orchestrator.create_case_from_intake(
        channel="rfp_document",
        raw_content={
            "title": "Cloud Migration Project",
            "business_unit": "IT Operations",
            "description": "Migrate legacy systems to AWS cloud infrastructure",
            "artifact_type": "rfp_document",
            "artifact_ref": "rfp-001.pdf",
            "submitted_via": "web"
        },
        created_by_user_id=test_user.id
    )
    
    # Advance to extraction
    updated_case = orchestrator.advance_to_extraction(case.id)
    
    # Verify case state
    assert updated_case.workflow_state == "extraction_pending"
    assert updated_case.next_action == "extraction_review_required"
    
    # Verify review created
    reviews = db_session.query(HITLReview).filter_by(
        case_id=case.id,
        review_type="extraction"
    ).all()
    
    assert len(reviews) == 1
    review = reviews[0]
    assert review.status == "pending"
    assert review.generated_payload is not None


def test_advance_to_extraction_workflow_event(db_session, test_user):
    """Test advancing to extraction records workflow event"""
    orchestrator = WorkflowOrchestratorService(db_session)
    case = orchestrator.create_case_from_intake(
        channel="email",
        raw_content={
            "title": "Security Audit",
            "business_unit": "Security",
            "description": "Comprehensive security assessment",
            "artifact_type": "email",
            "artifact_ref": "email-002.eml",
            "submitted_via": "email_gateway"
        },
        created_by_user_id=test_user.id
    )
    
    original_state = case.workflow_state
    
    # Advance to extraction
    orchestrator.advance_to_extraction(case.id, actor_id="test_system")
    
    # Verify workflow event recorded
    from app.models.workflow_event import WorkflowEvent
    events = db_session.query(WorkflowEvent).filter_by(
        case_id=case.id,
        event_type="extraction_initiated"
    ).all()
    
    assert len(events) == 1
    event = events[0]
    assert event.from_state == original_state
    assert event.to_state == "extraction_pending"
    assert event.actor_type == "system"
    assert event.actor_id == "test_system"


def test_advance_to_extraction_missing_case(db_session):
    """Test advancing nonexistent case to extraction raises error"""
    orchestrator = WorkflowOrchestratorService(db_session)
    
    with pytest.raises(ValueError, match="Case 99999 not found"):
        orchestrator.advance_to_extraction(99999)


def test_advance_to_extraction_missing_normalized_need(db_session, test_user):
    """Test advancing case without normalized need raises error"""
    # Create case without going through orchestrator
    case = NeedCase(
        case_number="CASE-2026-99999",
        inbound_channel="email",
        workflow_state="intake_normalized",
        next_action="pending",
        created_by=test_user.id
    )
    db_session.add(case)
    db_session.commit()
    
    orchestrator = WorkflowOrchestratorService(db_session)
    
    with pytest.raises(ValueError, match="No normalized need found"):
        orchestrator.advance_to_extraction(case.id)


def test_advance_to_extraction_uses_normalized_fields(db_session, test_user):
    """Test extraction uses all normalized fields (mandatory, sourced, derived)"""
    orchestrator = WorkflowOrchestratorService(db_session)
    case = orchestrator.create_case_from_intake(
        channel="rfp_document",
        raw_content={
            "title": "Application Development",
            "business_unit": "Product",
            "description": "Full-stack web application",
            "artifact_type": "rfp_document",
            "artifact_ref": "rfp-003.pdf",
            "submitted_via": "web"
        },
        created_by_user_id=test_user.id
    )
    
    orchestrator.advance_to_extraction(case.id)
    
    # Verify extraction review contains attributes
    review = db_session.query(HITLReview).filter_by(
        case_id=case.id,
        review_type="extraction"
    ).first()
    
    assert review is not None
    payload = json.loads(review.generated_payload)
    
    # Verify extraction produced structured attributes
    assert "service_category" in payload
    assert "estimated_duration" in payload
    assert "required_skills" in payload


def test_case_workflow_states_progression(db_session, test_user):
    """Test complete workflow state progression from intake to extraction"""
    orchestrator = WorkflowOrchestratorService(db_session)
    
    # Step 1: Create case (intake_normalized)
    case = orchestrator.create_case_from_intake(
        channel="email",
        raw_content={
            "title": "Database Services",
            "business_unit": "IT",
            "description": "Oracle DBA support",
            "artifact_type": "email",
            "artifact_ref": "email-003.eml",
            "submitted_via": "email_gateway"
        },
        created_by_user_id=test_user.id
    )
    
    assert case.workflow_state == "intake_normalized"
    
    # Step 2: Advance to extraction
    updated = orchestrator.advance_to_extraction(case.id)
    
    assert updated.workflow_state == "extraction_pending"
    assert updated.next_action == "extraction_review_required"
    
    # Verify review exists
    review = db_session.query(HITLReview).filter_by(case_id=case.id).first()
    assert review.status == "pending"
