"""Integration tests for VMS handoff endpoint and classification verdict"""
import json

from app.models.classification_result import ClassificationResult
from app.models.hitl_review import HITLReview
from app.models.need_case import NeedCase
from app.models.vms_handoff import VMSHandoff
from app.services.agents.agn1_service import AGN1Service
from app.services.workflow.orchestrator_service import WorkflowOrchestratorService


def test_classification_verdict_generation(db_session):
    """Test AGN1 generates classification verdict with confidence and rationale."""
    # Create test case
    case = NeedCase(
        case_number="CASE-2026-00999",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=1
    )
    db_session.add(case)
    db_session.commit()
    
    # Confirmed attributes from extraction review
    confirmed_attributes = {
        "service_category": {
            "value": "software_development",
            "confidence": 0.85
        },
        "estimated_duration": {
            "value": "6_months",
            "confidence": 0.70
        },
        "required_skills": {
            "value": ["Python", "FastAPI", "React"],
            "confidence": 0.90
        }
    }
    
    # Execute AGN1 classification
    agn1_service = AGN1Service(db_session)
    review = agn1_service.classify_need(case.id, confirmed_attributes)
    
    # Verify classification review created
    assert review.case_id == case.id
    assert review.review_type == "classification"
    assert review.status == "pending"
    
    # Verify classification verdict in generated_payload
    generated_payload = json.loads(review.generated_payload)
    assert "ai_verdict" in generated_payload
    assert generated_payload["ai_verdict"] in ["single_resource", "it_service"]
    assert "confidence_score" in generated_payload
    assert "rationale_inputs" in generated_payload
    assert isinstance(generated_payload["confidence_score"], float)


def test_classification_verdict_linked_to_attributes(db_session):
    """Test classification verdict is linked to structured attribute set."""
    # Create test case
    case = NeedCase(
        case_number="CASE-2026-01000",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=1
    )
    db_session.add(case)
    db_session.commit()
    
    # Single-resource attributes (simple, one skill)
    single_resource_attributes = {
        "service_category": {
            "value": "consulting",
            "confidence": 0.90
        },
        "estimated_duration": {
            "value": "1_month",
            "confidence": 0.85
        },
        "required_skills": {
            "value": ["Java"],  # Single skill
            "confidence": 0.95
        }
    }
    
    # Execute classification
    agn1_service = AGN1Service(db_session)
    review = agn1_service.classify_need(case.id, single_resource_attributes)
    
    # Verify verdict
    generated_payload = json.loads(review.generated_payload)
    assert generated_payload["ai_verdict"] == "single_resource"
    
    # Verify rationale includes attribute references
    rationale = generated_payload["rationale_inputs"]
    assert "skills_count" in rationale
    assert rationale["skills_count"] == 1


