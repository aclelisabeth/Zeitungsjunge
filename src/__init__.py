"""Zeitungsjunge - News Aggregation and Summarization Application."""

__version__ = "1.0.0"
__author__ = "Elisabeth Schallerl"
__description__ = "Aggregates and summarizes important news headlines from configurable online news sources"

from src.models import Article, Source, RankedArticle, FetchResult

__all__ = ['Article', 'Source', 'RankedArticle', 'FetchResult']
