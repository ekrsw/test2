from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalApprovalRequest, ProposalStatus
from app.models.proposal import Proposal
from app.models.article import Article
from app.models.user import User
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ProposalResponse)
async def create_proposal(
    proposal_data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new proposal"""
    # Get article to determine approval group
    article = db.query(Article).filter(Article.article_id == proposal_data.article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    db_proposal = Proposal(
        user_id=current_user.id,
        article_id=proposal_data.article_id,
        article=proposal_data.article,
        type=proposal_data.type,
        title=proposal_data.title,
        info_category_id=proposal_data.info_category_id,
        keywords=proposal_data.keywords,
        importance=proposal_data.importance,
        published_start=proposal_data.published_start,
        published_end=proposal_data.published_end,
        target=proposal_data.target,
        question=proposal_data.question,
        answer=proposal_data.answer,
        add_comments=proposal_data.add_comments,
        reason=proposal_data.reason,
        approval_group_id=article.approval_group_id
    )
    
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    
    return db_proposal

@router.get("/", response_model=List[ProposalResponse])
async def get_proposals(
    status: Optional[ProposalStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposals based on user role and status"""
    query = db.query(Proposal)
    
    # Filter based on user role
    if current_user.role == "管理者":
        # Admin can see all proposals
        pass
    elif current_user.role == "SV":
        # SV can see proposals for their approval group and their own proposals
        query = query.filter(
            or_(
                Proposal.approval_group_id == current_user.group_id,
                Proposal.user_id == current_user.id
            )
        )
    else:
        # General users can only see their own proposals
        query = query.filter(Proposal.user_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.filter(Proposal.status == status)
    
    proposals = query.all()
    return proposals

@router.get("/pending-approval", response_model=List[ProposalResponse])
async def get_pending_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposals pending approval for SV/Admin"""
    if current_user.role not in ["SV", "管理者"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SV and administrators can view pending approvals"
        )
    
    query = db.query(Proposal).filter(Proposal.status == "申請中")
    
    if current_user.role == "SV":
        # SV can only approve proposals for their group
        query = query.filter(Proposal.approval_group_id == current_user.group_id)
    
    proposals = query.all()
    return proposals

@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal by ID"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check access permissions
    if (current_user.role == "一般ユーザー" and proposal.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    elif (current_user.role == "SV" and 
          proposal.user_id != current_user.id and 
          proposal.approval_group_id != current_user.group_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return proposal

@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: UUID,
    proposal_data: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update proposal (only by creator and only if pending)"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Only creator can update and only if pending
    if proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can update the proposal"
        )
    
    if proposal.status != "申請中":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending proposals can be updated"
        )
    
    # Update fields
    update_data = proposal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proposal, field, value)
    
    db.commit()
    db.refresh(proposal)
    
    return proposal

@router.post("/{proposal_id}/approve", response_model=ProposalResponse)
async def approve_or_reject_proposal(
    proposal_id: UUID,
    approval_data: ProposalApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject proposal (SV/Admin only)"""
    if current_user.role not in ["SV", "管理者"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SV and administrators can approve proposals"
        )
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check if SV can approve this proposal
    if (current_user.role == "SV" and 
        proposal.approval_group_id != current_user.group_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only approve proposals for your group"
        )
    
    # Check if proposal is still pending
    if proposal.status != "申請中":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal is not pending approval"
        )
    
    # Check if user is trying to approve their own proposal
    if proposal.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot approve your own proposal"
        )
    
    # Validate rejection reason
    if approval_data.status == ProposalStatus.REJECTED and not approval_data.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required when rejecting a proposal"
        )
    
    # Update proposal
    proposal.status = approval_data.status
    proposal.approved_by = current_user.id
    proposal.rejection_reason = approval_data.rejection_reason
    
    db.commit()
    db.refresh(proposal)
    
    return proposal

@router.delete("/{proposal_id}")
async def delete_proposal(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete proposal (creator or admin only)"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Only creator or admin can delete
    if proposal.user_id != current_user.id and current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(proposal)
    db.commit()
    
    return {"message": "Proposal deleted successfully"}