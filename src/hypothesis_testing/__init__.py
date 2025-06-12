"""
Hypothesis Testing Module for Title Complexity Analysis

Comprehensive statistical testing framework for song title vs popularity research.
Supports t-tests, ANOVA, regression, and advanced A/B testing methodologies.
"""

from .test_setup import TestSetup
from .statistical_tests import TitleFeatureAnalyzer
from .results_interpretation import ResultsInterpreter

__all__ = ['TestSetup', 'TitleFeatureAnalyzer', 'ResultsInterpreter'] 