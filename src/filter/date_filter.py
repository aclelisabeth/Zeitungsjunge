"""Date filtering module for articles."""

from datetime import datetime, timedelta
from typing import List
from src.models import Article


class DateFilter:
    """Filters articles by publication date range."""
    
    # Define supported time ranges
    RANGES = {
        'today': 1,
        '7d': 7,
        '30d': 30,
        '60d': 60,
        '90d': 90,
    }
    
    @staticmethod
    def is_valid_range(range_name: str) -> bool:
        """
        Check if a time range is valid.
        
        Args:
            range_name: Time range identifier (e.g., '7d', 'today')
            
        Returns:
            True if valid, False otherwise
        """
        return range_name in DateFilter.RANGES
    
    @staticmethod
    def get_supported_ranges() -> List[str]:
        """
        Get list of supported time ranges.
        
        Returns:
            List of supported range identifiers
        """
        return list(DateFilter.RANGES.keys())
    
    @staticmethod
    def filter_by_range(articles: List[Article], range_name: str) -> List[Article]:
        """
        Filter articles by publication date range.
        
        Args:
            articles: List of Article objects
            range_name: Time range identifier (e.g., '7d', 'today')
            
        Returns:
            Filtered list of articles within the specified range
            
        Raises:
            ValueError: If range_name is not valid
        """
        if not DateFilter.is_valid_range(range_name):
            raise ValueError(f"Invalid date range: {range_name}. Supported: {DateFilter.get_supported_ranges()}")
        
        days = DateFilter.RANGES[range_name]
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        filtered = []
        for article in articles:
            if article.published_date >= cutoff_date:
                filtered.append(article)
        
        return filtered
    
    @staticmethod
    def get_range_description(range_name: str) -> str:
        """
        Get human-readable description of a time range.
        
        Args:
            range_name: Time range identifier
            
        Returns:
            Description string
        """
        descriptions = {
            'today': 'Last 24 hours',
            '7d': 'Last 7 days',
            '30d': 'Last 30 days',
            '60d': 'Last 60 days',
            '90d': 'Last 90 days',
        }
        return descriptions.get(range_name, 'Unknown range')
