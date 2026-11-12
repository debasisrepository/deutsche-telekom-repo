"""Unit tests for AGN5 deterministic rule engine."""

import pytest

from app.services.rules.agn5_rule_engine import AGN5RuleEngine


@pytest.fixture
def engine():
    return AGN5RuleEngine()


@pytest.fixture
def engine_with_session(db_session):
    return AGN5RuleEngine(session=db_session)


def test_completeness_score_all_filled(engine):
    """Test completeness score with all mandatory fields filled."""
    mandatory_fields = {
        "need_title": "Test Need",
        "business_unit": "IT",
        "need_description": "Test description"
    }
    
    score = engine.calculate_completeness_score(mandatory_fields)
    assert score == 1.0


def test_completeness_score_partial_filled(engine):
    """Test completeness score with partial fields filled."""
    mandatory_fields = {
        "need_title": "Test Need",
        "business_unit": "",
        "need_description": "Test description"
    }
    
    score = engine.calculate_completeness_score(mandatory_fields)
    assert score == pytest.approx(0.67, abs=0.01)


def test_completeness_score_empty(engine):
    """Test completeness score with all fields empty."""
    mandatory_fields = {
        "need_title": "",
        "business_unit": "",
        "need_description": ""
    }
    
    score = engine.calculate_completeness_score(mandatory_fields)
    assert score == 0.0


def test_completeness_score_empty_dict(engine):
    """Test completeness score with empty dictionary."""
    score = engine.calculate_completeness_score({})
    assert score == 0.0


def test_initial_workflow_state_high_completeness(engine):
    """Test initial state determination for high completeness."""
    state, action = engine.determine_initial_workflow_state(1.0)
    assert state == "intake_normalized"
    assert "Review" in action


def test_initial_workflow_state_threshold_completeness(engine):
    """Test initial state determination at threshold (0.8)."""
    state, action = engine.determine_initial_workflow_state(0.8)
    assert state == "intake_normalized"
    assert "Review" in action


def test_initial_workflow_state_low_completeness(engine):
    """Test initial state determination for low completeness."""
    state, action = engine.determine_initial_workflow_state(0.5)
    assert state == "intake_pending"
    assert "Complete" in action


def test_initial_workflow_state_below_threshold(engine):
    """Test initial state determination just below threshold."""
    state, action = engine.determine_initial_workflow_state(0.79)
    assert state == "intake_pending"
    assert "Complete" in action


def test_vms_routing_single_resource(engine):
    """Test VMS routing for single resource classification."""
    assert engine.validate_vms_routing_precondition("single_resource") is True


def test_vms_routing_it_service(engine):
    """Test VMS routing for IT service classification."""
    assert engine.validate_vms_routing_precondition("it_service") is False


def test_supplier_count_invalid_low(engine):
    """Test supplier count validation below minimum."""
    assert engine.validate_supplier_count(2) == "invalid_low"
    assert engine.validate_supplier_count(0) == "invalid_low"


def test_supplier_count_valid(engine):
    """Test supplier count validation within range."""
    assert engine.validate_supplier_count(3) == "valid"
    assert engine.validate_supplier_count(4) == "valid"
    assert engine.validate_supplier_count(6) == "valid"


def test_supplier_count_invalid_high(engine):
    """Test supplier count validation above maximum."""
    assert engine.validate_supplier_count(7) == "invalid_high"
    assert engine.validate_supplier_count(10) == "invalid_high"


def test_supplier_count_with_tol4(engine):
    """Test supplier count validation via TOL4 adapter."""
    result = engine.validate_supplier_count_with_tol4(4)
    
    assert "validation_result" in result
    assert "rule_snapshot" in result
    assert result["validation_result"] == "valid"
    assert result["supplier_count"] == 4


def test_supplier_count_with_tol4_invalid_low(engine):
    """Test TOL4 validation with invalid low count."""
    result = engine.validate_supplier_count_with_tol4(2)
    
    assert result["validation_result"] == "invalid_low"
    assert result["supplier_count"] == 2


def test_supplier_count_with_tol4_invalid_high(engine):
    """Test TOL4 validation with invalid high count."""
    result = engine.validate_supplier_count_with_tol4(8)
    
    assert result["validation_result"] == "invalid_high"
    assert result["supplier_count"] == 8


def test_lock_preconditions_valid(engine):
    """Test lock preconditions with valid state."""
    can_lock, reason = engine.validate_lock_preconditions("valid", True)
    assert can_lock is True
    assert reason == ""


def test_lock_preconditions_invalid_count(engine):
    """Test lock preconditions with invalid count."""
    can_lock, reason = engine.validate_lock_preconditions("invalid_low", True)
    assert can_lock is False
    assert "invalid_low" in reason


def test_lock_preconditions_missing_citations(engine):
    """Test lock preconditions with missing citations."""
    can_lock, reason = engine.validate_lock_preconditions("valid", False)
    assert can_lock is False
    assert "citation" in reason.lower()


