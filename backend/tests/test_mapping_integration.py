"""Integration tests for panel mapping functionality."""
import json


def test_store_and_list_mappings(client, auth_client, db_session):
    """Test storing and listing panel/functional-group mappings."""
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    from app.services.mapping.panel_mapping_service import PanelMappingService
    
    # Create a test case
    case = NeedCase(
        case_number="MAP-TEST-001",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Add normalized need with confirmed attributes
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({
            "service_category": "cloud_infrastructure",
            "need_title": "Cloud Migration"
        }),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    db_session.commit()
    
    # Store mappings
    mapping_service = PanelMappingService(db_session)
    confirmed_attrs = json.loads(normalized.mandatory_fields)
    stored_mappings = mapping_service.store_mappings(case.id, confirmed_attrs)
    
    # Verify stored mappings
    assert len(stored_mappings) > 0
    assert "panel_code" in stored_mappings[0]
    assert "functional_group_code" in stored_mappings[0]
    
    # List mappings
    listed_mappings = mapping_service.list_mappings(case.id)
    assert len(listed_mappings) == len(stored_mappings)
    assert listed_mappings[0]["panel_code"] == stored_mappings[0]["panel_code"]


def test_mapping_endpoint(auth_client, db_session):
    """Test GET /api/v1/cases/{caseId}/mapping endpoint."""
    from app.models.case_mapping import CaseMapping
    from app.models.functional_group import FunctionalGroup
    from app.models.need_case import NeedCase
    from app.models.panel import Panel
    
    # Create test case
    case = NeedCase(
        case_number="MAP-TEST-002",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Create panel and functional group
    panel = Panel(panel_code="TEST-PANEL-001", panel_name="Test Panel")
    fg = FunctionalGroup(functional_group_code="TEST-FG-001", functional_group_name="Test FG")
    db_session.add_all([panel, fg])
    db_session.flush()
    
    # Create mapping
    mapping = CaseMapping(
        case_id=case.id,
        panel_id=panel.id,
        functional_group_id=fg.id,
        mapping_status="proposed",
        rationale_inputs="Test mapping"
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Call endpoint
    response = auth_client.get(f"/api/v1/cases/{case.id}/mapping")
    assert response.status_code == 200
    
    data = response.json()
    assert data["case_id"] == case.id
    assert data["case_number"] == "MAP-TEST-002"
    assert "mappings" in data
    assert len(data["mappings"]) == 1
    assert data["mappings"][0]["panel_code"] == "TEST-PANEL-001"


def test_mapping_repository_idempotency(db_session):
    """Test that panel and functional group creation is idempotent."""
    from app.repositories.mapping_repository import MappingRepository
    
    repo = MappingRepository(db_session)
    
    # Create panel twice
    panel1 = repo.get_or_create_panel("IDEM-PANEL-001", "Idempotent Panel")
    panel2 = repo.get_or_create_panel("IDEM-PANEL-001", "Idempotent Panel")
    
    assert panel1.id == panel2.id
    
    # Create functional group twice
    fg1 = repo.get_or_create_functional_group("IDEM-FG-001", "Idempotent FG")
    fg2 = repo.get_or_create_functional_group("IDEM-FG-001", "Idempotent FG")
    
    assert fg1.id == fg2.id
