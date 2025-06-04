from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.models.article import Article
from app.models.user import User
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new article (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create articles"
        )
    
    # Check if article_id already exists
    existing_article = db.query(Article).filter(Article.article_id == article_data.article_id).first()
    if existing_article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article ID already exists"
        )
    
    db_article = Article(
        article_id=article_data.article_id,
        article=article_data.article,
        approval_group_id=article_data.approval_group_id
    )
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    return db_article

@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all articles"""
    articles = db.query(Article).all()
    return articles

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get article by article_id"""
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update article (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update articles"
        )
    
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Update fields
    update_data = article_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)
    
    db.commit()
    db.refresh(article)
    
    return article

@router.delete("/{article_id}")
async def delete_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete article (admin only)"""
    if current_user.role != "管理者":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete articles"
        )
    
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    db.delete(article)
    db.commit()
    
    return {"message": "Article deleted successfully"}