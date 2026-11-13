"""Journey J-01: Intake to Classification acceptance tests.

Tests the complete user journey from need intake (ATS1) through attribute review
(ATS2) and classification review (ATS3), covering all in-scope features FR-001,
FR-002, and FR-003.
"""

import json
from datetime import datetime

import pytest


def test_j01_complete_it_service_journey(auth_client, db_session):
    """Test complete J-01 journey for IT service classification.

    Journey steps:
    - ATS1: Ingest need from RFP channel
    - ATS2: Review and approve extracted attributes
    - ATS3: Review and approve IT service classification
    """
    correlation_id = "J01-IT-001"

    # ATS1: Ingest need
    intake_payload = {
        "business_unit_id": "BU-TEST-J01",
        "channel_type": "rfp",
        "raw_artifact_ref": "s3://test/j01-rfp.pdf",
        "normalized_payload_json": json.dumps({
            "title": "Enterprise Application Services",
            "description": "Full-stack application development team"
        }),
        "need_attributes": {
            "service_type": "Application Development",
            "scope_description": "Full-stack enterprise application development",
            "estimated_volume_duration": "18 months, 6-8 FTE",
            "required_skills": json.dumps(["Java", "React", "PostgreSQL", "AWS"]),
            "budget_indication": "€800K-€1.2M annually",
            "delivery_location": "Germany (hybrid)"
        }
    }

    intake_resp = auth_client.post(
        "/api/v1/intake/needs",
        json=intake_payload,
        headers={"X-Correlation-Id": correlation_id}
    )
    assert intake_resp.status_code == 201, f"Intake failed: {intake_resp.text}"
    intake_data = intake_resp.json()
    assert intake_data["status"] == "normalized"
    assert intake_data["correlation_id"] == correlation_id
    need_id = intake_data["need_id"]

    # ATS2: Review attributes (approve)
    review_payload = {
        "review_decision": "approve",
        "need_attributes": intake_payload["need_attributes"],
        "reviewer_notes": "Attributes clear and complete"
    }

    review_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/attributes",
        json=review_payload
    )
    assert review_resp.status_code == 200, f"Attribute review failed: {review_resp.text}"
    review_data = review_resp.json()
    assert review_data["next_status"] == "classification_review_pending"

    # ATS3: Classify as IT service (approve)
    classification_payload = {
        "classification_verdict": "it_service",
        "classification_confidence": 0.91,
        "rationale": "Full-stack team requirement, clearly IT service",
        "review_decision": "approve",
        "escalation_required": False,
        "exemplars_referenced": ["EXEMPLAR-IT-002", "EXEMPLAR-IT-006"]
    }

    classification_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/classification",
        json=classification_payload
    )
    assert classification_resp.status_code == 200, f"Classification review failed: {classification_resp.text}"
    classification_data = classification_resp.json()
    assert classification_data["workflow_status"] == "classified_it_service"
    assert classification_data["classification_verdict"] == "it_service"


def test_j01_complete_single_resource_journey(auth_client, db_session):
    """Test complete J-01 journey for single resource classification.

    Journey steps:
    - ATS1: Ingest need from email channel
    - ATS2: Review and approve extracted attributes
    - ATS3: Review and approve single_resource classification
    """
    correlation_id = "J01-SR-001"

    # ATS1: Ingest single resource need
    intake_payload = {
        "business_unit_id": "BU-TEST-J01-SR",
        "channel_type": "email",
        "raw_artifact_ref": "email://inbox/j01-sr-001.eml",
        "normalized_payload_json": json.dumps({
            "title": "Senior DevOps Engineer",
            "description": "1 senior engineer for 8 months"
        }),
        "need_attributes": {
            "service_type": "DevOps Engineering",
            "scope_description": "Senior DevOps engineer for CI/CD pipeline setup",
            "estimated_volume_duration": "8 months, 1 FTE",
            "required_skills": json.dumps(["Kubernetes", "GitLab CI", "Terraform"]),
            "budget_indication": "€80K-€95K total",
            "delivery_location": "Frankfurt office"
        }
    }

    intake_resp = auth_client.post(
        "/api/v1/intake/needs",
        json=intake_payload,
        headers={"X-Correlation-Id": correlation_id}
    )
    assert intake_resp.status_code == 201
    need_id = intake_resp.json()["need_id"]

    # ATS2: Review attributes (approve)
    review_payload = {
        "review_decision": "approve",
        "need_attributes": intake_payload["need_attributes"],
        "reviewer_notes": "Single resource attributes validated"
    }

    review_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/attributes",
        json=review_payload
    )
    assert review_resp.status_code == 200

    # ATS3: Classify as single_resource (approve)
    classification_payload = {
        "classification_verdict": "single_resource",
        "classification_confidence": 0.93,
        "rationale": "Single engineer, fixed duration, clearly single resource",
        "review_decision": "approve",
        "escalation_required": False,
        "exemplars_referenced": ["EXEMPLAR-SR-001"]
    }

    classification_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/classification",
        json=classification_payload
    )
    assert classification_resp.status_code == 200
    classification_data = classification_resp.json()
    assert classification_data["workflow_status"] == "classified_single_resource"
    assert classification_data["classification_verdict"] == "single_resource"


