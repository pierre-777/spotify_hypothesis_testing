"""
Data Collection Module for Song Title Analysis

Optimised collection system for large-scale title complexity analysis.
Provides efficient Spotify API data collection with rate limiting,
error handling, and comprehensive title feature extraction.

Note: The main collection system is located at the project root as optimised_title_collector.py
"""

from .optimised_title_collector import OptimisedTitleCollector

__all__ = ['OptimisedTitleCollector'] 