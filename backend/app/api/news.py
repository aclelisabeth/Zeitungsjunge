"""News and articles API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.schemas.schemas import (
    ArticleResponse, SearchRequest, SearchResponse, PaginatedResponse
)
from backend.app.services.article_service import ArticleService
from backend.app.services.summarization_service import summarization_service
from backend.app.utils.security import get_current_user
from backend.app.db.database import get_db

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/", response_model=PaginatedResponse)
def get_news(
    time_range: str = Query("today", pattern="^(today|7d|30d|60d|90d)$"),
    region: Optional[str] = Query(None, pattern="^(us|de|eu|global)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get news articles by time range and region."""
    # Convert time_range to days
    range_mapping = {
        "today": 1,
        "7d": 7,
        "30d": 30,
        "60d": 60,
        "90d": 90
    }
    days = range_mapping.get(time_range, 1)
    
    articles, total = ArticleService.get_articles_by_time_range(
        db,
        days=days,
        region=region,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [ArticleResponse.from_orm(a) for a in articles]
    }


@router.get("/search", response_model=SearchResponse)
def search_news(
    query: str = Query(..., min_length=1, max_length=512),
    region: Optional[str] = Query(None, pattern="^(us|de|eu|global)$"),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search articles by keyword."""
    articles, total = ArticleService.search_articles(
        db,
        query_text=query,
        region=region,
        days=days,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "query": query,
        "results": [ArticleResponse.from_orm(a) for a in articles]
    }


@router.get("/trending", response_model=list[ArticleResponse])
def get_trending_news(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trending articles."""
    articles = ArticleService.get_trending_articles(
        db,
        days=days,
        limit=limit
    )
    
    return [ArticleResponse.from_orm(a) for a in articles]


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get article details by ID."""
    article = ArticleService.get_article_by_id(db, article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return article


@router.post("/{article_id}/summarize", response_model=dict)
def summarize_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI summary for article."""
    article = ArticleService.get_article_by_id(db, article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if summary already exists
    if article.summary:
        return {
            "article_id": article.id,
            "summary": article.summary,
            "already_generated": True
        }
    
    # Generate new summary
    summary = summarization_service.summarize(
        title=article.title,
        description=article.description,
        content=article.content
    )
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Summarization service unavailable"
        )
    
    # Update article with summary
    updated_article = ArticleService.update_article_summary(db, article_id, summary)
    
    return {
        "article_id": updated_article.id,
        "summary": updated_article.summary,
        "already_generated": False
    }
