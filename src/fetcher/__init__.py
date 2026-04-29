"""Fetcher module for retrieving articles from news sources."""

from src.fetcher.base_fetcher import BaseFetcher
from src.fetcher.rss_fetcher import RSSFetcher
from src.fetcher.api_fetcher import APIFetcher
from src.models import Source, FetchResult


class FetcherFactory:
    """Factory for creating appropriate fetcher instances."""
    
    @staticmethod
    def create_fetcher(source: Source) -> BaseFetcher:
        """
        Create a fetcher instance based on source type.
        
        Args:
            source: Source configuration object
            
        Returns:
            BaseFetcher subclass instance
            
        Raises:
            ValueError: If source type is unsupported
        """
        if source.type == 'rss':
            return RSSFetcher(source)
        elif source.type == 'api':
            return APIFetcher(source)
        else:
            raise ValueError(f"Unsupported source type: {source.type}")


__all__ = ['BaseFetcher', 'RSSFetcher', 'APIFetcher', 'FetcherFactory']
