"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= User Preference Schemas =============

class UserPreferenceBase(BaseModel):
    """Base user preference schema."""
    preferred_regions: str = "global"
    preferred_languages: str = "en,de"
    articles_per_page: int = 15
    default_time_range: str = "today"
    theme: str = "light"
    enable_notifications: bool = True
    similarity_threshold: float = 0.75


class UserPreferenceCreate(UserPreferenceBase):
    """User preference creation schema."""
    pass


class UserPreferenceResponse(UserPreferenceBase):
    """User preference response schema."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Article Schemas =============

class ArticleBase(BaseModel):
    """Base article schema."""
    title: str
    description: Optional[str] = None
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """Article creation schema."""
    source_id: int
    content: Optional[str] = None
    image_url: Optional[str] = None
    keywords: Optional[str] = None
    region: str = "global"
    language: str = "en"


class ArticleResponse(ArticleBase):
    """Article response schema."""
    id: int
    source_id: int
    summary: Optional[str] = None
    importance_score: float
    frequency_count: int
    image_url: Optional[str] = None
    keywords: Optional[str] = None
    region: str
    language: str
    fetched_at: datetime
    
    class Config:
        from_attributes = True


class ArticleDetailResponse(ArticleResponse):
    """Detailed article response with full content."""
    content: Optional[str] = None
    summary_generated_at: Optional[datetime] = None


# ============= News Source Schemas =============

class NewsSourceBase(BaseModel):
    """Base news source schema."""
    name: str
    url: str
    feed_type: str
    region: str
    credibility_score: float = 0.5
    is_active: bool = True


class NewsSourceCreate(NewsSourceBase):
    """News source creation schema."""
    pass


class NewsSourceResponse(NewsSourceBase):
    """News source response schema."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Search Schemas =============

class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=512)
    region: Optional[str] = None
    time_range: Optional[str] = None  # today, 7d, 30d, 60d, 90d
    language: Optional[str] = None
    limit: int = 20
    offset: int = 0


class SearchResponse(BaseModel):
    """Search response schema."""
    total: int
    results: List[ArticleResponse]
    query: str


# ============= Email Subscription Schemas =============

class EmailSubscriptionBase(BaseModel):
    """Base email subscription schema."""
    frequency: str  # daily, weekly, never
    time_of_day: str = "09:00"
    regions: str = "global"
    is_active: bool = True


class EmailSubscriptionCreate(EmailSubscriptionBase):
    """Email subscription creation schema."""
    pass


class EmailSubscriptionResponse(EmailSubscriptionBase):
    """Email subscription response schema."""
    id: int
    user_id: int
    last_sent_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Authentication Schemas =============

class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


# ============= Bookmark Schemas =============

class BookmarkResponse(BaseModel):
    """Bookmark response schema."""
    id: int
    user_id: int
    article_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Paginated Response =============

class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""
    total: int
    limit: int
    offset: int
    items: List[dict]
