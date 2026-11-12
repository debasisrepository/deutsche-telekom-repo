"""Integration tests for cases endpoints."""


def test_create_case_rfp_document(auth_client, db_session):
    """Test creating a case from RFP document intake."""
    response = auth_client.post("/api/v1/cases", json={
        "channel": "rfp_document",
        "title": "Cloud Migration Project",
        "business_unit": "IT",
        "description": "Migrate on-premises infrastructure to cloud",
        "artifact_type": "rfp_document",
        "artifact_ref": "rfp-test-001.pdf"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "case_number" in data
    assert data["case_number"].startswith("CASE-2026-")
    assert data["inbound_channel"] == "rfp_document"
    assert data["workflow_state"] in ["intake_normalized", "intake_pending"]
    assert "normalized_need" in data
    assert data["normalized_need"]["completeness_score"] >= 0.0


def test_create_case_email(auth_client):
    """Test creating a case from email intake."""
    response = auth_client.post("/api/v1/cases", json={
        "channel": "email",
        "title": "Security Assessment",
        "business_unit": "Security",
        "description": "Quarterly security audit",
        "artifact_type": "email",
        "artifact_ref": "email-test-001.eml"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["inbound_channel"] == "email"
    assert "normalized_need" in data


def test_create_case_phone_note(auth_client):
    """Test creating a case from phone note intake."""
    response = auth_client.post("/api/v1/cases", json={
        "channel": "phone_note",
        "title": "Urgent Hardware Replacement",
        "business_unit": "Facilities",
        "description": "Replace failed server hardware",
        "artifact_type": "phone_note",
        "artifact_ref": "note-test-001.txt"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["inbound_channel"] == "phone_note"


def test_create_case_supplier_offer(auth_client):
    """Test creating a case from supplier offer intake."""
    response = auth_client.post("/api/v1/cases", json={
        "channel": "supplier_offer",
        "title": "Network Equipment Upgrade",
        "business_unit": "Network Operations",
        "description": "Upgrade network switches and routers",
        "artifact_type": "supplier_offer",
        "artifact_ref": "offer-test-001.pdf"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["inbound_channel"] == "supplier_offer"


def test_get_case_by_id(auth_client, db_session):
    """Test retrieving case by ID."""
    # Create a case first
    create_response = auth_client.post("/api/v1/cases", json={
        "channel": "rfp_document",
        "title": "Test Case",
        "business_unit": "IT",
        "description": "Test description",
        "artifact_type": "rfp_document",
        "artifact_ref": "test.pdf"
    })
    assert create_response.status_code == 201
    case_id = create_response.json()["id"]
    
    # Get the case
    response = auth_client.get(f"/api/v1/cases/{case_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert data["workflow_state"] in ["intake_normalized", "intake_pending"]
    assert "normalized_need" in data
    assert len(data["source_artifacts"]) > 0


def test_get_case_not_found(auth_client):
    """Test retrieving nonexistent case."""
    response = auth_client.get("/api/v1/cases/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_cases(auth_client):
    """Test listing cases with pagination."""
    # Create a few cases
    for i in range(3):
        auth_client.post("/api/v1/cases", json={
            "channel": "email",
            "title": f"Test Case {i}",
            "business_unit": "IT",
            "description": f"Test description {i}",
            "artifact_type": "email",
            "artifact_ref": f"test-{i}.eml"
        })
    
    # List cases
    response = auth_client.get("/api/v1/cases")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 3
    assert len(data["items"]) > 0


def test_list_cases_pagination(auth_client):
    """Test case list pagination."""
    # Create cases
    for i in range(5):
        auth_client.post("/api/v1/cases", json={
            "channel": "email",
            "title": f"Pagination Test {i}",
            "business_unit": "IT",
            "description": f"Test {i}",
            "artifact_type": "email",
            "artifact_ref": f"page-{i}.eml"
        })
    
    # Get page 1
    response = auth_client.get("/api/v1/cases?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_case_has_source_artifact(auth_client):
    """Test that created case includes source artifact."""
    response = auth_client.post("/api/v1/cases", json={
        "channel": "rfp_document",
        "title": "Artifact Test",
        "business_unit": "IT",
        "description": "Test artifact preservation",
        "artifact_type": "rfp_document",
        "artifact_ref": "artifact-test.pdf"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert len(data["source_artifacts"]) == 1
    artifact = data["source_artifacts"][0]
    assert artifact["artifact_type"] == "rfp_document"
    assert artifact["storage_ref"] == "artifact-test.pdf"
    assert artifact["source_channel"] == "rfp_document"


def test_case_normalization_completeness(auth_client):
    """Test that case normalization tracks completeness."""
    # Complete case
    complete_response = auth_client.post("/api/v1/cases", json={
        "channel": "email",
        "title": "Complete Case",
        "business_unit": "IT",
        "description": "Complete description",
        "artifact_type": "email",
        "artifact_ref": "complete.eml"
    })
    
    assert complete_response.status_code == 201
    complete_data = complete_response.json()
    assert complete_data["normalized_need"]["completeness_score"] == 1.0
    assert complete_data["workflow_state"] == "intake_normalized"
