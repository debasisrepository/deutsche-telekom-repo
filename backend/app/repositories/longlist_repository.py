"""Longlist Repository - Data access for longlist proposals and suppliers."""
from sqlalchemy.orm import Session

from app.models.longlist_proposal import LonglistProposal
from app.models.proposal_supplier import ProposalSupplier


class LonglistRepository:
    """Repository for longlist proposal data access."""

    def __init__(self, session: Session):
        self.session = session

    def create_proposal(
        self,
        case_id: int,
        version_no: int,
        proposal_status: str,
        generation_inputs: str | None = None,
        generated_by_agent_run_id: str | None = None,
        requirement_tags: str | None = None
    ) -> LonglistProposal:
        """Create longlist proposal.
        
        Args:
            case_id: Case identifier
            version_no: Proposal version number
            proposal_status: Proposal status (e.g., draft, finalized)
            generation_inputs: JSON string of generation inputs
            generated_by_agent_run_id: Agent run identifier
            requirement_tags: Requirement tags
            
        Returns:
            LonglistProposal instance
        """
        proposal = LonglistProposal(
            case_id=case_id,
            version_no=version_no,
            proposal_status=proposal_status,
            generation_inputs=generation_inputs,
            generated_by_agent_run_id=generated_by_agent_run_id,
            requirement_tags=requirement_tags
        )
        self.session.add(proposal)
        self.session.flush()
        return proposal

    def create_proposal_supplier(
        self,
        proposal_id: int,
        supplier_id: int,
        rank_position: int,
        recommendation_status: str,
        ranking_score: float,
        citation_complete: bool,
        requirement_tags: str | None = None
    ) -> ProposalSupplier:
        """Create proposal supplier record.
        
        Args:
            proposal_id: Proposal identifier
            supplier_id: Supplier identifier
            rank_position: Rank position in proposal
            recommendation_status: Recommendation status (e.g., recommended)
            ranking_score: Numerical ranking score
            citation_complete: Whether supplier has complete citations
            requirement_tags: Requirement tags
            
        Returns:
            ProposalSupplier instance
        """
        proposal_supplier = ProposalSupplier(
            proposal_id=proposal_id,
            supplier_id=supplier_id,
            rank_position=rank_position,
            recommendation_status=recommendation_status,
            ranking_score=ranking_score,
            citation_complete=citation_complete,
            requirement_tags=requirement_tags
        )
        self.session.add(proposal_supplier)
        self.session.flush()
        return proposal_supplier

    def get_proposal_by_id(self, proposal_id: int) -> LonglistProposal | None:
        """Get proposal by ID.
        
        Args:
            proposal_id: Proposal identifier
            
        Returns:
            LonglistProposal instance or None
        """
        return self.session.query(LonglistProposal).filter_by(id=proposal_id).first()

    def list_case_proposals(self, case_id: int) -> list[LonglistProposal]:
        """List all proposals for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of LonglistProposal instances
        """
        return self.session.query(LonglistProposal).filter_by(case_id=case_id).order_by(
            LonglistProposal.version_no.desc()
        ).all()

    def get_proposal_suppliers(self, proposal_id: int) -> list[ProposalSupplier]:
        """Get all suppliers for a proposal, ordered by rank.
        
        Args:
            proposal_id: Proposal identifier
            
        Returns:
            List of ProposalSupplier instances ordered by rank_position
        """
        return self.session.query(ProposalSupplier).filter_by(
            proposal_id=proposal_id
        ).order_by(ProposalSupplier.rank_position).all()