def test_dispatch_preconditions_with_locked_longlist(engine):
    """Test dispatch preconditions with locked longlist."""
    can_dispatch, reason = engine.validate_dispatch_preconditions(True)
    assert can_dispatch is True
    assert reason == ""


def test_dispatch_preconditions_without_locked_longlist(engine):
    """Test dispatch preconditions without locked longlist."""
    can_dispatch, reason = engine.validate_dispatch_preconditions(False)
    assert can_dispatch is False
    assert "locked longlist" in reason.lower()


def test_route_single_resource_case(engine_with_session, db_session):
    """Test routing single-resource case to VMS."""
    from app.models.need_case import NeedCase
    from app.models.user import User
    from app.services.auth_service import hash_password
    
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("test123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Create test case
    case = NeedCase(
        case_number="CASE-TEST-001",
        inbound_channel="email",
        workflow_state="classification_approved",
        next_action="route_to_vms",
        final_classification="single_resource",
        created_by=user.id,
        requirement_tags="REQ-INT-001"
    )
    db_session.add(case)
    db_session.flush()
    
    # Route case to VMS
    classification_result = {
        "ai_verdict": "single_resource",
        "confirmed_verdict": "single_resource",
        "confidence_score": 0.90
    }
    
    confirmed_attributes = {
        "service_category": {"value": "software_development"},
        "estimated_duration": {"value": "6_months"}
    }
    
    vms_handoff = engine_with_session.route_single_resource_case(
        case_id=case.id,
        case_number=case.case_number,
        classification_result=classification_result,
        confirmed_attributes=confirmed_attributes
    )
    
    assert vms_handoff.case_id == case.id
    assert vms_handoff.vms_reference_id.startswith("VMS-")
    assert vms_handoff.handoff_status in ["success", "pending"]
    assert vms_handoff.request_snapshot is not None


def test_route_single_resource_case_without_session(engine):
    """Test routing without session raises error."""
    with pytest.raises(ValueError, match="Session required"):
        engine.route_single_resource_case(
            case_id=1,
            case_number="CASE-TEST-001",
            classification_result={},
            confirmed_attributes={}
        )


def test_retrieve_evidence(engine):
    """Test evidence retrieval via TOL2 adapter."""
    confirmed_attributes = {
        "service_category": {"value": "cloud_infrastructure"},
        "estimated_duration": {"value": "12_months"}
    }
    
    evidence = engine.retrieve_evidence(
        case_id=1,
        confirmed_attributes=confirmed_attributes
    )
    
    assert isinstance(evidence, list)
    assert len(evidence) > 0
    
    for item in evidence:
        assert "supplier_code" in item
        assert "supplier_name" in item
        assert "evidence_type" in item
        assert "citation_label" in item
        assert "evidence_summary" in item


def test_retrieve_evidence_normalizes_fields(engine):
    """Test that evidence retrieval normalizes all expected fields."""
    confirmed_attributes = {
        "service_category": {"value": "security"}
    }
    
    evidence = engine.retrieve_evidence(
        case_id=1,
        confirmed_attributes=confirmed_attributes
    )
    
    # Verify all normalized fields are present
    for item in evidence:
        assert "supplier_code" in item
        assert "supplier_name" in item
        assert "evidence_type" in item
        assert "external_ref" in item
        assert "citation_label" in item
        assert "citation_ref" in item
        assert "evidence_summary" in item
        assert "evidence_found" in item
        assert "service_domain" in item
        # completion_date and signed_date may be None


def test_resolve_mappings(engine):
    """Test panel/functional-group mapping resolution via TOL3 adapter."""
    confirmed_attributes = {
        "service_category": {"value": "cloud_infrastructure"}
    }
    
    mappings = engine.resolve_mappings(
        case_id=1,
        confirmed_attributes=confirmed_attributes
    )
    
    assert isinstance(mappings, list)
    assert len(mappings) > 0
    
    for mapping in mappings:
        assert "panel_code" in mapping
        assert "panel_name" in mapping
        assert "functional_group_code" in mapping
        assert "functional_group_name" in mapping
        assert "rationale_inputs" in mapping


def test_resolve_mappings_different_categories(engine):
    """Test mapping resolution for different service categories."""
    # Test cloud category
    cloud_mappings = engine.resolve_mappings(
        case_id=1,
        confirmed_attributes={"service_category": {"value": "cloud_infrastructure"}}
    )
    assert any("CLOUD" in m.get("panel_code", "") for m in cloud_mappings)
    
    # Test security category
    sec_mappings = engine.resolve_mappings(
        case_id=2,
        confirmed_attributes={"service_category": {"value": "security"}}
    )
    assert any("SEC" in m.get("panel_code", "") for m in sec_mappings)
    
    # Test application category
    app_mappings = engine.resolve_mappings(
        case_id=3,
        confirmed_attributes={"service_category": {"value": "software_development"}}
    )
    assert any("APP" in m.get("panel_code", "") for m in app_mappings)
