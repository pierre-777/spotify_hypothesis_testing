"""
Statistical Tests Module

This module provides statistical tests for analysing title features
and their relationship with popularity.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    """Data class for storing test results"""
    test_name: str
    hypothesis: str
    test_statistic: float
    p_value: float
    effect_size: float
    conclusion: str
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TitleFeatureAnalyzer:
    """Analyses title features using statistical tests"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.results: List[TestResult] = []
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all statistical tests for title features"""
        self._test_title_length_correlation()
        self._test_word_count_groups()
        self._test_special_characters()
        return self.results
    
    def _test_title_length_correlation(self) -> None:
        """Test correlation between title length and popularity"""
        correlation, p_value = stats.pearsonr(
            self.data['title_length'],
            self.data['popularity']
        )
        
        result = TestResult(
            test_name="Title Length Correlation",
            hypothesis="Title length is correlated with popularity",
            test_statistic=correlation,
            p_value=p_value,
            effect_size=abs(correlation),
            conclusion=self._interpret_correlation(correlation, p_value)
        )
        self.results.append(result)
    
    def _test_word_count_groups(self) -> None:
        """Test if word count groups have different popularity distributions"""
        # Create word count groups
        self.data['word_count_group'] = pd.cut(
            self.data['word_count'],
            bins=[0, 1, 3, 5, float('inf')],
            labels=['Single', 'Short', 'Medium', 'Long']
        )
        
        # Perform ANOVA
        groups = [group for _, group in self.data.groupby('word_count_group')]
        f_stat, p_value = stats.f_oneway(*[group['popularity'] for group in groups])
        
        # Calculate effect size (eta squared)
        total_ss = sum((self.data['popularity'] - self.data['popularity'].mean()) ** 2)
        between_ss = sum(len(group) * ((group['popularity'].mean() - self.data['popularity'].mean()) ** 2)
                        for group in groups)
        eta_squared = between_ss / total_ss
        
        result = TestResult(
            test_name="Word Count ANOVA",
            hypothesis="Word count groups have different popularity distributions",
            test_statistic=f_stat,
            p_value=p_value,
            effect_size=eta_squared,
            conclusion=self._interpret_anova(p_value, eta_squared)
        )
        self.results.append(result)
    
    def _test_special_characters(self) -> None:
        """Test if presence of special characters affects popularity"""
        # Perform t-test
        with_special = self.data[self.data['has_special_chars']]['popularity']
        without_special = self.data[~self.data['has_special_chars']]['popularity']
        
        t_stat, p_value = stats.ttest_ind(with_special, without_special)
        
        # Calculate Cohen's d
        cohens_d = (with_special.mean() - without_special.mean()) / np.sqrt(
            ((with_special.std() ** 2 + without_special.std() ** 2) / 2)
        )
        
        result = TestResult(
            test_name="Special Characters t-test",
            hypothesis="Titles with special characters have different popularity",
            test_statistic=t_stat,
            p_value=p_value,
            effect_size=abs(cohens_d),
            conclusion=self._interpret_ttest(p_value, cohens_d)
        )
        self.results.append(result)
    
    def _interpret_correlation(self, correlation: float, p_value: float) -> str:
        """Interpret correlation test results"""
        if p_value > 0.05:
            return "No significant correlation found between title length and popularity"
        
        strength = "strong" if abs(correlation) > 0.5 else "moderate" if abs(correlation) > 0.3 else "weak"
        direction = "positive" if correlation > 0 else "negative"
        return f"Found {strength} {direction} correlation (r={correlation:.2f})"
    
    def _interpret_anova(self, p_value: float, eta_squared: float) -> str:
        """Interpret ANOVA test results"""
        if p_value > 0.05:
            return "No significant difference found between word count groups"
        
        effect = "large" if eta_squared > 0.14 else "medium" if eta_squared > 0.06 else "small"
        return f"Found significant differences between groups with {effect} effect size (η²={eta_squared:.2f})"
    
    def _interpret_ttest(self, p_value: float, cohens_d: float) -> str:
        """Interpret t-test results"""
        if p_value > 0.05:
            return "No significant difference found in popularity between titles with and without special characters"
        
        effect = "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small"
        direction = "higher" if cohens_d > 0 else "lower"
        return f"Found {effect} effect size (d={cohens_d:.2f}) with {direction} popularity for titles with special characters"
    
    def get_summary(self) -> Dict:
        """Get summary of all test results"""
        return {
            'total_tests': len(self.results),
            'significant_tests': sum(1 for r in self.results if r.p_value < 0.05),
            'test_results': [
                {
                    'test_name': r.test_name,
                    'hypothesis': r.hypothesis,
                    'p_value': r.p_value,
                    'effect_size': r.effect_size,
                    'conclusion': r.conclusion
                }
                for r in self.results
            ]
        }

def run_statistical_tests():
    """Main function to run statistical tests"""
    print("\n🔬 STEP 5: STATISTICAL TESTS")
    print("=" * 50)
    
    # Load data
    from ..data_processing.data_loader import SpotifyDataLoader
    loader = SpotifyDataLoader()
    df = loader.load_data("spotify_tracks.csv")
    
    # Run tests
    tests = TitleFeatureAnalyzer(df)
    results = tests.run_all_tests()
    
    return results

if __name__ == "__main__":
    results = run_statistical_tests() 