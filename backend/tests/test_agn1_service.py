"""Tests for AGN1 Service - Extraction and Classification"""
import json

from app.models.hitl_review import HITLReview
from app.services.agents.agn1_service import AGN1Service


def test_extract_attributes_creates_pending_review(db_session):
    """Test AGN1 extraction creates pending HITL review"""
    agn1 = AGN1Service(db_session)
    
    normalized_fields = {
        "title": "Cloud Infrastructure Modernization",
        "description": "Migrate legacy systems to cloud",
        "business_unit": "IT Operations"
    }
    
    # Execute extraction
    review = agn1.extract_attributes(
        case_id=1,
        normalized_fields=normalized_fields
    )
    
    # Verify review created
    assert review is not None
    assert review.case_id == 1
    assert review.review_type == "extraction"
    assert review.status == "pending"
    assert review.assigned_role == "reviewer"
    assert review.generated_payload is not None
    
    # Verify generated payload structure
    payload = json.loads(review.generated_payload)
    assert "service_category" in payload
    assert "estimated_duration" in payload
    assert "required_skills" in payload
    
    # Verify attribute structure
    assert "value" in payload["service_category"]
    assert "source_excerpt" in payload["service_category"]
    assert "confidence" in payload["service_category"]
    assert "lineage" in payload["service_category"]


def test_extract_attributes_persisted(db_session):
    """Test AGN1 extraction review is persisted to database"""
    agn1 = AGN1Service(db_session)
    
    normalized_fields = {
        "title": "Software Development Project",
        "description": "Build customer portal application"
    }
    
    review = agn1.extract_attributes(1, normalized_fields)
    db_session.commit()
    
    # Query from database
    persisted = db_session.query(HITLReview).filter_by(id=review.id).first()
    
    assert persisted is not None
    assert persisted.case_id == 1
    assert persisted.review_type == "extraction"
    assert persisted.status == "pending"


def test_classify_need_creates_pending_review(db_session):
    """Test AGN1 classification creates pending HITL review"""
    agn1 = AGN1Service(db_session)
    
    confirmed_attributes = {
        "service_category": {"value": "software_development"},
        "estimated_duration": {"value": "6_months"},
        "required_skills": {"value": ["Python", "React", "AWS"]}
    }
    
    # Execute classification
    review = agn1.classify_need(
        case_id=1,
        confirmed_attributes=confirmed_attributes
    )
    
    # Verify review created
    assert review is not None
    assert review.case_id == 1
    assert review.review_type == "classification"
    assert review.status == "pending"
    assert review.assigned_role == "reviewer"
    assert review.generated_payload is not None
    
    # Verify classification payload structure
    payload = json.loads(review.generated_payload)
    assert "ai_verdict" in payload
    assert "confidence_score" in payload
    assert "rationale_inputs" in payload
    assert "reasoning" in payload
    
    # Verify verdict is one of allowed values
    assert payload["ai_verdict"] in ["single_resource", "it_service"]


def test_classify_need_it_service_verdict(db_session):
    """Test classification produces it_service verdict for multi-skill projects"""
    agn1 = AGN1Service(db_session)
    
    # Multiple skills should indicate IT service
    attributes = {
        "service_category": {"value": "software_development"},
        "estimated_duration": {"value": "12_months"},
        "required_skills": {"value": ["Python", "React", "PostgreSQL", "AWS", "Docker"]}
    }
    
    review = agn1.classify_need(1, attributes)
    payload = json.loads(review.generated_payload)
    
    assert payload["ai_verdict"] == "it_service"
    assert payload["confidence_score"] > 0.5


def test_classify_need_single_resource_verdict(db_session):
    """Test classification produces single_resource verdict for simple needs"""
    agn1 = AGN1Service(db_session)
    
    # Single skill should indicate single resource
    attributes = {
        "service_category": {"value": "consulting"},
        "estimated_duration": {"value": "1_month"},
        "required_skills": {"value": ["Excel"]}
    }
    
    review = agn1.classify_need(1, attributes)
    payload = json.loads(review.generated_payload)
    
    assert payload["ai_verdict"] == "single_resource"
    assert "rationale_inputs" in payload


def test_extraction_lineage_metadata(db_session):
    """Test extraction includes lineage metadata for each attribute"""
    agn1 = AGN1Service(db_session)
    
    review = agn1.extract_attributes(1, {"title": "Test", "description": "Test description"})
    payload = json.loads(review.generated_payload)
    
    # Verify all attributes have lineage
    for attr_key, attr_value in payload.items():
        assert "lineage" in attr_value
        assert attr_value["lineage"] in ["ai_generated", "human_corrected", "directly_sourced"]


def test_classification_includes_rationale(db_session):
    """Test classification includes detailed rationale inputs"""
    agn1 = AGN1Service(db_session)
    
    attributes = {
        "estimated_duration": {"value": "6_months"},
        "required_skills": {"value": ["Python", "React"]}
    }
    
    review = agn1.classify_need(1, attributes)
    payload = json.loads(review.generated_payload)
    
    # Verify rationale structure
    assert "rationale_inputs" in payload
    rationale = payload["rationale_inputs"]
    assert "duration_indicator" in rationale
    assert "skills_count" in rationale
    assert rationale["skills_count"] == 2
