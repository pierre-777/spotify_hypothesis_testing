"""
Exploratory Data Analysis Module

This module performs exploratory data analysis on Spotify track data,
focusing on title features and their relationship with popularity.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SpotifyEDA:
    """Performs exploratory data analysis on Spotify track data."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.title_features = ['title_length', 'word_count', 'has_numbers', 'has_special_chars']
        
    def full_eda_report(self) -> Dict:
        """Generate a comprehensive EDA report."""
        logging.info("Starting exploratory data analysis...")
        
        results = {
            'dataset_overview': self._analyse_dataset_overview(),
            'distributions': self._analyse_distributions(),
            'correlations': self._analyse_correlations(),
            'title_length_analysis': self._analyse_title_length(),
            'word_count_analysis': self._analyse_word_count(),
            'title_features_analysis': self._analyse_title_features(),
            'statistical_assumptions': self._check_statistical_assumptions()
        }
        
        logging.info("Exploratory analysis complete")
        return results
    
    def _analyse_dataset_overview(self) -> Dict:
        """Analyse basic dataset characteristics."""
        return {
            'total_tracks': len(self.df),
            'unique_artists': self.df['artist_name'].nunique(),
            'popularity_range': (self.df['popularity'].min(), self.df['popularity'].max()),
            'title_length_range': (self.df['title_length'].min(), self.df['title_length'].max()),
            'word_count_range': (self.df['word_count'].min(), self.df['word_count'].max()),
            'titles_with_numbers': self.df['has_numbers'].sum(),
            'titles_with_special_chars': self.df['has_special_chars'].sum()
        }
    
    def _analyse_distributions(self) -> Dict:
        """Analyse distributions of key variables."""
        results = {}
        
        # Title length distribution
        results['title_length'] = {
            'mean': self.df['title_length'].mean(),
            'median': self.df['title_length'].median(),
            'std': self.df['title_length'].std(),
            'skew': stats.skew(self.df['title_length']),
            'kurtosis': stats.kurtosis(self.df['title_length'])
        }
        
        # Word count distribution
        results['word_count'] = {
            'mean': self.df['word_count'].mean(),
            'median': self.df['word_count'].median(),
            'std': self.df['word_count'].std(),
            'skew': stats.skew(self.df['word_count']),
            'kurtosis': stats.kurtosis(self.df['word_count'])
        }
        
        # Popularity distribution
        results['popularity'] = {
            'mean': self.df['popularity'].mean(),
            'median': self.df['popularity'].median(),
            'std': self.df['popularity'].std(),
            'skew': stats.skew(self.df['popularity']),
            'kurtosis': stats.kurtosis(self.df['popularity'])
        }
        
        return results
    
    def _analyse_correlations(self) -> Dict:
        """Analyse correlations between variables."""
        # Calculate correlations
        corr_matrix = self.df[['popularity', 'title_length', 'word_count']].corr()
        
        # Calculate point-biserial correlations for binary features
        pb_corr_numbers = stats.pointbiserialr(self.df['has_numbers'], self.df['popularity'])
        pb_corr_special = stats.pointbiserialr(self.df['has_special_chars'], self.df['popularity'])
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'point_biserial_correlations': {
                'has_numbers': pb_corr_numbers.correlation,
                'has_special_chars': pb_corr_special.correlation
            }
        }
    
    def _analyse_title_length(self) -> Dict:
        """Analyse title length patterns."""
        # Create title length groups
        self.df['title_length_group'] = pd.cut(
            self.df['title_length'],
            bins=[0, 20, 40, 60, float('inf')],
            labels=['Very Short', 'Short', 'Medium', 'Long']
        )
        
        # Calculate group statistics
        group_stats = self.df.groupby('title_length_group')['popularity'].agg([
            'count', 'mean', 'std', 'median'
        ]).to_dict()
        
        # Calculate effect sizes
        groups = self.df.groupby('title_length_group')['popularity']
        effect_sizes = {}
        
        for g1 in self.df['title_length_group'].unique():
            for g2 in self.df['title_length_group'].unique():
                if g1 < g2:
                    g1_data = groups.get_group(g1)
                    g2_data = groups.get_group(g2)
                    cohens_d = (g1_data.mean() - g2_data.mean()) / np.sqrt(
                        (g1_data.var() + g2_data.var()) / 2
                    )
                    effect_sizes[f"{g1}_vs_{g2}"] = cohens_d
        
        return {
            'group_statistics': group_stats,
            'effect_sizes': effect_sizes,
            'correlation_with_popularity': self.df['title_length'].corr(self.df['popularity'])
        }
    
    def _analyse_word_count(self) -> Dict:
        """Analyse word count patterns."""
        # Create word count groups
        self.df['word_count_group'] = pd.cut(
            self.df['word_count'],
            bins=[0, 2, 4, float('inf')],
            labels=['Short', 'Medium', 'Long']
        )
        
        # Calculate group statistics
        group_stats = self.df.groupby('word_count_group')['popularity'].agg([
            'count', 'mean', 'std', 'median'
        ]).to_dict()
        
        # Calculate effect sizes
        groups = self.df.groupby('word_count_group')['popularity']
        effect_sizes = {}
        
        for g1 in self.df['word_count_group'].unique():
            for g2 in self.df['word_count_group'].unique():
                if g1 < g2:
                    g1_data = groups.get_group(g1)
                    g2_data = groups.get_group(g2)
                    cohens_d = (g1_data.mean() - g2_data.mean()) / np.sqrt(
                        (g1_data.var() + g2_data.var()) / 2
                    )
                    effect_sizes[f"{g1}_vs_{g2}"] = cohens_d
        
        return {
            'group_statistics': group_stats,
            'effect_sizes': effect_sizes,
            'correlation_with_popularity': self.df['word_count'].corr(self.df['popularity'])
        }
    
    def _analyse_title_features(self) -> Dict:
        """Analyse patterns in title features."""
        results = {}
        
        # Analyse numbers in titles
        number_stats = self.df.groupby('has_numbers')['popularity'].agg([
            'count', 'mean', 'std', 'median'
        ]).to_dict()
        
        # Analyse special characters
        special_stats = self.df.groupby('has_special_chars')['popularity'].agg([
            'count', 'mean', 'std', 'median'
        ]).to_dict()
        
        # Calculate effect sizes
        number_effect = (self.df[self.df['has_numbers']]['popularity'].mean() -
                        self.df[~self.df['has_numbers']]['popularity'].mean()) / np.sqrt(
            (self.df[self.df['has_numbers']]['popularity'].var() +
             self.df[~self.df['has_numbers']]['popularity'].var()) / 2
        )
        
        special_effect = (self.df[self.df['has_special_chars']]['popularity'].mean() -
                         self.df[~self.df['has_special_chars']]['popularity'].mean()) / np.sqrt(
            (self.df[self.df['has_special_chars']]['popularity'].var() +
             self.df[~self.df['has_special_chars']]['popularity'].var()) / 2
        )
        
        return {
            'numbers_in_titles': {
                'statistics': number_stats,
                'effect_size': number_effect
            },
            'special_chars_in_titles': {
                'statistics': special_stats,
                'effect_size': special_effect
            }
        }
    
    def _check_statistical_assumptions(self) -> Dict:
        """Check statistical assumptions for hypothesis testing."""
        results = {}
        
        # Normality tests
        title_stat, title_p = stats.shapiro(self.df['title_length'].sample(5000))
        word_stat, word_p = stats.shapiro(self.df['word_count'].sample(5000))
        pop_stat, pop_p = stats.shapiro(self.df['popularity'].sample(5000))
        
        results['normality_tests'] = {
            'title_length': {'statistic': title_stat, 'p_value': title_p},
            'word_count': {'statistic': word_stat, 'p_value': word_p},
            'popularity': {'statistic': pop_stat, 'p_value': pop_p}
        }
        
        # Group size checks
        if 'word_count_group' in self.df.columns:
            group_sizes = self.df['word_count_group'].value_counts()
            results['group_sizes'] = group_sizes.to_dict()
        
        # Variance homogeneity
        if 'word_count_group' in self.df.columns:
            groups = [group['popularity'].values for name, group in self.df.groupby('word_count_group')]
            levene_stat, levene_p = stats.levene(*groups)
            results['variance_homogeneity'] = {
                'statistic': levene_stat,
                'p_value': levene_p
            }
        
        return results

def run_exploratory_analysis():
    """Main function to run EDA"""
    print("\n🔍 STEP 3: EXPLORATORY DATA ANALYSIS")
    print("=" * 50)
    
    # Load cleaned data from previous step
    from .data_loader import SpotifyDataLoader
    
    loader = SpotifyDataLoader()
    
    # Try to load cleaned data first, fallback to raw data
    try:
        # Look for most recent cleaned data
        data_files = list(loader.data_dir.glob("spotify_cleaned_data_*.csv"))
        if data_files:
            latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
            df = pd.read_csv(latest_file)
            print(f"📂 Using cleaned data: {latest_file}")
        else:
            print("📂 No cleaned data found, using raw data...")
            df = loader.load_existing_data()
    except:
        print("📂 Loading most recent raw data...")
        df = loader.load_existing_data()
    
    # Run EDA
    eda = SpotifyEDA(df)
    results = eda.full_eda_report()
    
    return df, results

if __name__ == "__main__":
    df, results = run_exploratory_analysis() 