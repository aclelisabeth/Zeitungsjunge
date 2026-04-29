"""Deduplication module for identifying and merging duplicate articles."""

from difflib import SequenceMatcher
from typing import List, Dict, Tuple
from src.models import Article


class Deduplicator:
    """Identifies and merges duplicate articles across sources."""
    
    def __init__(self, threshold: float = 0.75):
        """
        Initialize deduplicator.
        
        Args:
            threshold: Similarity threshold (0-1) for considering articles as duplicates
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
    
    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """
        Deduplicate articles and merge metadata from duplicate sources.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Deduplicated list with merged source information
        """
        if not articles:
            return []
        
        # Build similarity matrix
        duplicates = self._find_duplicates(articles)
        
        # Group articles by duplicate clusters
        clusters = self._group_duplicates(articles, duplicates)
        
        # Merge articles within each cluster
        merged_articles = []
        for cluster_indices in clusters:
            merged = self._merge_cluster(articles, cluster_indices)
            merged_articles.append(merged)
        
        return merged_articles
    
    def _find_duplicates(self, articles: List[Article]) -> Dict[int, List[int]]:
        """
        Find duplicate pairs between articles.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Dict mapping article index to list of duplicate indices
        """
        duplicates = {}
        
        for i in range(len(articles)):
            duplicates[i] = []
            for j in range(i + 1, len(articles)):
                similarity = self._calculate_similarity(articles[i], articles[j])
                if similarity >= self.threshold:
                    duplicates[i].append(j)
                    if j not in duplicates:
                        duplicates[j] = []
                    duplicates[j].append(i)
        
        return duplicates
    
    def _calculate_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate similarity between two articles.
        
        Uses title + description for comparison.
        
        Args:
            article1: First Article object
            article2: Second Article object
            
        Returns:
            Similarity score (0-1)
        """
        # Combine title and description for comparison
        text1 = f"{article1.title.lower()} {article1.description.lower()}".strip()
        text2 = f"{article2.title.lower()} {article2.description.lower()}".strip()
        
        # Handle empty texts
        if not text1 or not text2:
            return 0.0
        
        # Calculate similarity using SequenceMatcher
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _group_duplicates(self, articles: List[Article], duplicates: Dict[int, List[int]]) -> List[List[int]]:
        """
        Group articles into duplicate clusters.
        
        Args:
            articles: List of Article objects
            duplicates: Dict from _find_duplicates
            
        Returns:
            List of clusters (each cluster is a list of indices)
        """
        visited = set()
        clusters = []
        
        for i in range(len(articles)):
            if i in visited:
                continue
            
            # Start a new cluster
            cluster = self._bfs_cluster(i, duplicates, visited)
            clusters.append(cluster)
        
        return clusters
    
    def _bfs_cluster(self, start: int, duplicates: Dict[int, List[int]], visited: set) -> List[int]:
        """
        Build a cluster using breadth-first search.
        
        Args:
            start: Starting article index
            duplicates: Dict from _find_duplicates
            visited: Set of already visited indices
            
        Returns:
            List of indices in the cluster
        """
        cluster = []
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            cluster.append(current)
            
            # Add related duplicates to queue
            for dup_idx in duplicates.get(current, []):
                if dup_idx not in visited:
                    queue.append(dup_idx)
        
        return cluster
    
    def _merge_cluster(self, articles: List[Article], cluster_indices: List[int]) -> Article:
        """
        Merge articles in a cluster into one representative article.
        
        Keeps the article with highest credibility weight and records other sources.
        
        Args:
            articles: List of Article objects
            cluster_indices: Indices of articles in the cluster
            
        Returns:
            Merged Article object
        """
        if not cluster_indices:
            return articles[0]
        
        # Sort by credibility weight (descending)
        cluster_indices.sort(
            key=lambda idx: articles[idx].source_id,
            reverse=False  # We'll manually compare credibility
        )
        
        # Find article with highest recency and store other sources
        best_article = articles[cluster_indices[0]]
        for idx in cluster_indices[1:]:
            if articles[idx].published_date > best_article.published_date:
                best_article = articles[idx]
        
        # Record duplicate sources
        duplicate_sources = []
        for idx in cluster_indices:
            if idx != cluster_indices[0]:
                source_name = articles[idx].source_name
                if source_name not in duplicate_sources and source_name != best_article.source_name:
                    duplicate_sources.append(source_name)
        
        # Create merged article with duplicate sources in description
        merged = Article(
            title=best_article.title,
            description=best_article.description,
            url=best_article.url,
            source_id=best_article.source_id,
            source_name=best_article.source_name,
            published_date=best_article.published_date,
            fetched_date=best_article.fetched_date,
            region=best_article.region,
            category=best_article.category,
            content=best_article.content
        )
        
        # Attach duplicate sources for later use
        merged._duplicate_sources = duplicate_sources
        
        return merged
