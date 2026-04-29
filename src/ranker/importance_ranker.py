"""Importance ranking module for articles."""

from datetime import datetime, timedelta
from typing import List, Optional
from src.models import Article, RankedArticle


class ImportanceRanker:
    """Ranks articles by importance using multiple scoring factors."""
    
    def __init__(self, weights: dict = None, top_n: int = 15):
        """
        Initialize ranker with scoring weights.
        
        Args:
            weights: Dict with 'frequency', 'recency', 'credibility' weights
            top_n: Number of top articles to return
        """
        self.weights = weights or {
            'frequency': 0.4,
            'recency': 0.3,
            'credibility': 0.3,
        }
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.top_n = max(1, top_n)
    
    def rank(self, articles: List[Article]) -> List[RankedArticle]:
        """
        Rank articles and return top N.
        
        Args:
            articles: List of Article objects
            
        Returns:
            List of RankedArticle objects, sorted by score (highest first)
        """
        if not articles:
            return []
        
        # Calculate scores
        ranked = []
        for article in articles:
            score = self._calculate_score(article, articles)
            ranked_article = RankedArticle(
                article=article,
                score=score,
                duplicate_sources=getattr(article, '_duplicate_sources', [])
            )
            ranked.append(ranked_article)
        
        # Sort by score (highest first)
        ranked.sort(key=lambda x: x.score, reverse=True)
        
        # Return top N
        return ranked[:self.top_n]
    
    def _calculate_score(self, article: Article, all_articles: List[Article]) -> float:
        """
        Calculate importance score for an article.
        
        Score = (frequency × 0.4) + (recency × 0.3) + (credibility × 0.3)
        
        Args:
            article: Article to score
            all_articles: All articles (for frequency calculation)
            
        Returns:
            Score between 0 and 100
        """
        freq_score = self._frequency_score(article, all_articles)
        recency_score = self._recency_score(article)
        credibility_score = self._credibility_score(article)
        
        total_score = (
            (freq_score * self.weights['frequency']) +
            (recency_score * self.weights['recency']) +
            (credibility_score * self.weights['credibility'])
        )
        
        return total_score
    
    def _frequency_score(self, article: Article, all_articles: List[Article]) -> float:
        """
        Calculate frequency score (how many sources report similar story).
        
        Args:
            article: Article to score
            all_articles: All articles to check against
            
        Returns:
            Score between 0 and 100
        """
        duplicate_sources = getattr(article, '_duplicate_sources', [])
        
        # Count all sources reporting this story (including primary source)
        total_sources = len(duplicate_sources) + 1
        
        # Get unique sources in all articles
        unique_sources = set(a.source_name for a in all_articles)
        max_sources = len(unique_sources)
        
        # Frequency score: (reported by N sources / max sources) × 100
        if max_sources == 0:
            return 0.0
        
        return min(100.0, (total_sources / max_sources) * 100)
    
    def _recency_score(self, article: Article) -> float:
        """
        Calculate recency score (newer articles score higher).
        
        Args:
            article: Article to score
            
        Returns:
            Score between 0 and 100
        """
        now = datetime.utcnow()
        age = now - article.published_date
        
        # Articles older than 90 days get score 0
        if age > timedelta(days=90):
            return 0.0
        
        # Articles from today get full score, scales linearly
        max_age = timedelta(days=90)
        recency = 1.0 - (age.total_seconds() / max_age.total_seconds())
        
        return max(0.0, recency * 100)
    
    def _credibility_score(self, article: Article) -> float:
        """
        Calculate credibility score based on source weight.
        
        Note: This is a placeholder. In a real implementation, 
        we would need to store source credibility with articles.
        
        Args:
            article: Article to score
            
        Returns:
            Score between 0 and 100
        """
        # Default credibility score (0.8 = 80 out of 100)
        # This would be populated from source config in real implementation
        default_credibility = 0.8
        
        return default_credibility * 100
    
    def filter_by_region(self, articles: List[Article], region: str) -> List[Article]:
        """
        Filter articles by region.
        
        Args:
            articles: List of Article objects
            region: Region filter ('us', 'de', 'eu', 'global')
            
        Returns:
            Filtered list of articles
        """
        if region == 'global':
            return articles
        
        if region == 'eu':
            # EU = all European sources except 'global'
            return [a for a in articles if a.region in ['de', 'eu']]
        
        # Specific region
        return [a for a in articles if a.region == region or a.region == 'global']