def test_classification_confidence_metadata_stored(db_session):
    """Test classification result stores confidence metadata."""
    # Create test case with classification
    case = NeedCase(
        case_number="CASE-2026-01001",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="vms_routing",
        final_classification="single_resource",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification result with confidence metadata
    classification_result = ClassificationResult(
        case_id=case.id,
        ai_verdict="single_resource",
        confirmed_verdict="single_resource",
        confidence_score=0.88,
        rationale_inputs=json.dumps({
            "duration_indicator": "1_month",
            "skills_count": 1,
            "complexity_score": 0.25
        }),
        overridden=False
    )
    db_session.add(classification_result)
    db_session.commit()
    
    # Verify classification result persisted
    result = db_session.query(ClassificationResult).filter_by(case_id=case.id).first()
    assert result is not None
    assert result.confidence_score == 0.88
    assert result.ai_verdict == "single_resource"
    assert result.confirmed_verdict == "single_resource"
    
    # Verify rationale inputs
    rationale = json.loads(result.rationale_inputs)
    assert "duration_indicator" in rationale
    assert "skills_count" in rationale


def test_classification_rationale_viewable(db_session):
    """Test users can view classification rationale inputs."""
    # Create case with pending classification review
    case = NeedCase(
        case_number="CASE-2026-01002",
        inbound_channel="email",
        workflow_state="classification_pending",
        next_action="classification_review",
        created_by=1
    )
    db_session.add(case)
    db_session.commit()
    
    # Create classification review with rationale
    review = HITLReview(
        case_id=case.id,
        review_type="classification",
        status="pending",
        assigned_role="reviewer",
        generated_payload=json.dumps({
            "ai_verdict": "it_service",
            "confidence_score": 0.92,
            "rationale_inputs": {
                "duration_indicator": "6_months",
                "skills_count": 3,
                "complexity_score": 0.75
            },
            "reasoning": "Classified as it_service based on duration and multiple skill requirements"
        })
    )
    db_session.add(review)
    db_session.commit()
    
    # Verify rationale is accessible
    retrieved_review = db_session.query(HITLReview).filter_by(
        case_id=case.id,
        review_type="classification"
    ).first()
    
    assert retrieved_review is not None
    payload = json.loads(retrieved_review.generated_payload)
    assert "rationale_inputs" in payload
    assert "reasoning" in payload
    assert payload["reasoning"] != ""


def test_vms_handoff_for_single_resource_case(db_session):
    """Test VMS handoff triggered for single-resource case."""
    # Create single-resource case
    case = NeedCase(
        case_number="CASE-2026-01003",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="vms_routing",
        final_classification="single_resource",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification result
    classification_result = ClassificationResult(
        case_id=case.id,
        ai_verdict="single_resource",
        confirmed_verdict="single_resource",
        confidence_score=0.90,
        rationale_inputs=json.dumps({"skills_count": 1}),
        overridden=False
    )
    db_session.add(classification_result)
    
    # Create extraction review with confirmed attributes
    extraction_review = HITLReview(
        case_id=case.id,
        review_type="extraction",
        status="approved",
        decision="approve",
        reviewer_id=1,
        generated_payload=json.dumps({"service_category": {"value": "consulting"}}),
        final_payload=json.dumps({"service_category": {"value": "consulting"}})
    )
    db_session.add(extraction_review)
    db_session.commit()
    
    # Trigger VMS handoff
    orchestrator = WorkflowOrchestratorService(db_session)
    updated_case = orchestrator.route_single_resource_case(
        case_id=case.id,
        reviewer_id=1
    )
    
    # Verify VMS handoff created
    vms_handoff = db_session.query(VMSHandoff).filter_by(case_id=case.id).first()
    assert vms_handoff is not None
    assert vms_handoff.vms_reference_id.startswith("VMS-")
    assert vms_handoff.handoff_status == "success"
    
    # Verify workflow state updated
    assert updated_case.workflow_state == "routed_to_vms"


def test_supplier_selection_workflow_terminated_after_vms_handoff(db_session):
    """Test supplier-selection workflow terminated after VMS handoff."""
    # Create single-resource case
    case = NeedCase(
        case_number="CASE-2026-01004",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="vms_routing",
        final_classification="single_resource",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create classification result
    classification_result = ClassificationResult(
        case_id=case.id,
        ai_verdict="single_resource",
        confirmed_verdict="single_resource",
        confidence_score=0.88,
        rationale_inputs=json.dumps({}),
        overridden=False
    )
    db_session.add(classification_result)
    
    # Create extraction review
    extraction_review = HITLReview(
        case_id=case.id,
        review_type="extraction",
        status="approved",
        decision="approve",
        reviewer_id=1,
        generated_payload=json.dumps({}),
        final_payload=json.dumps({})
    )
    db_session.add(extraction_review)
    db_session.commit()
    
    # Route to VMS
    orchestrator = WorkflowOrchestratorService(db_session)
    updated_case = orchestrator.route_single_resource_case(case.id, reviewer_id=1)
    
    # Verify workflow terminated (not in any IT-service workflow state)
    assert updated_case.workflow_state == "routed_to_vms"
    assert updated_case.next_action == "vms_processing"


def test_case_retains_vms_reference(db_session):
    """Test case retains reference to external VMS routing outcome."""
    # Create and route case
    case = NeedCase(
        case_number="CASE-2026-01005",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="vms_routing",
        final_classification="single_resource",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create required dependencies
    classification_result = ClassificationResult(
        case_id=case.id,
        ai_verdict="single_resource",
        confirmed_verdict="single_resource",
        confidence_score=0.85,
        rationale_inputs=json.dumps({}),
        overridden=False
    )
    db_session.add(classification_result)
    
    extraction_review = HITLReview(
        case_id=case.id,
        review_type="extraction",
        status="approved",
        decision="approve",
        reviewer_id=1,
        generated_payload=json.dumps({}),
        final_payload=json.dumps({})
    )
    db_session.add(extraction_review)
    db_session.commit()
    
    # Route to VMS
    orchestrator = WorkflowOrchestratorService(db_session)
    orchestrator.route_single_resource_case(case.id, reviewer_id=1)
    
    # Verify VMS reference retained
    vms_handoff = db_session.query(VMSHandoff).filter_by(case_id=case.id).first()
    assert vms_handoff is not None
    
    # Can retrieve VMS reference via case relationship
    db_session.refresh(case)
    retrieved_handoff = db_session.query(VMSHandoff).filter_by(case_id=case.id).first()
    assert retrieved_handoff.vms_reference_id == vms_handoff.vms_reference_id


def test_routed_cases_distinguishable_in_work_queues(db_session):
    """Test routed-out cases distinguishable from IT-service cases."""
    # Create IT-service case
    it_service_case = NeedCase(
        case_number="CASE-2026-01006",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="evidence_retrieval",
        final_classification="it_service",
        created_by=1
    )
    db_session.add(it_service_case)
    
    # Create routed-out case
    routed_case = NeedCase(
        case_number="CASE-2026-01007",
        inbound_channel="email",
        workflow_state="routed_to_vms",
        next_action="vms_processing",
        final_classification="single_resource",
        created_by=1
    )
    db_session.add(routed_case)
    db_session.commit()
    
    # Query IT-service cases (should not include routed cases)
    it_service_cases = db_session.query(NeedCase).filter(
        NeedCase.final_classification == "it_service"
    ).all()
    
    assert len(it_service_cases) == 1
    assert it_service_cases[0].case_number == "CASE-2026-01006"
    
    # Query routed cases
    routed_cases = db_session.query(NeedCase).filter(
        NeedCase.workflow_state == "routed_to_vms"
    ).all()
    
    assert len(routed_cases) == 1
    assert routed_cases[0].case_number == "CASE-2026-01007"
