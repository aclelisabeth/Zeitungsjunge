"""Base fetcher class for news sources."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import Article, FetchResult, Source
from datetime import datetime


class BaseFetcher(ABC):
    """Abstract base class for fetching articles from news sources."""
    
    def __init__(self, source: Source, timeout: int = 10):
        """
        Initialize fetcher with a source configuration.
        
        Args:
            source: Source configuration object
            timeout: Request timeout in seconds
        """
        self.source = source
        self.timeout = timeout
    
    @abstractmethod
    def fetch(self) -> FetchResult:
        """
        Fetch articles from the source.
        
        Returns:
            FetchResult object with articles or error
        """
        pass
    
    def _sanitize_description(self, text: Optional[str]) -> str:
        """
        Clean and sanitize description text.
        
        Args:
            text: Raw description text
            
        Returns:
            Sanitized description text
        """
        if not text:
            return ""
        
        # Remove HTML tags and special characters
        import re
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'&[a-z]+;', '', text)  # Remove HTML entities
        text = text.strip()
        
        # Limit to first 500 characters
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text
    
    def _sanitize_url(self, url: Optional[str]) -> str:
        """
        Validate and sanitize URL.
        
        Args:
            url: URL string
            
        Returns:
            Sanitized URL or empty string
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Only allow HTTP/HTTPS URLs
        if not url.startswith(('http://', 'https://')):
            return ""
        
        # Validate URL length (prevent DoS)
        if len(url) > 2048:
            return ""
        
        return url
    
    def _sanitize_title(self, text: Optional[str]) -> str:
        """
        Sanitize title text.
        
        Args:
            text: Raw title text
            
        Returns:
            Sanitized title text
        """
        if not text:
            return "Untitled"
        
        text = text.strip()
        
        # Limit to 300 characters
        if len(text) > 300:
            text = text[:297] + "..."
        
        return text
