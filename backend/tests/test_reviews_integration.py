"""Integration tests for extraction and classification review endpoints"""
import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.classification_result import ClassificationResult
from app.models.hitl_review import HITLReview
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.services.agents.agn1_service import AGN1Service


def test_extraction_review_approve_without_modification(
    auth_client: TestClient, db_session: Session
):
    """Test reviewer can approve extracted attributes without modification"""
    # Create case with extraction pending review
    case = NeedCase(
        case_number="CASE-2026-00101",
        inbound_channel="email",
        workflow_state="extraction_pending",
        next_action="extraction_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create normalized need
    normalized_need = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"title": "Software Development Need"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.8
    )
    db_session.add(normalized_need)
    
    # Create pending extraction review via AGN1
    agn1_service = AGN1Service(db_session)
    review = agn1_service.extract_attributes(
        case.id,
        {"title": "Software Development Need"}
    )
    db_session.commit()
    
    # Apply approve decision
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/extraction",
        json={"decision": "approve", "edited_attributes": None}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["review_type"] == "extraction"
    assert data["status"] == "approved"
    assert data["decision"] == "approve"
    assert data["next_workflow_state"] == "extraction_approved"
    assert data["next_action"] == "classification_pending"
    
    # Verify review record updated
    db_session.refresh(review)
    assert review.status == "approved"
    assert review.decision == "approve"
    assert review.final_payload == review.generated_payload


def test_extraction_review_edit_attributes(
    auth_client: TestClient, db_session: Session
):
    """Test reviewer can edit one or more extracted attributes"""
    # Create case with extraction pending review
    case = NeedCase(
        case_number="CASE-2026-00102",
        inbound_channel="email",
        workflow_state="extraction_pending",
        next_action="extraction_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create normalized need
    normalized_need = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"title": "Consulting Services"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.9
    )
    db_session.add(normalized_need)
    
    # Create pending extraction review
    agn1_service = AGN1Service(db_session)
    review = agn1_service.extract_attributes(
        case.id,
        {"title": "Consulting Services"}
    )
    db_session.commit()
    
    # Apply edit decision with corrected attributes
    edited_attributes = {
        "service_category": {
            "value": "consulting",
            "source_excerpt": "Corrected by reviewer",
            "confidence": 1.0,
            "lineage": "human_corrected"
        }
    }
    
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/extraction",
        json={"decision": "edit", "edited_attributes": edited_attributes}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["decision"] == "edit"
    
    # Verify final_payload contains edited attributes
    db_session.refresh(review)
    assert review.status == "approved"
    assert review.decision == "edit"
    final_payload = json.loads(review.final_payload)
    assert final_payload == edited_attributes
    assert review.final_payload != review.generated_payload


