"""Workflow Orchestrator Service - Manages case lifecycle and state transitions"""
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.adapters.tol1_ingest_adapter import TOL1IngestAdapter
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.source_artifact import SourceArtifact
from app.services.agents.agn1_service import AGN1Service
from app.services.audit.audit_service import AuditService
from app.services.rules.agn5_rule_engine import AGN5RuleEngine


class WorkflowOrchestratorService:
    """
    Orchestrates workflow operations including case creation, state transitions,
    and coordination between agents and deterministic steps.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.tol1_adapter = TOL1IngestAdapter()
        self.agn5_engine = AGN5RuleEngine(session)
        self.agn1_service = AGN1Service(session)
        self.audit_service = AuditService(session)
    
    def create_case_from_intake(
        self,
        channel: str,
        raw_content: dict[str, Any],
        created_by_user_id: int
    ) -> NeedCase:
        """
        Create a new case from intake submission.
        Performs ATS1 normalization step.
        
        Args:
            channel: Inbound channel (rfp_document, email, phone_note, supplier_offer)
            raw_content: Raw intake data
            created_by_user_id: ID of user creating the case
            
        Returns:
            Created NeedCase with normalized need and source artifact
        """
        # Step 1: Normalize intake via TOL1 adapter
        normalized_data = self.tol1_adapter.normalize_intake(channel, raw_content)
        
        # Step 2: Calculate completeness score via AGN5
        completeness_score = self.agn5_engine.calculate_completeness_score(
            normalized_data["mandatory_fields"]
        )
        
        # Step 3: Determine initial workflow state via AGN5
        workflow_state, next_action = self.agn5_engine.determine_initial_workflow_state(
            completeness_score
        )
        
        # Step 4: Generate unique case number
        case_number = self._generate_case_number()
        
        # Step 5: Create case
        case = NeedCase(
            case_number=case_number,
            inbound_channel=channel,
            workflow_state=workflow_state,
            next_action=next_action,
            created_by=created_by_user_id,
            requirement_tags="REQ-DATA-001,REQ-DATA-002,REQ-DOMAIN-001"
        )
        self.session.add(case)
        self.session.flush()  # Get case.id for FK references
        
        # Step 6: Create normalized need record
        normalized_need = NormalizedNeed(
            case_id=case.id,
            mandatory_fields=json.dumps(normalized_data["mandatory_fields"]),
            sourced_fields=json.dumps(normalized_data["sourced_fields"]),
            derived_fields=json.dumps(normalized_data["derived_fields"]),
            completeness_score=completeness_score,
            requirement_tags="REQ-DATA-002"
        )
        self.session.add(normalized_need)
        
        # Step 7: Create source artifact record
        artifact = SourceArtifact(
            case_id=case.id,
            artifact_type=raw_content.get("artifact_type", "form_submission"),
            storage_ref=raw_content.get("artifact_ref", ""),
            source_channel=channel,
            requirement_tags="REQ-DATA-001"
        )
        self.session.add(artifact)
        
        # Step 8: Record workflow event and audit log
        self.audit_service.record_workflow_event(
            case_id=case.id,
            event_type="case_created",
            from_state=None,
            to_state=workflow_state,
            actor_type="user",
            actor_id=str(created_by_user_id),
            payload=json.dumps({
                "case_number": case_number,
                "inbound_channel": channel,
                "completeness_score": completeness_score
            })
        )
        
        self.audit_service.record_audit(
            case_id=case.id,
            action_type="case_creation",
            actor_type="user",
            actor_id=str(created_by_user_id),
            target_type="need_case",
            target_id=str(case.id),
            audit_payload=json.dumps({
                "case_number": case_number,
                "channel": channel,
                "workflow_state": workflow_state
            })
        )
        
        self.session.commit()
        self.session.refresh(case)
        
        return case
    
    def route_single_resource_case(
        self,
        case_id: int,
        reviewer_id: int
    ) -> NeedCase:
        """
        Route single-resource case to VMS and close supplier-selection workflow.
        
        Args:
            case_id: Case identifier
            reviewer_id: ID of user triggering VMS routing
            
        Returns:
            Updated NeedCase with routed-out status
        """
        from app.models.classification_result import ClassificationResult
        
        case = self.session.get(NeedCase, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")
        
        # Verify case is classified as single_resource
        if case.final_classification != "single_resource":
            raise ValueError(f"Case {case_id} is not classified as single_resource")
        
        # Get classification result
        classification_result = self.session.query(ClassificationResult).filter_by(case_id=case_id).first()
        if classification_result is None:
            raise ValueError(f"No classification result found for case {case_id}")
        
        # Get confirmed attributes from extraction review
        from app.repositories.review_repository import ReviewRepository
        review_repo = ReviewRepository(self.session)
        extraction_reviews = review_repo.get_by_case_and_type(case_id, "extraction", "approved")
        
        confirmed_attributes: dict[str, Any] = {}
        if extraction_reviews:
            extraction_review = extraction_reviews[0]
            confirmed_attributes = json.loads(extraction_review.final_payload) if extraction_review.final_payload else {}
        
        # Build classification result dict
        classification_dict = {
            "confirmed_verdict": classification_result.confirmed_verdict,
            "ai_verdict": classification_result.ai_verdict,
            "confidence_score": classification_result.confidence_score
        }
        
        # Route to VMS via AGN5
        vms_handoff = self.agn5_engine.route_single_resource_case(
            case_id=case.id,
            case_number=case.case_number,
            classification_result=classification_dict,
            confirmed_attributes=confirmed_attributes
        )
        
        # Update case workflow state to routed-out
        from_state = case.workflow_state
        case.workflow_state = "routed_to_vms"
        case.next_action = "vms_processing"
        
        # Record workflow event
        self.audit_service.record_workflow_event(
            case_id=case.id,
            event_type="vms_handoff",
            from_state=from_state,
            to_state=case.workflow_state,
            actor_type="user",
            actor_id=str(reviewer_id),
            payload=json.dumps({
                "vms_reference_id": vms_handoff.vms_reference_id,
                "handoff_status": vms_handoff.handoff_status
            })
        )
        
        self.audit_service.record_audit(
            case_id=case.id,
            action_type="vms_routing",
            actor_type="user",
            actor_id=str(reviewer_id),
            target_type="vms_handoff",
            target_id=str(vms_handoff.id),
            audit_payload=json.dumps({
                "vms_reference_id": vms_handoff.vms_reference_id,
                "case_number": case.case_number
            })
        )
        
        self.session.commit()
        self.session.refresh(case)
        
        return case
    
    def apply_extraction_decision(
        self,
        case_id: int,
        decision: str,
        reviewer_id: int,
        edited_attributes: dict[str, Any] | None = None
    ) -> NeedCase:
        """
        Apply extraction review decision and advance workflow.
        
        Args:
            case_id: Case identifier
            decision: Decision type (approve, edit, reject)
            reviewer_id: ID of user making decision
            edited_attributes: Optional edited attributes for 'edit' decision
            
        Returns:
            Updated NeedCase after decision applied
        """
        from app.services.reviews.hitl_service import HITLService
        
        hitl_service = HITLService(self.session)
        
        # Get pending extraction review
        from app.repositories.review_repository import ReviewRepository
        review_repo = ReviewRepository(self.session)
        reviews = review_repo.get_by_case_and_type(case_id, "extraction", "pending")
        
        if not reviews:
            raise ValueError(f"No pending extraction review for case {case_id}")
        
        review = reviews[0]
        
        # Apply decision
        hitl_service.apply_decision(
            review_id=review.id,
            decision=decision,
            reviewer_id=reviewer_id,
            edited_payload=edited_attributes
        )
        
        # If approved, trigger classification
        if decision in ["approve", "edit"]:
            self._trigger_classification(case_id, review)
        
        self.session.commit()
        
        case = self.session.get(NeedCase, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found after decision applied")
        return case
    
    def apply_classification_decision(
        self,
        case_id: int,
        decision: str,
        reviewer_id: int,
        confirmed_verdict: str | None = None
    ) -> NeedCase:
        """
        Apply classification review decision and route case.
        
        Args:
            case_id: Case identifier
            decision: Decision type (confirm, override)
            reviewer_id: ID of user making decision
            confirmed_verdict: Override verdict for 'override' decision
            
        Returns:
            Updated NeedCase after decision applied
        """
        from app.models.classification_result import ClassificationResult
        from app.services.reviews.hitl_service import HITLService
        
        hitl_service = HITLService(self.session)
        
        # Get pending classification review
        from app.repositories.review_repository import ReviewRepository
        review_repo = ReviewRepository(self.session)
        reviews = review_repo.get_by_case_and_type(case_id, "classification", "pending")
        
        if not reviews:
            raise ValueError(f"No pending classification review for case {case_id}")
        
        review = reviews[0]
        
        # Parse generated payload
        import json
        generated_payload = json.loads(review.generated_payload) if review.generated_payload else {}
        ai_verdict = generated_payload.get("ai_verdict", "it_service")
        
        # Determine override payload
        override_payload = None
        if decision == "override" and confirmed_verdict:
            override_payload = {
                "ai_verdict": ai_verdict,
                "confirmed_verdict": confirmed_verdict,
                "overridden": True
            }
        
        # Apply decision
        hitl_service.apply_decision(
            review_id=review.id,
            decision=decision,
            reviewer_id=reviewer_id,
            edited_payload=override_payload
        )
        
        # Create or update classification_result
        final_verdict: str = confirmed_verdict if (decision == "override" and confirmed_verdict) else ai_verdict
        
        classification_result = self.session.query(ClassificationResult).filter_by(case_id=case_id).first()
        if classification_result is None:
            classification_result = ClassificationResult(
                case_id=case_id,
                ai_verdict=ai_verdict,
                confirmed_verdict=final_verdict,
                confidence_score=generated_payload.get("confidence_score", 0.0),
                rationale_inputs=json.dumps(generated_payload.get("rationale_inputs", {})),
                overridden=(decision == "override"),
                requirement_tags="REQ-DOMAIN-005"
            )
            self.session.add(classification_result)
        else:
            classification_result.confirmed_verdict = final_verdict
            classification_result.overridden = (decision == "override")
        
        # Update case final_classification
        case = self.session.get(NeedCase, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found after review applied")
        
        case.final_classification = final_verdict
        
        self.session.commit()
        
        return case
    
    def _trigger_classification(self, case_id: int, extraction_review) -> None:
        """
        Trigger AGN1 classification after extraction approval.
        
        Args:
            case_id: Case identifier
            extraction_review: Approved extraction review with final attributes
        """
        import json
        
        # Get confirmed attributes from extraction review
        final_payload = json.loads(extraction_review.final_payload) if extraction_review.final_payload else {}
        
        # Trigger AGN1 classification (ATS3)
        classification_review = self.agn1_service.classify_need(case_id, final_payload)
        
        # Update case workflow state
        case = self.session.get(NeedCase, case_id)
        if case:
            case.workflow_state = "classification_pending"
            case.next_action = "classification_review_required"
            
            # Record workflow event
            self.audit_service.record_workflow_event(
                case_id=case.id,
                event_type="classification_initiated",
                from_state="extraction_approved",
                to_state=case.workflow_state,
                actor_type="system",
                actor_id="AGN1",
                payload=json.dumps({"review_id": classification_review.id})
            )
        
        self.session.flush()
    
    def _generate_case_number(self) -> str:
        """Generate unique case number in format CASE-YYYY-NNNNN"""
        year = datetime.now(UTC).year
        
        # Find latest case number for this year
        from sqlalchemy import func, select
        stmt = select(func.max(NeedCase.case_number)).where(
            NeedCase.case_number.like(f"CASE-{year}-%")
        )
        result = self.session.execute(stmt)
        latest = result.scalar()
        
        if latest:
            # Extract sequence number and increment
            seq = int(latest.split("-")[-1]) + 1
        else:
            # First case of the year
            seq = 1
        
        return f"CASE-{year}-{seq:05d}"
    
    def initialize_workflow_state(self, case_id: int) -> NeedCase:
        """
        Initialize workflow state for a new case.
        Sets initial state and next_action based on completeness.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Updated NeedCase with initialized workflow state
        """
        case = self.session.get(NeedCase, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")
        
        # Workflow state already set during case creation
        # This method exists for explicit re-initialization if needed
        return case
    
    def advance_to_extraction(self, case_id: int, actor_id: str = "system") -> NeedCase:
        """
        Advance case to extraction-pending state and trigger AGN1 extraction.
        
        Args:
            case_id: Case identifier
            actor_id: Actor advancing the workflow (default: system)
            
        Returns:
            Updated NeedCase in extraction_pending state
        """
        case = self.session.get(NeedCase, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")
        
        # Get normalized need
        normalized_need = self.session.query(NormalizedNeed).filter_by(case_id=case_id).first()
        if normalized_need is None:
            raise ValueError(f"No normalized need found for case {case_id}")
        
        # Parse normalized fields
        mandatory_fields = json.loads(normalized_need.mandatory_fields)
        sourced_fields = json.loads(normalized_need.sourced_fields)
        derived_fields = json.loads(normalized_need.derived_fields)
        
        normalized_fields = {
            **mandatory_fields,
            **sourced_fields,
            **derived_fields
        }
        
        # Trigger AGN1 extraction (ATS2)
        review = self.agn1_service.extract_attributes(case_id, normalized_fields)
        
        # Update case workflow state
        from_state = case.workflow_state
        case.workflow_state = "extraction_pending"
        case.next_action = "extraction_review_required"
        
        # Record workflow event
        self.audit_service.record_workflow_event(
            case_id=case.id,
            event_type="extraction_initiated",
            from_state=from_state,
            to_state=case.workflow_state,
            actor_type="system",
            actor_id=actor_id,
            payload=json.dumps({"review_id": review.id})
        )
        
        self.session.commit()
        self.session.refresh(case)
        
        return case
