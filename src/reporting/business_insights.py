"""
Business Insights Generator Module

This module transforms statistical test results into actionable business insights for
title feature analysis and statistical test results.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessInsightGenerator:
    """Generates business insights from title analysis results"""
    
    def __init__(self, data: pd.DataFrame, test_results: Dict):
        """
        Initialize with dataset and test results
        
        Args:
            data: Cleaned Spotify dataset
            test_results: Dictionary of statistical test results
        """
        self.data = data
        self.test_results = test_results
        self.insights = []
    
    def generate_insights(self) -> List[str]:
        """Generate comprehensive business insights"""
        logger.info("🔍 Generating business insights...")
        
        self._analyse_title_length()
        self._analyse_word_count()
        self._analyse_special_characters()
        self._analyse_genre_patterns()
        
        return self.insights
    
    def _analyse_title_length(self) -> None:
        """Analyse insights related to title length"""
        
        # Title length distribution analysis
        avg_length = self.data['title_length'].mean()
        median_length = self.data['title_length'].median()
        
        self.insights.append(f"📏 TITLE LENGTH INSIGHTS:")
        self.insights.append(f"   • Average title length: {avg_length:.1f} characters")
        self.insights.append(f"   • Median title length: {median_length:.1f} characters")
        
        # Correlation with popularity
        if 'title_length_correlation' in self.test_results:
            corr_result = self.test_results['title_length_correlation']
            correlation = corr_result.get('correlation', 0)
            p_value = corr_result.get('p_value', 1)
            
            if p_value < 0.05:
                if correlation > 0:
                    self.insights.append("   • Longer titles tend to have higher popularity")
                    self.insights.append("   • Recommendation: Consider encouraging descriptive titles")
                else:
                    self.insights.append("   • Shorter titles tend to have higher popularity")  
                    self.insights.append("   • Recommendation: Consider encouraging concise titles")
            else:
                self.insights.append("   • No significant relationship between title length and popularity")
        
        # Genre-specific patterns
        if 'genre_category' in self.data.columns:
            genre_lengths = self.data.groupby('genre_category')['title_length'].mean().sort_values(ascending=False)
            longest_genre = genre_lengths.index[0]
            shortest_genre = genre_lengths.index[-1]
            
            self.insights.append(f"   • {longest_genre} has the longest average titles ({genre_lengths[longest_genre]:.1f} chars)")
            self.insights.append(f"   • {shortest_genre} has the shortest average titles ({genre_lengths[shortest_genre]:.1f} chars)")
    
    def _analyse_word_count(self) -> None:
        """Analyse insights related to word count"""
        
        avg_words = self.data['word_count'].mean()
        median_words = self.data['word_count'].median()
        
        self.insights.append(f"\n📝 WORD COUNT INSIGHTS:")
        self.insights.append(f"   • Average word count: {avg_words:.1f} words")
        self.insights.append(f"   • Median word count: {median_words:.1f} words")
        
        # Word count groups analysis
        if 'word_count_groups' in self.test_results:
            group_result = self.test_results['word_count_groups']
            p_value = group_result.get('p_value', 1)
            
            if p_value < 0.05:
                # Find optimal word count range
                group_means = self.data.groupby('word_count_group')['popularity'].mean()
                best_group = group_means.idxmax()
                
                self.insights.append(f"   • Titles with {best_group} words tend to perform best")
                self.insights.append("   • Recommendation: Target optimal word count ranges")
            else:
                self.insights.append("   • No significant difference between word count groups")
        
        # Genre-specific patterns
        if 'genre_category' in self.data.columns:
            genre_words = self.data.groupby('genre_category')['word_count'].mean().sort_values(ascending=False)
            most_words_genre = genre_words.index[0]
            least_words_genre = genre_words.index[-1]
            
            self.insights.append(f"   • {most_words_genre} uses the most words on average ({genre_words[most_words_genre]:.1f})")
            self.insights.append(f"   • {least_words_genre} uses the fewest words on average ({genre_words[least_words_genre]:.1f})")
    
    def _analyse_special_characters(self) -> None:
        """Analyse insights related to special characters"""
        
        if 'has_special_chars' in self.data.columns:
            special_char_pct = (self.data['has_special_chars'].sum() / len(self.data)) * 100
            
            self.insights.append(f"\n🔢 SPECIAL CHARACTERS INSIGHTS:")
            self.insights.append(f"   • {special_char_pct:.1f}% of titles contain special characters")
            
            # Performance comparison
            with_special = self.data[self.data['has_special_chars']]['popularity'].mean()
            without_special = self.data[~self.data['has_special_chars']]['popularity'].mean()
            
            if with_special > without_special:
                diff = with_special - without_special
                self.insights.append(f"   • Titles with special characters score {diff:.1f} points higher on average")
                self.insights.append("   • Recommendation: Consider strategic use of special characters")
            else:
                diff = without_special - with_special
                self.insights.append(f"   • Titles without special characters score {diff:.1f} points higher on average")
                self.insights.append("   • Recommendation: Consider cleaner, simpler titles")
        
        # Numbers in titles
        if 'has_numbers' in self.data.columns:
            numbers_pct = (self.data['has_numbers'].sum() / len(self.data)) * 100
            self.insights.append(f"   • {numbers_pct:.1f}% of titles contain numbers")
            
            with_numbers = self.data[self.data['has_numbers']]['popularity'].mean()
            without_numbers = self.data[~self.data['has_numbers']]['popularity'].mean()
            
            if with_numbers > without_numbers:
                diff = with_numbers - without_numbers
                self.insights.append(f"   • Titles with numbers score {diff:.1f} points higher on average")
            else:
                diff = without_numbers - with_numbers
                self.insights.append(f"   • Titles without numbers score {diff:.1f} points higher on average")
    
    def _analyse_genre_patterns(self) -> None:
        """Analyse genre-specific patterns in title features"""
        # Analyse title length by genre
        self.insights.append(f"\n🎵 GENRE-SPECIFIC INSIGHTS:")
        
        if 'genre_category' in self.data.columns:
            genre_stats = self.data.groupby('genre_category').agg({
                'popularity': 'mean',
                'title_length': 'mean', 
                'word_count': 'mean'
            }).round(1)
            
            # Most popular genre
            most_popular = genre_stats['popularity'].idxmax()
            highest_pop = genre_stats.loc[most_popular, 'popularity']
            
            self.insights.append(f"   • {most_popular} has the highest average popularity ({highest_pop})")
            
            # Genre with longest titles
            longest_titles = genre_stats['title_length'].idxmax()
            avg_length = genre_stats.loc[longest_titles, 'title_length']
            
            self.insights.append(f"   • {longest_titles} has the longest average title length ({avg_length} chars)")
            
            # Genre-specific recommendations
            for genre in genre_stats.index:
                pop = genre_stats.loc[genre, 'popularity']
                length = genre_stats.loc[genre, 'title_length']
                words = genre_stats.loc[genre, 'word_count']
                
                if pop > genre_stats['popularity'].mean():
                    self.insights.append(f"   • {genre}: High-performing genre - maintain current strategies")
                else:
                    self.insights.append(f"   • {genre}: Consider optimising title strategies")
    
    def generate_summary_report(self) -> str:
        """Generate a formatted business insights report"""
        
        report = []
        report.append("=" * 60)
        report.append("SPOTIFY TITLE ANALYSIS - BUSINESS INSIGHTS REPORT")
        report.append("=" * 60)
        
        # Add all insights
        for insight in self.insights:
            report.append(insight)
        
        # Add strategic recommendations
        report.append(f"\n🎯 STRATEGIC RECOMMENDATIONS:")
        report.append("   • Develop genre-specific title guidelines")
        report.append("   • Test optimal title length ranges for each genre")
        report.append("   • Monitor title trend changes over time")
        report.append("   • Implement A/B testing for title optimisation")
        report.append("   • Create title complexity scoring system")
        
        # Add implementation priorities
        report.append(f"\n📈 IMPLEMENTATION PRIORITIES:")
        report.append("   1. Focus on genres with biggest optimisation opportunities")
        report.append("   2. Develop title length guidelines based on correlation analysis")
        report.append("   3. Create special character usage recommendations")
        report.append("   4. Monitor and track title performance metrics")
        
        return "\n".join(report)


def run_business_insights():
    """
    Interactive function to generate business insights
    This would be called after statistical analysis is complete
    """
    print("🎯 BUSINESS INSIGHTS GENERATION")
    print("=" * 40)
    print("This module generates actionable business insights from statistical results")
    print("Current status: Ready to generate insights from test results")
    
    return None
