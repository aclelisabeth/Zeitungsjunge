"""Bookmark and user interaction service."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from backend.app.models.models import User, Article
from typing import List


class BookmarkService:
    """Service for bookmark management."""

    @staticmethod
    def add_bookmark(db: Session, user_id: int, article_id: int) -> Article:
        """Add article to user's bookmarks."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        if article not in user.bookmarks:
            user.bookmarks.append(article)
            db.commit()
        
        return article

    @staticmethod
    def remove_bookmark(db: Session, user_id: int, article_id: int) -> bool:
        """Remove article from user's bookmarks."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        if article in user.bookmarks:
            user.bookmarks.remove(article)
            db.commit()
        
        return True

    @staticmethod
    def get_user_bookmarks(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Article], int]:
        """Get all bookmarks for a user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Count total bookmarks
        total = len(user.bookmarks)
        
        # Get paginated bookmarks sorted by latest first
        bookmarks = sorted(
            user.bookmarks,
            key=lambda a: a.published_at or a.fetched_at,
            reverse=True
        )[offset:offset + limit]
        
        return bookmarks, total

    @staticmethod
    def is_bookmarked(db: Session, user_id: int, article_id: int) -> bool:
        """Check if article is bookmarked by user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False
        
        return article in user.bookmarks

    @staticmethod
    def clear_bookmarks(db: Session, user_id: int) -> bool:
        """Clear all bookmarks for a user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.bookmarks.clear()
        db.commit()
        return True