def test_extraction_review_reject(
    auth_client: TestClient, db_session: Session
):
    """Test reviewer can reject extraction result"""
    # Create case with extraction pending review
    case = NeedCase(
        case_number="CASE-2026-00103",
        inbound_channel="email",
        workflow_state="extraction_pending",
        next_action="extraction_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create normalized need
    normalized_need = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"title": "Unclear Request"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.4
    )
    db_session.add(normalized_need)
    
    # Create pending extraction review
    agn1_service = AGN1Service(db_session)
    review = agn1_service.extract_attributes(
        case.id,
        {"title": "Unclear Request"}
    )
    db_session.commit()
    
    # Apply reject decision
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/extraction",
        json={"decision": "reject"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["decision"] == "reject"
    
    # Verify review record updated
    db_session.refresh(review)
    assert review.status == "rejected"
    assert review.decision == "reject"
    assert review.final_payload is None


def test_classification_review_accept_verdict(
    auth_client: TestClient, db_session: Session
):
    """Test reviewer can accept the classification verdict"""
    # Create case with classification pending review
    case = NeedCase(
        case_number="CASE-2026-00104",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification review
    classification_payload = {
        "ai_verdict": "it_service",
        "confidence_score": 0.92,
        "rationale_inputs": {
            "duration_indicator": "6_months",
            "skills_count": 3,
            "complexity_score": 0.85
        }
    }
    
    review = HITLReview(
        case_id=case.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps(classification_payload)
    )
    db_session.add(review)
    db_session.commit()
    
    # Apply confirm decision
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/classification",
        json={"decision": "confirm"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["decision"] == "approve"
    
    # Verify classification_result created
    classification_result = db_session.query(ClassificationResult).filter_by(case_id=case.id).first()
    assert classification_result is not None
    assert classification_result.ai_verdict == "it_service"
    assert classification_result.confirmed_verdict == "it_service"
    assert classification_result.overridden is False
    
    # Verify case final_classification set
    db_session.refresh(case)
    assert case.final_classification == "it_service"


def test_classification_review_override_verdict(
    auth_client: TestClient, db_session: Session
):
    """Test reviewer can override verdict and specify corrected path"""
    # Create case with classification pending review
    case = NeedCase(
        case_number="CASE-2026-00105",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification review with AI verdict
    classification_payload = {
        "ai_verdict": "it_service",
        "confidence_score": 0.75,
        "rationale_inputs": {
            "duration_indicator": "3_months",
            "skills_count": 2
        }
    }
    
    review = HITLReview(
        case_id=case.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps(classification_payload)
    )
    db_session.add(review)
    db_session.commit()
    
    # Apply override decision
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/classification",
        json={"decision": "override", "confirmed_verdict": "single_resource"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["decision"] == "override"
    
    # Verify classification_result records override
    classification_result = db_session.query(ClassificationResult).filter_by(case_id=case.id).first()
    assert classification_result is not None
    assert classification_result.ai_verdict == "it_service"
    assert classification_result.confirmed_verdict == "single_resource"
    assert classification_result.overridden is True
    
    # Verify case final_classification set to overridden verdict
    db_session.refresh(case)
    assert case.final_classification == "single_resource"


def test_classification_controls_downstream_routing(
    auth_client: TestClient, db_session: Session
):
    """Test final confirmed classification controls downstream routing"""
    # Create case with classification pending review
    case = NeedCase(
        case_number="CASE-2026-00106",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification review with single_resource verdict
    classification_payload = {
        "ai_verdict": "single_resource",
        "confidence_score": 0.88,
        "rationale_inputs": {
            "duration_indicator": "1_month",
            "skills_count": 1
        }
    }
    
    review = HITLReview(
        case_id=case.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps(classification_payload)
    )
    db_session.add(review)
    db_session.commit()
    
    # Apply confirm decision
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/classification",
        json={"decision": "confirm"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify routing decision
    db_session.refresh(case)
    assert case.final_classification == "single_resource"
    assert case.next_action == "vms_handoff_pending"
    
    # Verify classification_result exists
    classification_result = db_session.query(ClassificationResult).filter_by(case_id=case.id).first()
    assert classification_result is not None
    assert classification_result.confirmed_verdict == "single_resource"


def test_extraction_review_missing_edited_attributes_for_edit(
    auth_client: TestClient, db_session: Session
):
    """Test edit decision requires edited_attributes"""
    # Create case with pending review
    case = NeedCase(
        case_number="CASE-2026-00107",
        inbound_channel="email",
        workflow_state="extraction_pending",
        next_action="extraction_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create pending review
    review = HITLReview(
        case_id=case.id,
        review_type="extraction",
        status="pending",
        generated_payload=json.dumps({"test": "data"})
    )
    db_session.add(review)
    db_session.commit()
    
    # Try edit without edited_attributes
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/extraction",
        json={"decision": "edit"}
    )
    
    assert response.status_code == 400
    assert "edited_attributes required" in response.json()["detail"]


def test_classification_review_missing_confirmed_verdict_for_override(
    auth_client: TestClient, db_session: Session
):
    """Test override decision requires confirmed_verdict"""
    # Create case with pending review
    case = NeedCase(
        case_number="CASE-2026-00108",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review_required",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create pending review
    review = HITLReview(
        case_id=case.id,
        review_type="classification",
        status="pending",
        generated_payload=json.dumps({"ai_verdict": "it_service", "confidence_score": 0.8})
    )
    db_session.add(review)
    db_session.commit()
    
    # Try override without confirmed_verdict
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/reviews/classification",
        json={"decision": "override"}
    )
    
    assert response.status_code == 400
    assert "confirmed_verdict required" in response.json()["detail"]
