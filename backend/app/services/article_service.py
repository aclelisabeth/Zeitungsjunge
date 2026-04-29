"""Article and news source management service."""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status
from backend.app.models.models import Article, NewsSource, User
from backend.app.schemas.schemas import ArticleCreate
from typing import List, Optional
from datetime import datetime, timedelta


class ArticleService:
    """Service for article management operations."""

    @staticmethod
    def create_article(db: Session, article_data: ArticleCreate) -> Article:
        """Create a new article."""
        # Check if article already exists
        existing = db.query(Article).filter(Article.url == article_data.url).first()
        if existing:
            return existing
        
        db_article = Article(**article_data.dict())
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article

    @staticmethod
    def get_article_by_id(db: Session, article_id: int) -> Optional[Article]:
        """Get article by ID."""
        return db.query(Article).filter(Article.id == article_id).first()

    @staticmethod
    def get_articles_by_time_range(
        db: Session,
        days: int = 1,
        region: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Article], int]:
        """Get articles within a time range."""
        query = db.query(Article)
        
        # Filter by date
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Article.published_at >= since)
        
        # Filter by region
        if region and region != "global":
            query = query.filter(Article.region == region)
        
        # Count total
        total = query.count()
        
        # Order by importance and date
        query = query.order_by(
            desc(Article.importance_score),
            desc(Article.published_at)
        )
        
        articles = query.offset(offset).limit(limit).all()
        return articles, total

    @staticmethod
    def search_articles(
        db: Session,
        query_text: str,
        region: Optional[str] = None,
        days: int = 30,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Article], int]:
        """Search articles by title, description, or keywords."""
        query = db.query(Article)
        
        # Full-text search
        search_term = f"%{query_text}%"
        query = query.filter(
            (Article.title.ilike(search_term)) |
            (Article.description.ilike(search_term)) |
            (Article.keywords.ilike(search_term))
        )
        
        # Filter by date
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Article.published_at >= since)
        
        # Filter by region
        if region and region != "global":
            query = query.filter(Article.region == region)
        
        # Count total
        total = query.count()
        
        # Order by importance
        query = query.order_by(
            desc(Article.importance_score),
            desc(Article.published_at)
        )
        
        articles = query.offset(offset).limit(limit).all()
        return articles, total

    @staticmethod
    def update_article_summary(db: Session, article_id: int, summary: str) -> Article:
        """Update article summary."""
        article = ArticleService.get_article_by_id(db, article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        article.summary = summary
        article.summary_generated_at = datetime.utcnow()
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def update_article_score(db: Session, article_id: int, score: float) -> Article:
        """Update article importance score."""
        article = ArticleService.get_article_by_id(db, article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        article.importance_score = score
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def get_trending_articles(
        db: Session,
        days: int = 7,
        limit: int = 20
    ) -> List[Article]:
        """Get trending articles based on frequency and recency."""
        since = datetime.utcnow() - timedelta(days=days)
        
        articles = db.query(Article).filter(
            Article.published_at >= since
        ).order_by(
            desc(Article.importance_score),
            desc(Article.frequency_count),
            desc(Article.published_at)
        ).limit(limit).all()
        
        return articles


class NewsSourceService:
    """Service for news source management."""

    @staticmethod
    def create_news_source(db: Session, source_data: dict) -> NewsSource:
        """Create a new news source."""
        # Check if source already exists
        existing = db.query(NewsSource).filter(
            NewsSource.url == source_data["url"]
        ).first()
        
        if existing:
            return existing
        
        db_source = NewsSource(**source_data)
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        return db_source

    @staticmethod
    def get_news_source(db: Session, source_id: int) -> Optional[NewsSource]:
        """Get news source by ID."""
        return db.query(NewsSource).filter(NewsSource.id == source_id).first()

    @staticmethod
    def get_active_sources(db: Session) -> List[NewsSource]:
        """Get all active news sources."""
        return db.query(NewsSource).filter(NewsSource.is_active == True).all()

    @staticmethod
    def get_sources_by_region(db: Session, region: str) -> List[NewsSource]:
        """Get news sources by region."""
        return db.query(NewsSource).filter(
            (NewsSource.region == region) | (NewsSource.region == "global"),
            NewsSource.is_active == True
        ).all()

    @staticmethod
    def update_news_source(db: Session, source_id: int, update_data: dict) -> NewsSource:
        """Update news source."""
        source = NewsSourceService.get_news_source(db, source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News source not found"
            )
        
        for key, value in update_data.items():
            if hasattr(source, key):
                setattr(source, key, value)
        
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def delete_news_source(db: Session, source_id: int) -> bool:
        """Deactivate news source."""
        source = NewsSourceService.get_news_source(db, source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News source not found"
            )
        
        source.is_active = False
        db.commit()
        return True
