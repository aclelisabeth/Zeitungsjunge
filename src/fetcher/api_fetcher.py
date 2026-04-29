"""Hacker News API fetcher implementation."""

import requests
from datetime import datetime
from typing import List, Optional
from src.models import Article, FetchResult, Source
from src.fetcher.base_fetcher import BaseFetcher


class APIFetcher(BaseFetcher):
    """Fetcher for REST APIs (Hacker News)."""
    
    def fetch(self) -> FetchResult:
        """
        Fetch articles from Hacker News API.
        
        Returns:
            FetchResult object with articles or error
        """
        try:
            api_config = self.source.api_config or {}
            endpoint = api_config.get('endpoint', 'topstories')
            items_per_fetch = api_config.get('items_per_fetch', 30)
            
            # Fetch top story IDs
            url = f"{self.source.url}{endpoint}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            story_ids = response.json()[:items_per_fetch]
            
            # Fetch individual stories
            articles = []
            for story_id in story_ids:
                try:
                    article = self._fetch_story(story_id, api_config)
                    if article:
                        articles.append(article)
                    
                    # Limit articles
                    if len(articles) >= items_per_fetch:
                        break
                except Exception as e:
                    print(f"Warning: Error fetching story {story_id}: {str(e)}")
                    continue
            
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=articles,
                error=None if articles else "No stories fetched"
            )
        
        except requests.exceptions.RequestException as e:
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=[],
                error=f"API request failed: {str(e)}"
            )
        except Exception as e:
            return FetchResult(
                source_id=self.source.id,
                source_name=self.source.name,
                articles=[],
                error=f"Unexpected error: {str(e)}"
            )
    
    def _fetch_story(self, story_id: int, api_config: dict) -> Optional[Article]:
        """
        Fetch a single story from Hacker News.
        
        Args:
            story_id: Hacker News story ID
            api_config: API configuration dict
            
        Returns:
            Article object or None
        """
        try:
            url = f"{self.source.url}item/{story_id}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            story = response.json()
            
            # Filter: only include stories with a URL and reasonable score
            if not story.get('url') or story.get('type') != 'story':
                return None
            
            # Only include stories with at least 5 points (filter spam)
            if story.get('score', 0) < 5:
                return None
            
            title = self._sanitize_title(story.get('title', 'Untitled'))
            url = self._sanitize_url(story.get('url', ''))
            
            if not title or not url:
                return None
            
            # Create description from HN metadata
            description = self._create_hn_description(story)
            
            # Parse date
            published_date = datetime.utcfromtimestamp(story.get('time', 0))
            
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
        
        except Exception as e:
            return None
    
    def _create_hn_description(self, story: dict) -> str:
        """
        Create a description for Hacker News story.
        
        Args:
            story: Story data from HN API
            
        Returns:
            Description string
        """
        parts = []
        
        score = story.get('score', 0)
        comments = story.get('descendants', 0)
        
        parts.append(f"Score: {score} | Comments: {comments}")
        
        if story.get('text'):
            text = self._sanitize_description(story['text'])
            if text:
                parts.append(text)
        
        return " | ".join(parts)
