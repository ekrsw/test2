from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Dict, List, Optional
from datetime import datetime, date
from uuid import UUID

from app.database import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.models.group import Group
from app.auth import get_current_user

router = APIRouter()

@router.get("/user/monthly-proposals")
async def get_user_monthly_proposals(
    year: int,
    month: int,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly proposal count for a user"""
    target_user_id = user_id if user_id else current_user.id
    
    # Permission check
    if (current_user.role == "一般ユーザー" and target_user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    count = db.query(func.count(Proposal.id)).filter(
        and_(
            Proposal.user_id == target_user_id,
            extract('year', Proposal.created_at) == year,
            extract('month', Proposal.created_at) == month
        )
    ).scalar()
    
    return {"count": count, "year": year, "month": month}

@router.get("/user/approval-rate")
async def get_user_approval_rate(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval rate for a user"""
    target_user_id = user_id if user_id else current_user.id
    
    # Permission check
    if (current_user.role == "一般ユーザー" and target_user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    total_count = db.query(func.count(Proposal.id)).filter(
        Proposal.user_id == target_user_id
    ).scalar()
    
    approved_count = db.query(func.count(Proposal.id)).filter(
        and_(
            Proposal.user_id == target_user_id,
            Proposal.status == "承認済み"
        )
    ).scalar()
    
    approval_rate = (approved_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "total_proposals": total_count,
        "approved_proposals": approved_count,
        "approval_rate": round(approval_rate, 2)
    }

@router.get("/user/proposal-summary")
async def get_user_proposal_summary(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed proposal summary for a user"""
    target_user_id = user_id if user_id else current_user.id
    
    # Permission check
    if (current_user.role == "一般ユーザー" and target_user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get counts by status
    status_counts = db.query(
        Proposal.status,
        func.count(Proposal.id).label('count')
    ).filter(
        Proposal.user_id == target_user_id
    ).group_by(Proposal.status).all()
    
    # Get counts by type
    type_counts = db.query(
        Proposal.type,
        func.count(Proposal.id).label('count')
    ).filter(
        Proposal.user_id == target_user_id
    ).group_by(Proposal.type).all()
    
    # Format results
    status_summary = {status: count for status, count in status_counts}
    type_summary = {proposal_type: count for proposal_type, count in type_counts}
    
    return {
        "status_summary": status_summary,
        "type_summary": type_summary
    }

@router.get("/group/proposal-counts")
async def get_group_proposal_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal counts by group (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view group statistics"
        )
    
    results = db.query(
        Group.name,
        func.count(Proposal.id).label('proposal_count')
    ).outerjoin(
        Proposal, Group.id == Proposal.approval_group_id
    ).group_by(
        Group.id, Group.name
    ).all()
    
    return [{"group_name": name, "proposal_count": count} for name, count in results]

@router.get("/monthly-trends")
async def get_monthly_trends(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly proposal trends (admin/SV only)"""
    if current_user.role == "一般ユーザー":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    query = db.query(
        extract('month', Proposal.created_at).label('month'),
        func.count(Proposal.id).label('count')
    ).filter(
        extract('year', Proposal.created_at) == year
    )
    
    # Filter by group for SV
    if current_user.role == "SV":
        query = query.filter(Proposal.approval_group_id == current_user.group_id)
    
    results = query.group_by(
        extract('month', Proposal.created_at)
    ).order_by(
        extract('month', Proposal.created_at)
    ).all()
    
    # Fill in missing months with 0
    monthly_data = {}
    for month, count in results:
        monthly_data[int(month)] = count
    
    trend_data = []
    for month in range(1, 13):
        trend_data.append({
            "month": month,
            "count": monthly_data.get(month, 0)
        })
    
    return {"year": year, "monthly_trends": trend_data}

@router.get("/approval-statistics")
async def get_approval_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval statistics (admin/SV only)"""
    if current_user.role == "一般ユーザー":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    query = db.query(Proposal)
    
    # Filter by group for SV
    if current_user.role == "SV":
        query = query.filter(Proposal.approval_group_id == current_user.group_id)
    
    total_proposals = query.count()
    pending_proposals = query.filter(Proposal.status == "申請中").count()
    approved_proposals = query.filter(Proposal.status == "承認済み").count()
    rejected_proposals = query.filter(Proposal.status == "却下").count()
    
    approval_rate = (approved_proposals / total_proposals * 100) if total_proposals > 0 else 0
    rejection_rate = (rejected_proposals / total_proposals * 100) if total_proposals > 0 else 0
    
    return {
        "total_proposals": total_proposals,
        "pending_proposals": pending_proposals,
        "approved_proposals": approved_proposals,
        "rejected_proposals": rejected_proposals,
        "approval_rate": round(approval_rate, 2),
        "rejection_rate": round(rejection_rate, 2)
    }