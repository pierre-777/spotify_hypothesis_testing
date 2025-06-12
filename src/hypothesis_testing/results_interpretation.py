"""
Results Interpretation Module

This module provides interpretation and analysis of statistical test results
from the title complexity hypothesis testing framework.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultsInterpreter:
    """
    Interprets statistical test results and provides business insights
    
    Takes raw statistical test results and converts them into:
    - Plain English interpretations
    - Business recommendations
    - Statistical significance assessments
    - Effect size evaluations
    """
    
    def __init__(self, test_results: Dict):
        """
        Initialize with test results from StatisticalTests
        
        Args:
            test_results: Dictionary containing test results from StatisticalTests
        """
        self.results = test_results
        self.interpretations = {}
        self.business_insights = []
    
    def interpret_all_results(self) -> Dict:
        """
        Interpret all statistical test results
        
        Returns:
            Dictionary containing interpretations for all tests
        """
        logger.info("🔍 Interpreting statistical test results...")
        
        # Interpret correlation analysis
        if 'title_length_correlation' in self.results:
            self.interpretations['title_length'] = self._interpret_correlation(
                self.results['title_length_correlation'], 
                'title length', 
                'popularity'
            )
        
        # Interpret group comparisons
        if 'word_count_groups' in self.results:
            self.interpretations['word_count'] = self._interpret_group_comparison(
                self.results['word_count_groups'],
                'word count groups'
            )
        
        # Interpret ANOVA results
        if 'title_features_anova' in self.results:
            self.interpretations['title_features'] = self._interpret_anova(
                self.results['title_features_anova'],
                'title features'
            )
        
        # Generate business insights
        self._generate_business_insights()
        
        logger.info("✅ Results interpretation complete")
        return self.interpretations
    
    def _interpret_correlation(self, correlation_result: Dict, var1: str, var2: str) -> Dict:
        """
        Interpret correlation analysis results
        
        Args:
            correlation_result: Dictionary with 'correlation' and 'p_value' keys
            var1: Name of first variable
            var2: Name of second variable
            
        Returns:
            Dictionary containing interpretation
        """
        corr = correlation_result['correlation']
        p_value = correlation_result['p_value']
        
        # Determine significance
        is_significant = p_value < 0.05
        significance_level = "significant" if is_significant else "not significant"
        
        # Determine effect size
        if abs(corr) < 0.1:
            effect_size = "negligible"
        elif abs(corr) < 0.3:
            effect_size = "small"
        elif abs(corr) < 0.5:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        # Determine direction
        direction = "positive" if corr > 0 else "negative"
        
        interpretation = {
            'statistical_summary': f"r = {corr:.3f}, p = {p_value:.3f}",
            'significance': significance_level,
            'effect_size': effect_size,
            'direction': direction,
            'interpretation': f"There is a {significance_level} {direction} {effect_size} correlation between {var1} and {var2}.",
            'business_implication': self._get_correlation_business_insight(var1, var2, corr, is_significant),
            'recommendations': [
                f"Analyse {var1} patterns by genre",
                f"Consider {var1} as a factor in track optimisation",
                f"Investigate outliers in {var1} distribution"
            ]
        }
        
        return interpretation
    
    def _interpret_group_comparison(self, group_result: Dict, group_name: str) -> Dict:
        """
        Interpret group comparison results (t-test, Mann-Whitney, etc.)
        
        Args:
            group_result: Dictionary with test results
            group_name: Name of the groups being compared
            
        Returns:
            Dictionary containing interpretation
        """
        test_statistic = group_result.get('test_statistic', 0)
        p_value = group_result.get('p_value', 1)
        
        # Determine significance
        is_significant = p_value < 0.05
        significance_level = "significant" if is_significant else "not significant"
        
        interpretation = {
            'statistical_summary': f"Test statistic = {test_statistic:.3f}, p = {p_value:.3f}",
            'significance': significance_level,
            'interpretation': f"The difference between {group_name} is {significance_level}.",
            'business_implication': self._get_group_business_insight(group_name, is_significant),
            'recommendations': [
                f"Analyse {group_name} patterns by genre",
                f"Consider segmenting strategies by {group_name}",
                f"Test {group_name} optimisation approaches"
            ]
        }
        
        return interpretation
    
    def _interpret_anova(self, anova_result: Dict, factor_name: str) -> Dict:
        """
        Interpret ANOVA results
        
        Args:
            anova_result: Dictionary with F-statistic and p-value
            factor_name: Name of the factor being tested
            
        Returns:
            Dictionary containing interpretation
        """
        f_statistic = anova_result.get('f_statistic', 0)
        p_value = anova_result.get('p_value', 1)
        
        # Determine significance
        is_significant = p_value < 0.05
        significance_level = "significant" if is_significant else "not significant"
        
        interpretation = {
            'statistical_summary': f"F = {f_statistic:.3f}, p = {p_value:.3f}",
            'significance': significance_level,
            'interpretation': f"The effect of {factor_name} on popularity is {significance_level}.",
            'business_implication': self._get_anova_business_insight(factor_name, is_significant),
            'recommendations': [
                f"Analyse {factor_name} patterns by genre",
                f"Develop {factor_name}-specific strategies",
                f"Test targeted {factor_name} optimisations"
            ]
        }
        
        return interpretation
    
    def _get_correlation_business_insight(self, var1: str, var2: str, correlation: float, is_significant: bool) -> str:
        """Generate business insight for correlation analysis"""
        if not is_significant:
            return f"No reliable relationship found between {var1} and {var2}. Consider other factors."
        
        if var1 == "title length":
            if correlation > 0:
                return "Longer titles tend to be associated with higher popularity. Consider strategic title extension."
            else:
                return "Shorter titles tend to be associated with higher popularity. Consider concise title strategies."
        
        return f"Significant relationship between {var1} and {var2} detected. Investigate further."
    
    def _get_group_business_insight(self, group_name: str, is_significant: bool) -> str:
        """Generate business insight for group comparisons"""
        if not is_significant:
            return f"No meaningful difference between {group_name}. Standardised approach may be suitable."
        
        return f"Meaningful differences detected between {group_name}. Targeted strategies recommended."
    
    def _get_anova_business_insight(self, factor_name: str, is_significant: bool) -> str:
        """Generate business insight for ANOVA results"""
        if not is_significant:
            return f"{factor_name} does not significantly impact popularity. Focus on other factors."
        
        return f"{factor_name} significantly impacts popularity. Develop factor-specific optimisation strategies."
    
    def _generate_business_insights(self):
        """Generate overall business insights from all test results"""
        insights = []
        
        # Count significant results
        significant_tests = sum(1 for interp in self.interpretations.values() 
                              if interp['significance'] == 'significant')
        total_tests = len(self.interpretations)
        
        if significant_tests == 0:
            insights.append("🔍 No significant title feature relationships detected. Consider expanding analysis scope.")
        elif significant_tests == total_tests:
            insights.append("🎯 All title features show significant relationships with popularity. Comprehensive optimisation strategy recommended.")
        else:
            insights.append(f"📊 {significant_tests}/{total_tests} title features show significant relationships. Focus optimisation efforts on significant factors.")
        
        # Add specific insights based on patterns
        for test_name, interp in self.interpretations.items():
            if interp['significance'] == 'significant':
                insights.append(f"✅ {test_name.replace('_', ' ').title()}: {interp['business_implication']}")
        
        self.business_insights = insights
    
    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive summary report
        
        Returns:
            Formatted string containing full results summary
        """
        report = []
        report.append("=" * 60)
        report.append("SPOTIFY TITLE ANALYSIS - STATISTICAL RESULTS SUMMARY")
        report.append("=" * 60)
        
        # Executive summary
        report.append("\n📊 EXECUTIVE SUMMARY")
        report.append("-" * 30)
        for insight in self.business_insights:
            report.append(f"  {insight}")
        
        # Detailed results
        report.append("\n🔍 DETAILED STATISTICAL RESULTS")
        report.append("-" * 40)
        
        for test_name, interp in self.interpretations.items():
            report.append(f"\n{test_name.replace('_', ' ').upper()}:")
            report.append(f"  Statistical: {interp['statistical_summary']}")
            report.append(f"  Result: {interp['interpretation']}")
            report.append(f"  Business: {interp['business_implication']}")
            
            report.append("  Recommendations:")
            for rec in interp['recommendations']:
                report.append(f"    • {rec}")
        
        # Methodology note
        report.append(f"\n📝 METHODOLOGY")
        report.append("-" * 20)
        report.append("  • Significance level: α = 0.05")
        report.append("  • Effect sizes: negligible (<0.1), small (0.1-0.3), medium (0.3-0.5), large (>0.5)")
        report.append("  • Statistical tests selected based on data distribution and sample size")
        
        return "\n".join(report)


def run_results_interpretation():
    """
    Interactive function to run results interpretation
    This would be called after statistical tests are complete
    """
    print("📊 RESULTS INTERPRETATION")
    print("=" * 40)
    print("This module interprets statistical test results and provides business insights")
    print("Current status: Ready to interpret test results")
    
    # This would normally load actual test results
    # For now, return placeholder
    return None 