"""Cache management module for storing fetched and ranked articles."""

import json
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.models import Article, RankedArticle


class CacheManager:
    """Manages file-based caching of articles."""
    
    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 6):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Cache time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_hours * 3600
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, date_range: str) -> str:
        """
        Generate cache key based on date range and current date.
        
        Args:
            date_range: Time range identifier (e.g., '7d', 'today')
            
        Returns:
            Cache key string
        """
        today = datetime.utcnow().strftime('%Y-%m-%d')
        return f"{date_range}_{today}"
    
    def get_cache_path(self, date_range: str) -> Path:
        """
        Get full path to cache file.
        
        Args:
            date_range: Time range identifier
            
        Returns:
            Path object to cache file
        """
        cache_key = self.get_cache_key(date_range)
        return self.cache_dir / f"{cache_key}.json"
    
    def is_cache_valid(self, date_range: str) -> bool:
        """
        Check if cache exists and is still valid (within TTL).
        
        Args:
            date_range: Time range identifier
            
        Returns:
            True if cache is valid, False otherwise
        """
        cache_path = self.get_cache_path(date_range)
        
        if not cache_path.exists():
            return False
        
        # Check if cache is within TTL
        file_mtime = cache_path.stat().st_mtime
        current_time = time.time()
        age_seconds = current_time - file_mtime
        
        return age_seconds < self.ttl_seconds
    
    def load_cache(self, date_range: str) -> Optional[List[dict]]:
        """
        Load articles from cache.
        
        Args:
            date_range: Time range identifier
            
        Returns:
            List of article dicts or None if cache invalid
        """
        if not self.is_cache_valid(date_range):
            return None
        
        try:
            cache_path = self.get_cache_path(date_range)
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('articles', [])
        except Exception as e:
            print(f"Warning: Error reading cache: {str(e)}")
            return None
    
    def save_cache(self, date_range: str, articles: List[RankedArticle]) -> bool:
        """
        Save ranked articles to cache.
        
        Args:
            date_range: Time range identifier
            articles: List of RankedArticle objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_path = self.get_cache_path(date_range)
            
            # Serialize articles
            articles_data = []
            for ranked in articles:
                article_dict = self._serialize_article(ranked.article)
                article_dict['score'] = ranked.score
                article_dict['duplicate_sources'] = ranked.duplicate_sources
                articles_data.append(article_dict)
            
            # Write to cache
            cache_data = {
                'articles': articles_data,
                'timestamp': datetime.utcnow().isoformat(),
                'date_range': date_range,
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Warning: Error saving cache: {str(e)}")
            return False
    
    def clear_cache(self, date_range: Optional[str] = None) -> int:
        """
        Clear cache files.
        
        Args:
            date_range: Specific range to clear, or None to clear all
            
        Returns:
            Number of cache files removed
        """
        count = 0
        
        if date_range:
            cache_path = self.get_cache_path(date_range)
            if cache_path.exists():
                cache_path.unlink()
                count = 1
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
        
        return count
    
    def _serialize_article(self, article: Article) -> dict:
        """
        Convert Article object to dictionary for JSON serialization.
        
        Args:
            article: Article object
            
        Returns:
            Dictionary representation of article
        """
        return {
            'title': article.title,
            'description': article.description,
            'url': article.url,
            'source_id': article.source_id,
            'source_name': article.source_name,
            'published_date': article.published_date.isoformat(),
            'fetched_date': article.fetched_date.isoformat(),
            'region': article.region,
            'category': article.category,
        }
    
    def _deserialize_article(self, data: dict) -> Article:
        """
        Convert dictionary back to Article object.
        
        Args:
            data: Dictionary representation of article
            
        Returns:
            Article object
        """
        return Article(
            title=data['title'],
            description=data['description'],
            url=data['url'],
            source_id=data['source_id'],
            source_name=data['source_name'],
            published_date=datetime.fromisoformat(data['published_date']),
            fetched_date=datetime.fromisoformat(data['fetched_date']),
            region=data['region'],
            category=data.get('category'),
        )
