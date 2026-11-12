"""Unit tests for AGN2 service."""



def test_agn2_generate_ranked_longlist(db_session):
    """Test AGN2 ranked longlist generation."""
    from app.models.case_evidence import CaseEvidence
    from app.models.need_case import NeedCase
    from app.models.supplier import Supplier
    from app.services.agents.agn2_service import AGN2Service
    
    # Create test case
    case = NeedCase(
        case_number="AGN2-TEST-001",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Add suppliers with evidence
    suppliers = []
    for i in range(3):
        supplier = Supplier(
            supplier_code=f"AGN2-SUP-{i+1}",
            display_name=f"AGN2 Test Supplier {i+1}",
            status="active"
        )
        db_session.add(supplier)
        db_session.flush()
        suppliers.append(supplier)
        
        evidence = CaseEvidence(
            case_id=case.id,
            supplier_id=supplier.id,
            citation_label=f"AGN2 Evidence {i+1}",
            citation_ref=f"agn2/ref/{i+1}",
            evidence_summary=f"AGN2 Summary {i+1}",
            evidence_found=True
        )
        db_session.add(evidence)
    
    db_session.commit()
    
    # Generate longlist
    agn2_service = AGN2Service(db_session)
    result = agn2_service.generate_ranked_longlist(
        case_id=case.id,
        confirmed_attributes={"service_category": "cloud"},
        mapping_info={"panel": "TEST-PANEL"},
        agent_run_id="agn2-test-run-1"
    )
    
    # Verify result structure
    assert "proposal_id" in result
    assert "case_id" in result
    assert result["case_id"] == case.id
    assert "suppliers" in result
    assert len(result["suppliers"]) == 3
    assert result["total_suppliers"] == 3
    
    # Verify suppliers are ranked
    for idx, supplier_data in enumerate(result["suppliers"]):
        assert supplier_data["rank_position"] == idx + 1
        assert "ranking_score" in supplier_data
        assert "citation_complete" in supplier_data


def test_agn2_citation_completeness(db_session):
    """Test that AGN2 correctly marks citation completeness."""
    from app.models.case_evidence import CaseEvidence
    from app.models.need_case import NeedCase
    from app.models.supplier import Supplier
    from app.services.agents.agn2_service import AGN2Service
    
    # Create test case
    case = NeedCase(
        case_number="AGN2-TEST-002",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Add supplier with complete evidence
    supplier1 = Supplier(
        supplier_code="CITE-SUP-001",
        display_name="Complete Citation Supplier",
        status="active"
    )
    db_session.add(supplier1)
    db_session.flush()
    
    evidence1 = CaseEvidence(
        case_id=case.id,
        supplier_id=supplier1.id,
        citation_label="Complete Evidence",
        citation_ref="complete/ref",
        evidence_summary="Complete summary",
        evidence_found=True
    )
    db_session.add(evidence1)
    
    # Add supplier with incomplete evidence
    supplier2 = Supplier(
        supplier_code="CITE-SUP-002",
        display_name="Incomplete Citation Supplier",
        status="active"
    )
    db_session.add(supplier2)
    db_session.flush()
    
    evidence2 = CaseEvidence(
        case_id=case.id,
        supplier_id=supplier2.id,
        citation_label="Incomplete Evidence",
        citation_ref="incomplete/ref",
        evidence_summary="Incomplete summary",
        evidence_found=False
    )
    db_session.add(evidence2)
    db_session.commit()
    
    # Generate longlist
    agn2_service = AGN2Service(db_session)
    result = agn2_service.generate_ranked_longlist(
        case_id=case.id,
        confirmed_attributes={"service_category": "test"},
        agent_run_id="agn2-test-run-2"
    )
    
    # Verify citation completeness flags
    assert len(result["suppliers"]) == 2
    assert result["suppliers"][0]["citation_complete"] is True
    assert result["suppliers"][1]["citation_complete"] is False


def test_agn2_empty_evidence(db_session):
    """Test AGN2 behavior with no evidence."""
    from app.models.need_case import NeedCase
    from app.services.agents.agn2_service import AGN2Service
    
    # Create test case without evidence
    case = NeedCase(
        case_number="AGN2-TEST-003",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.commit()
    
    # Generate longlist
    agn2_service = AGN2Service(db_session)
    result = agn2_service.generate_ranked_longlist(
        case_id=case.id,
        confirmed_attributes={"service_category": "test"},
        agent_run_id="agn2-test-run-3"
    )
    
    # Should still create a proposal, even if empty
    assert "proposal_id" in result
    assert result["total_suppliers"] == 0
    assert len(result["suppliers"]) == 0
