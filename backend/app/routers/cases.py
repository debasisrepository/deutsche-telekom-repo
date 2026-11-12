"""Cases Router - Case intake and retrieval endpoints"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.schemas.case_schemas import (
    CaseDetail,
    CaseListItem,
    CaseListResponse,
    CreateCaseRequest,
)
from app.services.workflow.orchestrator_service import WorkflowOrchestratorService

router = APIRouter()


@router.post("", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case(
    request: CreateCaseRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new case from intake submission.
    Performs multi-channel intake capture and normalization (FR-001, FR-002).
    """
    # Build raw content from request
    raw_content = {
        "title": request.title,
        "business_unit": request.business_unit,
        "description": request.description,
        "artifact_type": request.artifact_type,
        "artifact_ref": request.artifact_ref,
        "submitted_via": request.submitted_via
    }
    
    # Create case via workflow orchestrator
    orchestrator = WorkflowOrchestratorService(db)
    case = orchestrator.create_case_from_intake(
        channel=request.channel,
        raw_content=raw_content,
        created_by_user_id=current_user.id
    )
    
    # Fetch with relations for response
    case_repo = CaseRepository(db)
    case_with_relations = case_repo.get_with_relations(case.id)
    
    if case_with_relations is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created case"
        )
    
    return CaseDetail.model_validate(case_with_relations)


@router.get("/{caseId}", response_model=CaseDetail)
def get_case(
    caseId: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retrieve case details by ID.
    Returns case with normalized need and source artifacts (FR-003).
    """
    case_repo = CaseRepository(db)
    case = case_repo.get_with_relations(caseId)
    
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return CaseDetail.model_validate(case)


@router.get("", response_model=CaseListResponse)
def list_cases(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = 1,
    page_size: int = 20,
    workflow_state: str | None = None
):
    """
    List cases with pagination and optional workflow state filter.
    Supports filtering by workflow_state query parameter (FR-003).
    """
    case_repo = CaseRepository(db)
    
    offset = (page - 1) * page_size
    
    if workflow_state is not None:
        # Filter by workflow state
        cases = case_repo.get_by_workflow_state(
            workflow_state=workflow_state,
            limit=page_size,
            offset=offset
        )
        total = case_repo.count_by_workflow_state(workflow_state)
    else:
        # No filter - get all
        cases = case_repo.get_all(limit=page_size, offset=offset)
        total = case_repo.count_all()
    
    return CaseListResponse(
        items=[CaseListItem.model_validate(case) for case in cases],
        total=total,
        page=page,
        page_size=page_size
    )
