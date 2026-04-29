"""Data models for the news aggregation application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Article:
    """Represents a single news article."""
    
    title: str
    description: str
    url: str
    source_id: str
    source_name: str
    published_date: datetime
    fetched_date: datetime
    region: str
    category: Optional[str] = None
    content: Optional[str] = None
    
    @property
    def id(self) -> str:
        """Unique ID based on title and source."""
        return f"{self.source_id}:{hash(self.title)}"
    
    def __repr__(self) -> str:
        return f"Article(title='{self.title[:50]}...', source='{self.source_name}')"


@dataclass
class Source:
    """Represents a news source configuration."""
    
    id: str
    name: str
    type: str  # 'rss' or 'api'
    url: str
    credibility_weight: float
    region: str
    enabled: bool
    category: Optional[str] = None
    api_config: Optional[dict] = None
    
    def __repr__(self) -> str:
        return f"Source(id='{self.id}', name='{self.name}', region='{self.region}')"


@dataclass
class RankedArticle:
    """Article with ranking score and metadata."""
    
    article: Article
    score: float
    duplicate_sources: List[str] = field(default_factory=list)
    
    def __lt__(self, other: "RankedArticle") -> bool:
        """For sorting (higher score = more important)."""
        return self.score > other.score
    
    def __repr__(self) -> str:
        sources_str = ", ".join(self.duplicate_sources) if self.duplicate_sources else self.article.source_name
        return f"RankedArticle(score={self.score:.2f}, sources=[{sources_str}])"


@dataclass
class FetchResult:
    """Result of fetching articles from a source."""
    
    source_id: str
    source_name: str
    articles: List[Article]
    error: Optional[str] = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success(self) -> bool:
        """Whether the fetch was successful."""
        return self.error is None and len(self.articles) > 0
