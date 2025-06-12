"""
Data Cleaning Module
Step 2: Clean and validate data for analysis

This module handles comprehensive data cleaning for title complexity analysis,
including missing value treatment, outlier detection, and feature validation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from scipy import stats

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyDataCleaner:
    """Clean and validate Spotify data for analysis"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with raw data"""
        self.df = df.copy()
        self.cleaned_df = None
        self.validation_results = {}
    
    def clean_data(self) -> pd.DataFrame:
        """
        Clean and validate data
        Returns:
            Cleaned DataFrame
        """
        logger.info("🧹 Starting data cleaning...")
        
        print("\n🧹 STEP 2: DATA CLEANING")
        print("=" * 50)
        
        # 2.1: Handle missing values
        self._handle_missing_values()
        
        # 2.2: Remove duplicates
        self._remove_duplicates()
        
        # 2.3: Validate data types
        self._validate_data_types()
        
        # 2.4: Handle outliers
        self._handle_outliers()
        
        # 2.5: Create derived features
        self._create_derived_features()
        
        # 2.6: Validate cleaned data
        self._validate_cleaned_data()
        
        logger.info("✅ Data cleaning completed")
        
        return self.cleaned_df
    
    def _handle_missing_values(self):
        """Handle missing values in the dataset"""
        print("\n🔍 HANDLING MISSING VALUES")
        print("-" * 40)
        
        # Check for missing values
        missing = self.df.isnull().sum()
        if missing.any():
            print("Missing values found:")
            for col, count in missing[missing > 0].items():
                print(f"  • {col}: {count:,}")
        
        # Handle missing values
        self.cleaned_df = self.df.copy()
        
        # Drop rows with missing key values
        key_cols = ['track_name', 'artist_name', 'popularity', 'duration_ms', 'genre']
        self.cleaned_df = self.cleaned_df.dropna(subset=key_cols)
        
        # Fill missing values in derived features
        if 'title_length' in self.cleaned_df.columns:
            self.cleaned_df['title_length'] = self.cleaned_df['title_length'].fillna(0)
        if 'word_count' in self.cleaned_df.columns:
            self.cleaned_df['word_count'] = self.cleaned_df['word_count'].fillna(0)
        if 'has_numbers' in self.cleaned_df.columns:
            self.cleaned_df['has_numbers'] = self.cleaned_df['has_numbers'].fillna(False)
        if 'has_special_chars' in self.cleaned_df.columns:
            self.cleaned_df['has_special_chars'] = self.cleaned_df['has_special_chars'].fillna(False)
    
    def _remove_duplicates(self):
        """Remove duplicate entries"""
        print("\n🔍 REMOVING DUPLICATES")
        print("-" * 40)
        
        initial_count = len(self.cleaned_df)
        self.cleaned_df = self.cleaned_df.drop_duplicates(subset=['track_name', 'artist_name'])
        removed_count = initial_count - len(self.cleaned_df)
        
        print(f"Removed {removed_count:,} duplicate entries")
    
    def _validate_data_types(self):
        """Validate and convert data types"""
        print("\n🔍 VALIDATING DATA TYPES")
        print("-" * 40)
        
        # Convert numeric columns
        numeric_cols = ['popularity', 'duration_ms', 'title_length', 'word_count']
        for col in numeric_cols:
            if col in self.cleaned_df.columns:
                self.cleaned_df[col] = pd.to_numeric(self.cleaned_df[col], errors='coerce')
        
        # Convert boolean columns
        bool_cols = ['has_numbers', 'has_special_chars']
        for col in bool_cols:
            if col in self.cleaned_df.columns:
                self.cleaned_df[col] = self.cleaned_df[col].astype(bool)
    
    def _handle_outliers(self):
        """Handle outliers in numeric columns"""
        print("\n🔍 HANDLING OUTLIERS")
        print("-" * 40)
        
        # Define valid ranges
        ranges = {
            'popularity': (0, 100),
            'duration_ms': (0, 3600000),  # 1 hour max
            'title_length': (0, 200),     # 200 characters max
            'word_count': (0, 50)         # 50 words max
        }
        
        # Clip values to valid ranges
        for col, (min_val, max_val) in ranges.items():
            if col in self.cleaned_df.columns:
                initial_outliers = len(self.cleaned_df[
                    (self.cleaned_df[col] < min_val) | 
                    (self.cleaned_df[col] > max_val)
                ])
                
                self.cleaned_df[col] = self.cleaned_df[col].clip(min_val, max_val)
                
                print(f"{col}: Clipped {initial_outliers:,} outliers to range [{min_val}, {max_val}]")
    
    def _create_derived_features(self):
        """Create derived features for analysis"""
        print("\n🔍 CREATING DERIVED FEATURES")
        print("-" * 40)
        
        # Title length groups
        self.cleaned_df['title_length_group'] = pd.cut(
            self.cleaned_df['title_length'],
            bins=[0, 20, 40, 60, float('inf')],
            labels=['Very Short (0-20)', 'Short (21-40)', 'Medium (41-60)', 'Long (60+)']
        )
        
        # Word count groups
        self.cleaned_df['word_count_group'] = pd.cut(
            self.cleaned_df['word_count'],
            bins=[0, 2, 4, float('inf')],
            labels=['Short (1-2 words)', 'Medium (3-4 words)', 'Long (5+ words)']
        )
        
        # Popularity categories
        self.cleaned_df['popularity_category'] = pd.cut(
            self.cleaned_df['popularity'],
            bins=[0, 20, 40, 60, 80, 100],
            labels=['Very Low (0-20)', 'Low (21-40)', 'Medium (41-60)', 'High (61-80)', 'Very High (81-100)']
        )
        
        # Title feature combinations
        self.cleaned_df['title_feature_group'] = self.cleaned_df.apply(
            lambda x: f"{'Has Numbers' if x['has_numbers'] else 'No Numbers'}, "
                     f"{'Has Special Chars' if x['has_special_chars'] else 'No Special Chars'}",
            axis=1
        )
    
    def _validate_cleaned_data(self):
        """Validate cleaned data"""
        print("\n🔍 VALIDATING CLEANED DATA")
        print("-" * 40)
        
        # Check for remaining missing values
        missing = self.cleaned_df.isnull().sum()
        if missing.any():
            print("⚠️  Warning: Missing values remain:")
            for col, count in missing[missing > 0].items():
                print(f"  • {col}: {count:,}")
        else:
            print("✅ No missing values in cleaned data")
        
        # Check data types
        print("\nData types:")
        for col, dtype in self.cleaned_df.dtypes.items():
            print(f"  • {col}: {dtype}")
        
        # Check value ranges
        print("\nValue ranges:")
        numeric_cols = ['popularity', 'duration_ms', 'title_length', 'word_count']
        for col in numeric_cols:
            if col in self.cleaned_df.columns:
                print(f"  • {col}: [{self.cleaned_df[col].min():.1f}, {self.cleaned_df[col].max():.1f}]")
        
        # Store validation results
        self.validation_results = {
            'rows': len(self.cleaned_df),
            'columns': len(self.cleaned_df.columns),
            'missing_values': missing.to_dict(),
            'dtypes': self.cleaned_df.dtypes.to_dict()
        }
    
    def _check_statistical_assumptions(self) -> Dict:
        """Check statistical assumptions for analysis"""
        print("\n📊 CHECKING STATISTICAL ASSUMPTIONS")
        print("-" * 40)
        
        assumptions = {}
        
        # 1. Normality tests
        print("1. Testing for normality:")
        
        # Shapiro-Wilk test for smaller samples, Anderson-Darling for larger
        if len(self.cleaned_df) < 5000:
            title_stat, title_p = stats.shapiro(self.cleaned_df['title_length'].sample(5000))
            word_stat, word_p = stats.shapiro(self.cleaned_df['word_count'].sample(5000))
            pop_stat, pop_p = stats.shapiro(self.cleaned_df['popularity'].sample(5000))
            test_name = "Shapiro-Wilk"
        else:
            title_stat, title_p = stats.normaltest(self.cleaned_df['title_length'])
            word_stat, word_p = stats.normaltest(self.cleaned_df['word_count'])
            pop_stat, pop_p = stats.normaltest(self.cleaned_df['popularity'])
            test_name = "D'Agostino-Pearson"
        
        print(f"   {test_name} test results:")
        print(f"   Title Length: statistic={title_stat:.4f}, p-value={title_p:.4f}")
        print(f"   Word Count: statistic={word_stat:.4f}, p-value={word_p:.4f}")
        print(f"   Popularity: statistic={pop_stat:.4f}, p-value={pop_p:.4f}")
        
        assumptions['normality'] = {
            'title_length_normal': title_p > 0.05,
            'word_count_normal': word_p > 0.05,
            'popularity_normal': pop_p > 0.05,
            'test_used': test_name
        }
        
        # 2. Equal variances (Levene's test)
        print("\n2. Testing for equal variances across groups:")
        
        # Test word count groups
        if 'word_count_group' in self.cleaned_df.columns:
            groups = [group['popularity'].values for name, group in self.cleaned_df.groupby('word_count_group')]
            levene_stat, levene_p = stats.levene(*groups)
            print(f"   Word Count Groups - Levene's test: statistic={levene_stat:.4f}, p-value={levene_p:.4f}")
            assumptions['word_count_equal_variance'] = levene_p > 0.05
        
        # Test title feature groups
        if 'title_feature_group' in self.cleaned_df.columns:
            groups = [group['popularity'].values for name, group in self.cleaned_df.groupby('title_feature_group')]
            levene_stat, levene_p = stats.levene(*groups)
            print(f"   Title Feature Groups - Levene's test: statistic={levene_stat:.4f}, p-value={levene_p:.4f}")
            assumptions['title_feature_equal_variance'] = levene_p > 0.05
        
        # 3. Sample size adequacy
        print("\n3. Sample size adequacy:")
        total_n = len(self.cleaned_df)
        print(f"   Total sample size: {total_n:,}")
        
        if 'word_count_group' in self.cleaned_df.columns:
            group_sizes = self.cleaned_df['word_count_group'].value_counts()
            min_group_size = group_sizes.min()
            print(f"   Minimum word count group size: {min_group_size:,}")
            assumptions['word_count_adequate_sample'] = min_group_size >= 30
        
        if 'title_feature_group' in self.cleaned_df.columns:
            group_sizes = self.cleaned_df['title_feature_group'].value_counts()
            min_group_size = group_sizes.min()
            print(f"   Minimum title feature group size: {min_group_size:,}")
            assumptions['title_feature_adequate_sample'] = min_group_size >= 30
        
        # 4. Independence assumption
        print("\n4. Independence assumption:")
        print("   ✓ Assuming independence (random sampling from Spotify catalog)")
        assumptions['independence'] = True
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR STATISTICAL TESTS:")
        if assumptions.get('normality', {}).get('popularity_normal', False):
            print("   ✓ Use parametric tests (t-tests, ANOVA)")
        else:
            print("   ⚠️  Consider non-parametric tests (Mann-Whitney, Kruskal-Wallis)")
        
        if not assumptions.get('word_count_equal_variance', True):
            print("   ⚠️  Use Welch's t-test for word count group comparisons")
        
        if not assumptions.get('title_feature_equal_variance', True):
            print("   ⚠️  Use Welch's t-test for title feature group comparisons")
        
        return assumptions

def run_data_cleaning():
    """Main function to run data cleaning"""
    print("\n🧹 STEP 2: DATA CLEANING")
    print("=" * 50)
    
    # Load data
    from .data_loader import SpotifyDataLoader
    loader = SpotifyDataLoader()
    df = loader.load_data("spotify_tracks.csv")
    
    # Clean data
    cleaner = SpotifyDataCleaner(df)
    cleaned_df = cleaner.clean_data()
    
    # Save cleaned data
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/spotify_cleaned_data_{timestamp}.csv"
    cleaned_df.to_csv(output_file, index=False)
    print(f"\n✅ Cleaned data saved to {output_file}")
    
    return cleaned_df

if __name__ == "__main__":
    cleaned_df = run_data_cleaning() 