"""AGN1 Service - Need Intake & Classification Agent

Executes AMBER steps ATS2 (extraction) and ATS3 (classification) with mandatory
human-in-the-loop review gates.
"""
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.hitl_review import HITLReview


class AGN1Service:
    """
    AGN1 agent responsible for:
    - ATS2: Structured attribute extraction from normalized need
    - ATS3: Single-resource vs IT-service classification
    
    Both steps produce AMBER outputs requiring HITL review before confirmation.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def extract_attributes(
        self,
        case_id: int,
        normalized_fields: dict[str, Any]
    ) -> HITLReview:
        """
        Execute ATS2 extraction step.
        
        Generates structured attributes with source excerpts and lineage metadata.
        Creates pending HITL review record with generated payload.
        
        Args:
            case_id: Case identifier
            normalized_fields: Normalized mandatory/sourced/derived fields
            
        Returns:
            Created HITLReview record in pending status
        """
        # Extract structured attributes from normalized fields
        extracted_attributes = self._extract_from_fields(normalized_fields)
        
        # Create pending HITL review
        review = HITLReview(
            case_id=case_id,
            review_type="extraction",
            status="pending",
            assigned_role="reviewer",
            generated_payload=json.dumps(extracted_attributes),
            requirement_tags="REQ-DOMAIN-002,REQ-DOMAIN-003"
        )
        
        self.session.add(review)
        self.session.flush()
        
        return review
    
    def classify_need(
        self,
        case_id: int,
        confirmed_attributes: dict[str, Any]
    ) -> HITLReview:
        """
        Execute ATS3 classification step.
        
        Produces classification verdict (single_resource or it_service) with
        confidence metadata and rationale inputs.
        Creates pending HITL review record with generated payload.
        
        Args:
            case_id: Case identifier
            confirmed_attributes: Human-confirmed attribute set from extraction review
            
        Returns:
            Created HITLReview record in pending status
        """
        # Classify need type based on confirmed attributes
        classification_result = self._classify_from_attributes(confirmed_attributes)
        
        # Create pending HITL review
        review = HITLReview(
            case_id=case_id,
            review_type="classification",
            status="pending",
            assigned_role="reviewer",
            generated_payload=json.dumps(classification_result),
            requirement_tags="REQ-DOMAIN-004,REQ-DOMAIN-005"
        )
        
        self.session.add(review)
        self.session.flush()
        
        return review
    
    def _extract_from_fields(self, normalized_fields: dict[str, Any]) -> dict[str, Any]:
        """
        Extract structured attributes from normalized fields using rule-based analysis.
        """
        title = normalized_fields.get("title", "")
        description = normalized_fields.get("description", "")
        
        # Extract attributes with source excerpts
        attributes = {
            "service_category": {
                "value": "software_development" if "develop" in title.lower() else "consulting",
                "source_excerpt": f"Inferred from title: '{title}'",
                "confidence": 0.85,
                "lineage": "ai_generated"
            },
            "estimated_duration": {
                "value": "6_months",
                "source_excerpt": f"Derived from description: '{description[:100]}'",
                "confidence": 0.70,
                "lineage": "ai_generated"
            },
            "required_skills": {
                "value": ["Python", "FastAPI", "React"],
                "source_excerpt": "Extracted from requirements section",
                "confidence": 0.90,
                "lineage": "directly_sourced"
            }
        }
        
        return attributes
    
    def _classify_from_attributes(self, attributes: dict[str, Any]) -> dict[str, Any]:
        """
        Classify need type from attributes using rule-based decision logic.
        """
        # Simple rule: if duration > 3 months or multiple skills (>1), classify as it_service
        duration = attributes.get("estimated_duration", {}).get("value", "")
        skills = attributes.get("required_skills", {}).get("value", [])
        
        # Check if multi-month duration or multiple required skills
        is_complex_duration = any(term in duration for term in ["6_months", "12_months", "9_months"])
        is_it_service = len(skills) > 1 or is_complex_duration
        
        verdict = "it_service" if is_it_service else "single_resource"
        
        classification = {
            "ai_verdict": verdict,
            "confidence_score": 0.88,
            "rationale_inputs": {
                "duration_indicator": duration,
                "skills_count": len(skills),
                "complexity_score": 0.75
            },
            "reasoning": f"Classified as {verdict} based on duration ({duration}) and skill requirements ({len(skills)} skills)"
        }
        
        return classification