def test_j01_attribute_review_modification(auth_client, db_session):
    """Test J-01 with attribute modification during ATS2 review."""
    correlation_id = "J01-MODIFY-001"

    # ATS1: Ingest need with low-confidence attributes
    intake_payload = {
        "business_unit_id": "BU-TEST-J01-MOD",
        "channel_type": "phone",
        "raw_artifact_ref": "phone://notes/j01-mod-001.txt",
        "normalized_payload_json": json.dumps({
            "title": "Data Analytics Service",
            "description": "Analytics team needed"
        }),
        "need_attributes": {
            "service_type": "Data Analytics",
            "scope_description": "Initial extraction unclear",
            "estimated_volume_duration": "Unknown",
            "required_skills": json.dumps([]),
            "budget_indication": "Not specified",
            "delivery_location": "TBD"
        }
    }

    intake_resp = auth_client.post(
        "/api/v1/intake/needs",
        json=intake_payload,
        headers={"X-Correlation-Id": correlation_id}
    )
    assert intake_resp.status_code == 201
    need_id = intake_resp.json()["need_id"]

    # ATS2: Review and modify attributes
    modified_attrs = {
        "service_type": "Business Intelligence & Analytics",
        "scope_description": "Data analytics and BI reporting team, 4-6 analysts",
        "estimated_volume_duration": "12 months, 4-6 FTE",
        "required_skills": json.dumps(["SQL", "Tableau", "Python", "Data Modeling"]),
        "budget_indication": "€400K-€600K annually",
        "delivery_location": "Remote (EU-based)"
    }

    review_payload = {
        "review_decision": "modify",
        "need_attributes": modified_attrs,
        "reviewer_notes": "Corrected attributes based on stakeholder clarification"
    }

    review_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/attributes",
        json=review_payload
    )
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert review_data["next_status"] == "classification_review_pending"
    # Modified attributes should be reflected
    assert review_data["need_attributes"]["service_type"] == "Business Intelligence & Analytics"


def test_j01_classification_low_confidence_hold(auth_client, db_session):
    """Test J-01 with low confidence classification held for review."""
    correlation_id = "J01-LOWCONF-001"

    # ATS1: Ingest borderline case
    intake_payload = {
        "business_unit_id": "BU-TEST-J01-LC",
        "channel_type": "rfp",
        "raw_artifact_ref": "s3://test/j01-borderline.pdf",
        "normalized_payload_json": json.dumps({
            "title": "Mixed Services Request",
            "description": "Could be team or single resource"
        }),
        "need_attributes": {
            "service_type": "Development Support",
            "scope_description": "Development assistance, scope unclear",
            "estimated_volume_duration": "6 months, 1-3 resources",
            "required_skills": json.dumps(["JavaScript"]),
            "budget_indication": "€150K total",
            "delivery_location": "Remote"
        }
    }

    intake_resp = auth_client.post(
        "/api/v1/intake/needs",
        json=intake_payload,
        headers={"X-Correlation-Id": correlation_id}
    )
    assert intake_resp.status_code == 201
    need_id = intake_resp.json()["need_id"]

    # ATS2: Approve attributes
    review_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/attributes",
        json={
            "review_decision": "approve",
            "need_attributes": intake_payload["need_attributes"],
            "reviewer_notes": "Attributes acceptable"
        }
    )
    assert review_resp.status_code == 200

    # ATS3: Low confidence classification - held for review
    classification_payload = {
        "classification_verdict": "it_service",
        "classification_confidence": 0.62,  # Below typical threshold
        "rationale": "Borderline case, confidence low, held for human review",
        "review_decision": "approve",
        "escalation_required": True,
        "exemplars_referenced": []
    }

    classification_resp = auth_client.post(
        f"/api/v1/reviews/needs/{need_id}/classification",
        json=classification_payload
    )
    assert classification_resp.status_code == 200
    classification_data = classification_resp.json()
    # Low confidence cases should still advance but be flagged
    assert classification_data["escalation_required"] is True
    assert classification_data["classification_confidence"] == 0.62
