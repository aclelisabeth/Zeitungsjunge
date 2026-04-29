"""Bookmarks API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.schemas.schemas import ArticleResponse, PaginatedResponse
from backend.app.services.bookmark_service import BookmarkService
from backend.app.utils.security import get_current_user
from backend.app.db.database import get_db

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("/{article_id}", response_model=ArticleResponse)
def add_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add article to bookmarks."""
    article = BookmarkService.add_bookmark(
        db,
        current_user["user_id"],
        article_id
    )
    
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove article from bookmarks."""
    BookmarkService.remove_bookmark(
        db,
        current_user["user_id"],
        article_id
    )


@router.get("/", response_model=PaginatedResponse)
def get_bookmarks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's bookmarked articles."""
    bookmarks, total = BookmarkService.get_user_bookmarks(
        db,
        current_user["user_id"],
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [ArticleResponse.from_orm(b) for b in bookmarks]
    }


@router.get("/check/{article_id}", response_model=dict)
def check_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check if article is bookmarked."""
    is_bookmarked = BookmarkService.is_bookmarked(
        db,
        current_user["user_id"],
        article_id
    )
    
    return {"article_id": article_id, "is_bookmarked": is_bookmarked}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_bookmarks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clear all bookmarks."""
    BookmarkService.clear_bookmarks(db, current_user["user_id"])
