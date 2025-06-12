"""
Data Processing Module for Song Title Analysis

Comprehensive data processing pipeline for Spotify track title analysis.
Includes text analysis, emotional content detection, and statistical preparation.
"""

from .data_loader import SpotifyDataLoader
from .data_cleaner import SpotifyDataCleaner
from .exploratory_analysis import SpotifyEDA

__all__ = ['SpotifyDataLoader', 'SpotifyDataCleaner', 'SpotifyEDA'] 