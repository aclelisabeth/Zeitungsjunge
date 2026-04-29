"""Database models for Zeitungsjunge Phase 2."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from backend.app.db.database import Base


# Association table for many-to-many relationship between users and articles (bookmarks)
user_bookmarks = Table(
    'user_bookmarks',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
)


class User(Base):
    """User model for authentication and preferences."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bookmarks = relationship("Article", secondary=user_bookmarks, back_populates="bookmarked_by")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    email_subscriptions = relationship("EmailSubscription", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    """User preferences for news filtering and display."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    preferred_regions = Column(String(255), default="global")  # Comma-separated: us,de,eu,global
    preferred_languages = Column(String(255), default="en,de")
    articles_per_page = Column(Integer, default=15)
    default_time_range = Column(String(50), default="today")  # today, 7d, 30d, 60d, 90d
    theme = Column(String(20), default="light")  # light, dark
    enable_notifications = Column(Boolean, default=True)
    similarity_threshold = Column(Float, default=0.75)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")


class NewsSource(Base):
    """News source configuration."""

    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    feed_type = Column(String(20), nullable=False)  # rss, api
    region = Column(String(50), nullable=False)  # us, de, eu, global
    credibility_score = Column(Float, default=0.5)  # 0-1
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")


class Article(Base):
    """Cached news article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('news_sources.id'), nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(512), unique=True, nullable=False, index=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # AI-generated summary
    summary = Column(Text, nullable=True)
    summary_generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Ranking
    importance_score = Column(Float, default=0.0)
    frequency_count = Column(Integer, default=1)
    
    # Metadata
    image_url = Column(String(512), nullable=True)
    keywords = Column(String(512), nullable=True)  # Comma-separated
    region = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    source = relationship("NewsSource", back_populates="articles")
    bookmarked_by = relationship("User", secondary=user_bookmarks, back_populates="bookmarks")


class SearchHistory(Base):
    """User search history for analytics."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query = Column(String(512), nullable=False)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="search_history")


class EmailSubscription(Base):
    """Email digest subscription settings."""

    __tablename__ = "email_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    frequency = Column(String(50), nullable=False)  # daily, weekly, never
    time_of_day = Column(String(10), default="09:00")  # HH:MM format
    regions = Column(String(255), default="global")  # Comma-separated
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="email_subscriptions")
