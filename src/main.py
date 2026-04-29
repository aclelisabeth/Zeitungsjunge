"""Main CLI entry point for Zeitungsjunge news aggregator."""

import json
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Fix encoding on Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.models import Source, Article, FetchResult
from src.fetcher import FetcherFactory
from src.filter import DateFilter
from src.deduplicator import Deduplicator
from src.ranker import ImportanceRanker
from src.cache import CacheManager
from src.output import MarkdownGenerator


class NewsAggregator:
    """Main news aggregation orchestrator."""
    
    def __init__(self, config_path: str = "config/sources.json"):
        """
        Initialize aggregator with configuration.
        
        Args:
            config_path: Path to sources.json configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.sources = self._load_sources()
        self.cache_manager = CacheManager(
            cache_dir=self.config['cache']['cache_dir'],
            ttl_hours=self.config['cache']['ttl_hours']
        )
        self.ranker = ImportanceRanker(
            weights=self.config['ranking']['weights'],
            top_n=self.config['ranking']['top_articles']
        )
        self.markdown_gen = MarkdownGenerator(
            output_dir=self.config['output']['dir']
        )
    
    def _load_config(self) -> dict:
        """Load configuration from sources.json."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file")
            sys.exit(1)
    
    def _load_sources(self) -> List[Source]:
        """Load and validate sources from configuration."""
        sources = []
        for source_data in self.config['sources']:
            if source_data.get('enabled', True):
                source = Source(
                    id=source_data['id'],
                    name=source_data['name'],
                    type=source_data['type'],
                    url=source_data['url'],
                    credibility_weight=source_data.get('credibility_weight', 0.8),
                    region=source_data.get('region', 'global'),
                    enabled=source_data.get('enabled', True),
                    category=source_data.get('category'),
                    api_config=source_data.get('api_config')
                )
                sources.append(source)
        
        return sources
    
    def fetch_articles(self) -> tuple[List[Article], Dict[str, int]]:
        """
        Fetch articles from all configured sources.
        
        Returns:
            Tuple of (articles list, metadata dict)
        """
        all_articles = []
        metadata = {
            'sources_fetched': 0,
            'sources_failed': 0,
            'articles_fetched': 0,
        }
        
        print(f"Fetching from {len(self.sources)} sources...")
        
        for source in self.sources:
            try:
                fetcher = FetcherFactory.create_fetcher(source)
                result = fetcher.fetch()
                
                if result.success:
                    all_articles.extend(result.articles)
                    metadata['sources_fetched'] += 1
                    print(f"  [OK] {source.name}: {len(result.articles)} articles")
                else:
                    metadata['sources_failed'] += 1
                    print(f"  [FAIL] {source.name}: {result.error}")
            except Exception as e:
                metadata['sources_failed'] += 1
                print(f"  [FAIL] {source.name}: {str(e)}")
        
        metadata['articles_fetched'] = len(all_articles)
        
        print(f"\nFetched: {metadata['articles_fetched']} total articles")
        print(f"Sources: {metadata['sources_fetched']} successful, {metadata['sources_failed']} failed")
        
        return all_articles, metadata
    
    def process_articles(
        self,
        articles: List[Article],
        date_range: str,
        region: str = "global"
    ):
        """
        Process articles: filter, deduplicate, rank.
        
        Args:
            articles: List of fetched articles
            date_range: Time range filter
            region: Regional filter
            
        Returns:
            Tuple of (ranked articles, metadata)
        """
        print(f"\nProcessing articles...")
        
        # Filter by date range
        print(f"  Filtering by date range: {DateFilter.get_range_description(date_range)}")
        filtered = DateFilter.filter_by_range(articles, date_range)
        print(f"  After date filter: {len(filtered)} articles")
        
        # Filter by region
        filtered = self.ranker.filter_by_region(filtered, region)
        print(f"  After region filter: {len(filtered)} articles")
        
        # Deduplicate
        print(f"  Deduplicating (75% threshold)...")
        deduplicator = Deduplicator(threshold=0.75)
        deduplicated = deduplicator.deduplicate(filtered)
        print(f"  After deduplication: {len(deduplicated)} unique stories")
        
        # Rank
        print(f"  Ranking by importance...")
        ranked = self.ranker.rank(deduplicated)
        print(f"  Selected: {len(ranked)} top articles")
        
        return ranked
    
    def run(
        self,
        date_range: str = "today",
        region: str = "global",
        use_cache: bool = True,
        output_path: str = None
    ) -> str:
        """
        Run complete aggregation pipeline.
        
        Args:
            date_range: Time range filter ('today', '7d', '30d', etc.)
            region: Regional filter ('us', 'de', 'eu', 'global')
            use_cache: Whether to use cached data if available
            output_path: Optional custom output path
            
        Returns:
            Path to generated markdown file
        """
        # Validate inputs
        if not DateFilter.is_valid_range(date_range):
            print(f"Error: Invalid date range '{date_range}'")
            print(f"Supported ranges: {', '.join(DateFilter.get_supported_ranges())}")
            sys.exit(1)
        
        if region not in self.config['regional_filtering']['supported_regions']:
            print(f"Error: Invalid region '{region}'")
            print(f"Supported regions: {', '.join(self.config['regional_filtering']['supported_regions'])}")
            sys.exit(1)
        
        print(f"=== Zeitungsjunge News Aggregator ===")
        print(f"Date range: {DateFilter.get_range_description(date_range)}")
        print(f"Region: {region.upper()}")
        print()
        
        # Try to use cache
        if use_cache and self.cache_manager.is_cache_valid(date_range):
            print("Using cached articles...")
            # Cache loading would need to reconstruct RankedArticle objects
            # For now, we'll fetch fresh data
            use_cache = False
        
        # Fetch articles
        articles, metadata = self.fetch_articles()
        
        if not articles:
            print("No articles fetched. Exiting.")
            sys.exit(1)
        
        # Process articles
        ranked = self.process_articles(articles, date_range, region)
        
        if not ranked:
            print("No articles matched the criteria. Exiting.")
            sys.exit(1)
        
        # Save to cache
        if self.config['cache']['enabled']:
            self.cache_manager.save_cache(date_range, ranked)
        
        # Generate markdown
        print(f"\nGenerating markdown report...")
        output_file = self.markdown_gen.generate(
            ranked,
            date_range,
            region,
            metadata=metadata
        )
        
        print(f"[DONE] Report saved to: {output_file}")
        
        return output_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Zeitungsjunge - News Aggregation & Summarization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                              # Default: today, all sources
  python src/main.py --range 7d                   # Last 7 days
  python src/main.py --range 7d --region us       # Last 7 days, US sources only
  python src/main.py --range 30d --region de      # Last 30 days, German sources
  python src/main.py --range today --no-cache     # Fresh fetch, no cache
        """
    )
    
    parser.add_argument(
        '--range',
        choices=['today', '7d', '30d', '60d', '90d'],
        default='today',
        help='Time range for articles (default: today)'
    )
    
    parser.add_argument(
        '--region',
        choices=['us', 'de', 'eu', 'global'],
        default='global',
        help='Regional filter (default: global)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Bypass cache and fetch fresh data'
    )
    
    parser.add_argument(
        '--output',
        help='Custom output file path'
    )
    
    parser.add_argument(
        '--config',
        default='config/sources.json',
        help='Path to sources.json configuration (default: config/sources.json)'
    )
    
    args = parser.parse_args()
    
    # Run aggregator
    aggregator = NewsAggregator(config_path=args.config)
    aggregator.run(
        date_range=args.range,
        region=args.region,
        use_cache=not args.no_cache,
        output_path=args.output
    )


if __name__ == '__main__':
    main()
