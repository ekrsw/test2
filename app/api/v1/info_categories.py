from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.info_category import InfoCategoryCreate, InfoCategoryUpdate, InfoCategoryResponse
from app.models.info_category import InfoCategory
from app.models.user import User
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=InfoCategoryResponse)
async def create_info_category(
    category_data: InfoCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new info category (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create info categories"
        )
    
    db_category = InfoCategory(
        name=category_data.name,
        description=category_data.description
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

@router.get("/", response_model=List[InfoCategoryResponse])
async def get_info_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all info categories"""
    categories = db.query(InfoCategory).all()
    return categories

@router.get("/{category_id}", response_model=InfoCategoryResponse)
async def get_info_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get info category by ID"""
    category = db.query(InfoCategory).filter(InfoCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Info category not found"
        )
    
    return category

@router.put("/{category_id}", response_model=InfoCategoryResponse)
async def update_info_category(
    category_id: UUID,
    category_data: InfoCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update info category (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update info categories"
        )
    
    category = db.query(InfoCategory).filter(InfoCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Info category not found"
        )
    
    # Update fields
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}")
async def delete_info_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete info category (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete info categories"
        )
    
    category = db.query(InfoCategory).filter(InfoCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Info category not found"
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Info category deleted successfully"}