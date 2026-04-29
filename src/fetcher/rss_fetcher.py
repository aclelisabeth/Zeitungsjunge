"""RSS feed fetcher implementation."""

import feedparser
import requests
from datetime import datetime
from typing import List, Optional
from src.models import Article, FetchResult, Source
from src.fetcher.base_fetcher import BaseFetcher


class RSSFetcher(BaseFetcher):
    """Fetcher for RSS/Atom feeds."""
    
    def fetch(self) -> FetchResult:
        """
        Fetch articles from RSS feed.
        
        Returns:
            FetchResult object with articles or error
        """
        try:
            # Fetch feed with timeout
            response = requests.get(
                self.source.url,
                timeout=self.timeout,
                headers={'User-Agent': 'Zeitungsjunge/1.0 (+https://github.com/anomalyco/opencode)'}
            )
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo and not feed.entries:
                return FetchResult(
                    source_id=self.source.id,
                    source_name=self.source.name,
                    articles=[],
                    error=f"Failed to parse RSS feed: {feed.bozo_exception}"
                )
            
            articles = []
            
            for entry in feed.entries[:30]:  # Limit to 30 entries per feed
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    # Log error but continue processing other entries
                    print(f"Warning: Error parsing entry from {self.source.name}: {str(e)}")
                    continue
            
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=articles,
                error=None if articles else "No entries found in feed"
            )
        
        except requests.exceptions.RequestException as e:
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=[],
                error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=[],
                error=f"Unexpected error: {str(e)}"
            )
    
    def _parse_entry(self, entry) -> Optional[Article]:
        """
        Parse a single RSS entry into an Article object.
        
        Args:
            entry: Parsed RSS entry from feedparser
            
        Returns:
            Article object or None if parsing fails
        """
        # Extract and sanitize fields
        title = self._sanitize_title(entry.get('title', 'Untitled'))
        url = self._sanitize_url(entry.get('link', ''))
        description = self._sanitize_description(entry.get('summary', ''))
        
        # Parse publication date
        published_date = self._parse_date(entry)
        
        if not title or not url:
            return None
        
        return Article(
            title=title,
            description=description,
            url=url,
            source_id=self.source.id,
            source_name=self.source.name,
            published_date=published_date,
            fetched_date=datetime.utcnow(),
            region=self.source.region,
            category=self.source.category
        )
    
    def _parse_date(self, entry) -> datetime:
        """
        Parse publication date from RSS entry.
        
        Args:
            entry: Parsed RSS entry
            
        Returns:
            datetime object or current UTC time if parsing fails
        """
        # Try different date fields in order of preference
        date_fields = [
            entry.get('published_parsed'),
            entry.get('updated_parsed'),
        ]
        
        for date_tuple in date_fields:
            if date_tuple:
                try:
                    return datetime(*date_tuple[:6])
                except (TypeError, ValueError):
                    continue
        
        # Fallback to current time if no valid date found
        return datetime.utcnow()
