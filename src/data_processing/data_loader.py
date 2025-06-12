"""
Data Loading Module
Step 2: Load and validate data from CSV files
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyDataLoader:
    """Load and validate Spotify data from CSV files"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize data loader with data directory"""
        self.data_dir = Path(data_dir)
        self.df = None
        self.summary = {}
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """
        Load data from CSV file
        Args:
            filename: Name of CSV file in data directory
        Returns:
            Loaded DataFrame
        """
        logger.info(f"📂 Loading data from {filename}")
        
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path)
            logger.info(f"✅ Successfully loaded {len(self.df)} rows")
            return self.df
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            raise
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics for loaded data
        Returns:
            Dictionary of summary statistics
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        summary = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'title_length_range': (self.df['title_length'].min(), self.df['title_length'].max()) if 'title_length' in self.df.columns else None,
            'word_count_range': (self.df['word_count'].min(), self.df['word_count'].max()) if 'word_count' in self.df.columns else None,
            'popularity_range': (self.df['popularity'].min(), self.df['popularity'].max()) if 'popularity' in self.df.columns else None,
            'release_year_range': (self.df['release_year'].min(), self.df['release_year'].max()) if 'release_year' in self.df.columns else None,
            'genres': self.df['genre_category'].unique().tolist() if 'genre_category' in self.df.columns else [],
            'has_numbers': self.df['has_numbers'].value_counts().to_dict() if 'has_numbers' in self.df.columns else {},
            'has_special_chars': self.df['has_special_chars'].value_counts().to_dict() if 'has_special_chars' in self.df.columns else {}
        }
        
        self.summary = summary
        return summary
    
    def print_summary(self):
        """Print summary statistics for loaded data"""
        if not self.summary:
            self.get_summary()
        
        print("\n📊 DATA SUMMARY")
        print("=" * 40)
        print(f"📈 Total rows: {self.summary['rows']:,}")
        print(f"📋 Total columns: {self.summary['columns']}")
        
        if self.summary['title_length_range']:
            print(f"📏 Title length range: {self.summary['title_length_range'][0]:.1f}-{self.summary['title_length_range'][1]:.1f}")
        
        if self.summary['word_count_range']:
            print(f"📝 Word count range: {self.summary['word_count_range'][0]:.1f}-{self.summary['word_count_range'][1]:.1f}")
        
        if self.summary['popularity_range']:
            print(f"⭐ Popularity range: {self.summary['popularity_range'][0]}-{self.summary['popularity_range'][1]}")
        
        if self.summary['release_year_range']:
            print(f"📅 Release year range: {self.summary['release_year_range'][0]}-{self.summary['release_year_range'][1]}")
        
        if self.summary['genres']:
            print(f"\n🎵 Genres ({len(self.summary['genres'])}):")
            for genre in sorted(self.summary['genres']):
                print(f"   • {genre}")
        
        if self.summary['has_numbers']:
            print("\n🔢 Title numbers:")
            for has_numbers, count in self.summary['has_numbers'].items():
                print(f"   • {'Has numbers' if has_numbers else 'No numbers'}: {count:,}")
        
        if self.summary['has_special_chars']:
            print("\n🔤 Special characters:")
            for has_chars, count in self.summary['has_special_chars'].items():
                print(f"   • {'Has special chars' if has_chars else 'No special chars'}: {count:,}")
        
        print("\n❓ Missing values:")
        for col, count in self.summary['missing_values'].items():
            if count > 0:
                print(f"   • {col}: {count:,}")
    
    def get_key_columns(self) -> list:
        """Get list of key columns for analysis"""
        return ['track_name', 'artist_name', 'popularity', 'title_length', 'word_count', 'has_numbers', 'has_special_chars', 'genre_category']

def run_data_loading():
    """Main function to run data loading"""
    print("\n📂 STEP 2: DATA LOADING")
    print("=" * 50)
    
    loader = SpotifyDataLoader()
    
    # Load data
    df = loader.load_data("spotify_tracks.csv")
    
    # Print summary
    loader.print_summary()
    
    return df

if __name__ == "__main__":
    df = run_data_loading() 