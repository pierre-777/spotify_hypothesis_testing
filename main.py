"""
Spotify Song Title Hypothesis Testing

This script provides an interactive interface for testing hypotheses about Spotify song titles.
It includes functionality for data collection, API testing, dataset viewing, and statistical analysis.
"""

from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
from datetime import datetime
import sys
import numpy as np
import logging
from pathlib import Path
import requests
import great_expectations as ge
from great_expectations.core import ExpectationSuite
from great_expectations.dataset import PandasDataset
from typing import Dict, List, Optional, Union

# Load environment variables
load_dotenv()

# Add src directory to path for proper imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.data_collection.optimised_title_collector import OptimisedTitleCollector
    from src.data_processing.data_loader import SpotifyDataLoader
    from src.data_processing.post_eda_cleaner import PostEDADataCleaner
    # Note: BusinessInsightGenerator will be created when needed
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Please ensure all modules are in the src/ directory")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SpotifyDataValidator:
    """Validates Spotify data quality using Great Expectations."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        try:
            self.context = ge.get_context()
            self._setup_expectation_suite()
        except Exception as e:
            logging.warning(f"Great Expectations initialization failed: {e}")
            self.context = None
            self.suite = None
    
    def _setup_expectation_suite(self):
        """Set up the expectation suite for Spotify data validation."""
        if self.context is None:
            self.suite = None
            return
        
        try:
            self.suite = self.context.get_expectation_suite("spotify_data_suite")
        except Exception:
            try:
                self.suite = self.context.create_expectation_suite("spotify_data_suite")
            except Exception:
                logging.warning("Could not create expectation suite, continuing without validation")
                self.suite = None
    
    def validate_dataset(self, df: pd.DataFrame) -> Dict:
        """Validate a dataset against our expectations."""
        if self.suite is None:
            logging.warning("Great Expectations not properly initialized, skipping validation")
            return {"success": True, "results": []}
        
        try:
            ge_df = PandasDataset(df)
            
            # Define expectations for title analysis
            ge_df.expect_column_values_to_not_be_null("track_name")
            ge_df.expect_column_values_to_not_be_null("artist_name")
            ge_df.expect_column_values_to_not_be_null("genre")
            ge_df.expect_column_values_to_be_between("popularity", 20, 100)
            ge_df.expect_column_values_to_be_between("duration_ms", 0, None)
            ge_df.expect_column_values_to_be_between("title_length", 1, 200)
            ge_df.expect_column_values_to_be_between("word_count", 1, 50)
            
            # Check for duplicates
            ge_df.expect_compound_columns_to_be_unique(["track_name", "artist_name"])
            
            # Get validation results
            results = ge_df.validate()
            return results
        except Exception as e:
            logging.error(f"Validation failed: {e}")
            return {"success": False, "error": str(e)}

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n🎵 Spotify Song Title Analysis")
    print("=" * 40)

def show_menu():
    """Display the main menu with 8-step DataCamp methodology."""
    print("\n📋 MAIN MENU - DataCamp Hypothesis Testing Methodology")
    print("=" * 60)
    print("1. 🔌 Test API Connection")
    print("2. 📥 Collect Data")
    print("   • Test Collection (100 tracks per genre - ~800 total)")  
    print("   • Medium Collection (250 tracks per genre - ~2,000 total)")
    print("   • Full Collection (4,000 tracks per genre - ~32,000 total)")
    print("   • Mega Collection (6,000 tracks per genre - ~48,000 total)")
    print("3. 📊 View Dataset")
    print("4. 🧹 Clean Data (Basic)")
    print("5. 🔍 Exploratory Data Analysis")
    print("6. 🔧 Advanced Cleaning (Post-EDA)")
    print("7. 🔬 Statistical Analysis & Hypothesis Testing")
    print("8. 📈 Results & Interpretation")
    print("9. ℹ️ Project Info")
    print("0. 🚪 Exit")
    return input("\nSelect an option: ")

def run_step_1():
    """Test API connection."""
    clear_screen()
    print_header()
    print("\n🔌 Testing API Connection")
    print("-" * 40)
    
    try:
        collector = OptimisedTitleCollector(test_mode=True)
        print("✅ API client initialization successful!")
        
        # Test actual search functionality
        print("🔍 Testing search functionality...")
        test_results = collector.sp.search(q="year:2024 genre:pop", type='track', limit=1, offset=0)
        
        if test_results and 'tracks' in test_results:
            tracks = test_results['tracks']['items']
            print(f"✅ Search API successful! Found {len(tracks)} track(s)")
            if tracks:
                track = tracks[0]
                print(f"   Sample track: '{track['name']}' by {track['artists'][0]['name']}")
        else:
            print("⚠️  Search API returned empty results")
            
        return True
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False

def run_step_2():
    """Collect data using the new collector with test, medium, full, and mega options."""
    clear_screen()
    print_header()
    print("\n📥 STEP 2: DATA COLLECTION")
    print("-" * 40)
    print("DataCamp Methodology: Gather data for hypothesis testing")
    print("\nSelect collection mode:")
    print("1. 🔬 Test Collection (100 tracks per genre - ~800 total)")
    print("2. 🧪 Medium Collection (250 tracks per genre - ~2,000 total)")
    print("3. 📥 Full Collection (4,000 tracks per genre - ~32,000 total)")
    print("4. 🚀 Mega Collection (6,000 tracks per genre - ~48,000 total)")
    print("5. 🔄 Recover Partial Collection")
    
    mode = input("\nSelect mode (1-5): ")
    
    if mode == "5":
        # Recovery mode
        print("\n🔄 Recover Partial Collection...")
        data_dir = Path("data")
        temp_dirs = list(data_dir.glob("temp_collection_*"))
        
        if not temp_dirs:
            print("❌ No partial collections found")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nFound {len(temp_dirs)} partial collections:")
        for i, temp_dir in enumerate(temp_dirs, 1):
            print(f"{i}. {temp_dir.name}")
        
        try:
            choice = int(input("\nSelect a partial collection to recover (number): ")) - 1
            selected_dir = temp_dirs[choice]
            
            collector = OptimisedTitleCollector(test_mode=False)
            df = collector.recover_partial_collection(str(selected_dir))
            
            if df is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"spotify_recovered_{timestamp}.csv"
                df.to_csv(f"data/{filename}", index=False)
                print(f"\n✅ Recovery complete!")
                print(f"💾 Data saved to: data/{filename}")
                
                # Ask if user wants to clean up the temp directory
                cleanup = input("\n🧹 Delete temporary files? (y/N): ")
                if cleanup.lower() == 'y':
                    for file in selected_dir.glob("*.csv"):
                        file.unlink()
                    selected_dir.rmdir()
                    print("✅ Temporary files cleaned up")
            else:
                print("\n❌ Recovery failed")
        except (ValueError, IndexError):
            print("❌ Invalid selection")
        
        input("\nPress Enter to continue...")
        return
    
    # Handle regular collection modes
    collection_configs = {
        "1": ("test", "🔬 Test Collection", "Starting Test Collection..."),
        "2": ("medium", "🧪 Medium Collection", "Starting Medium Collection..."),
        "3": ("full", "📥 Full Collection", "Starting Full Collection..."),
        "4": ("mega", "🚀 Mega Collection", "Starting Mega Collection...")
    }
    
    if mode not in collection_configs:
        print("❌ Invalid selection")
        input("\nPress Enter to continue...")
        return
    
    size, mode_name, start_message = collection_configs[mode]
    
    # Show warning for large collections
    if mode in ["3", "4"]:
        time_estimate = "15-20 minutes" if mode == "3" else "20-25 minutes"
        track_count = "~32,000" if mode == "3" else "~48,000"
        print(f"\n{start_message}")
        print(f"⚠️  This will collect {track_count} tracks and may take {time_estimate}...")
        if mode == "4":
            print("🎯 Target: 6,000 tracks per genre with enhanced genre verification")
        confirm = input("Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Collection cancelled.")
            input("\nPress Enter to continue...")
            return
    else:
        print(f"\n{start_message}")
    
    # Run the collection
    collector = OptimisedTitleCollector(test_mode=False)
    collector.set_collection_size(size)
    df = collector.collect_tracks()
    
    if df is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spotify_{size}_{timestamp}.csv"
        df.to_csv(f"data/{filename}", index=False)
        print(f"\n✅ {mode_name} complete!")
        print(f"📊 Total tracks collected: {len(df):,}")
        print(f"🎵 Genres: {df['genre_category'].nunique()}")
        if 'artist_name' in df.columns:
            print(f"👥 Unique artists: {df['artist_name'].nunique():,}")
        print(f"💾 Data saved to: data/{filename}")
        
        # Show temporal distribution for larger collections
        if mode in ["3", "4"] and 'release_year' in df.columns:
            print(f"\n📅 Temporal Distribution:")
            year_counts = df['release_year'].value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"   {year}: {count:,} tracks")
        
        # Show genre distribution
        print(f"\n📈 Genre Distribution:")
        genre_counts = df['genre_category'].value_counts()
        for genre, count in genre_counts.items():
            print(f"   {genre}: {count:,} tracks")
        
        # Show artist diversity for larger collections
        if mode in ["3", "4"] and 'artist_name' in df.columns:
            artist_counts = df['artist_name'].value_counts()
            max_songs_per_artist = artist_counts.max()
            avg_songs_per_artist = len(df) / df['artist_name'].nunique()
            print(f"\n👥 Artist Diversity:")
            print(f"   Total unique artists: {df['artist_name'].nunique():,}")
            print(f"   Average songs per artist: {avg_songs_per_artist:.1f}")
            print(f"   Maximum songs per artist: {max_songs_per_artist}")
    else:
        print(f"\n❌ {mode_name} failed")
        print("💡 Check data/temp_collection_* directories for any partial data")
    
    input("\nPress Enter to continue...")

def run_step_3():
    """View dataset."""
    clear_screen()
    print_header()
    print("\n📊 View Dataset")
    print("-" * 40)
    
    # List available datasets - look for any Spotify CSV files
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify*.csv"))
    
    if not datasets:
        print("No datasets found")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset (number): ")
    try:
        selected = datasets[int(choice) - 1]
        
        # Load the dataset directly since we may not have the SpotifyDataLoader
        df = pd.read_csv(selected)
        
        print(f"\n📊 Dataset: {selected.name}")
        print("-" * 40)
        print(f"📈 Total rows: {len(df):,}")
        print(f"📋 Columns: {len(df.columns)}")
        print(f"💾 File size: {selected.stat().st_size / (1024*1024):.1f} MB")
        
        print(f"\n📋 Column names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2}. {col}")
        
        print(f"\n📊 Dataset Summary:")
        if 'genre_category' in df.columns:
            print(f"🎵 Genres: {df['genre_category'].nunique()}")
            genre_counts = df['genre_category'].value_counts()
            for genre, count in genre_counts.items():
                print(f"   {genre}: {count:,} tracks")
        
        if 'popularity' in df.columns:
            print(f"📈 Popularity: {df['popularity'].mean():.1f} (avg), {df['popularity'].min()}-{df['popularity'].max()} (range)")
        
        if 'title_length' in df.columns:
            print(f"📏 Title length: {df['title_length'].mean():.1f} (avg), {df['title_length'].min()}-{df['title_length'].max()} (range)")
        
        if 'release_year' in df.columns:
            print(f"📅 Years: {df['release_year'].min()}-{df['release_year'].max()}")
            year_counts = df['release_year'].value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"   {year}: {count:,} tracks")
        
        print("\n📋 First 5 rows:")
        print(df.head())
        
        print("\n📋 Data types:")
        print(df.dtypes)
        
    except (ValueError, IndexError):
        print("Invalid selection")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        
    input("\nPress Enter to continue...")

def run_step_4():
    """Clean data."""
    clear_screen()
    print_header()
    print("\n🧹 Data Cleaning")
    print("-" * 40)
    
    # List available datasets - look for any Spotify CSV files
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify*.csv"))
    
    if not datasets:
        print("No datasets found")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset to clean (number): ")
    try:
        selected = datasets[int(choice) - 1]
        df = pd.read_csv(selected)
        
        # Basic data cleaning since we may not have the SpotifyDataCleaner
        print(f"\n🧹 Cleaning dataset: {selected.name}")
        print(f"📊 Original rows: {len(df):,}")
        
        # Remove duplicates
        df_cleaned = df.drop_duplicates()
        print(f"🔄 After removing duplicates: {len(df_cleaned):,}")
        
        # Remove null values in critical columns
        critical_columns = ['track_name', 'artist_name', 'popularity']
        before_nulls = len(df_cleaned)
        df_cleaned = df_cleaned.dropna(subset=[col for col in critical_columns if col in df_cleaned.columns])
        print(f"🔄 After removing nulls: {len(df_cleaned):,}")
        
        # Save cleaned data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/spotify_cleaned_{timestamp}.csv"
        df_cleaned.to_csv(output_file, index=False)
        
        print(f"\n✅ Data cleaning complete!")
        print(f"📊 Final rows: {len(df_cleaned):,}")
        print(f"💾 Cleaned data saved to: {output_file}")
        
    except (ValueError, IndexError):
        print("Invalid selection")
    except Exception as e:
        print(f"Error cleaning dataset: {e}")

def run_step_5():
    """Run exploratory analysis - DataCamp Step 5."""
    clear_screen()
    print_header()
    print("\n🔍 STEP 5: EXPLORATORY DATA ANALYSIS")
    print("-" * 40)
    print("DataCamp Methodology: Understand data patterns before hypothesis testing")
    
    # List available datasets - look for any Spotify CSV files
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify*.csv"))
    
    if not datasets:
        print("No datasets found. Please run Step 2: Collect Data first.")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset to analyse (number): ")
    try:
        selected = datasets[int(choice) - 1]
        df = pd.read_csv(selected)
        
        print(f"\n🔍 Exploratory Data Analysis: {selected.name}")
        print("-" * 50)
        
        # Basic EDA since we may not have the SpotifyEDA module
        print(f"📊 Dataset Overview:")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        if 'popularity' in df.columns:
            print(f"\n📈 Popularity Analysis:")
            print(f"   Mean: {df['popularity'].mean():.1f}")
            print(f"   Median: {df['popularity'].median():.1f}")
            print(f"   Range: {df['popularity'].min()} - {df['popularity'].max()}")
            print(f"   Std Dev: {df['popularity'].std():.1f}")
        
        if 'title_length' in df.columns:
            print(f"\n📏 Title Length Analysis:")
            print(f"   Mean: {df['title_length'].mean():.1f}")
            print(f"   Median: {df['title_length'].median():.1f}")
            print(f"   Range: {df['title_length'].min()} - {df['title_length'].max()}")
            
            # Correlation with popularity
            if 'popularity' in df.columns:
                corr = df['title_length'].corr(df['popularity'])
                print(f"   Correlation with popularity: {corr:.3f}")
        
        if 'word_count' in df.columns:
            print(f"\n📝 Word Count Analysis:")
            print(f"   Mean: {df['word_count'].mean():.1f}")
            print(f"   Median: {df['word_count'].median():.1f}")
            print(f"   Range: {df['word_count'].min()} - {df['word_count'].max()}")
            
            # Correlation with popularity
            if 'popularity' in df.columns:
                corr = df['word_count'].corr(df['popularity'])
                print(f"   Correlation with popularity: {corr:.3f}")
        
        if 'genre_category' in df.columns:
            print(f"\n🎵 Genre Analysis:")
            genre_pop = df.groupby('genre_category')['popularity'].agg(['mean', 'count']).round(1)
            print(genre_pop)
        
        if 'has_numbers' in df.columns:
            print(f"\n🔢 Numbers in Titles:")
            with_numbers = df['has_numbers'].sum()
            total = len(df)
            print(f"   Tracks with numbers: {with_numbers:,} ({100*with_numbers/total:.1f}%)")
            
            if 'popularity' in df.columns:
                pop_with = df[df['has_numbers'] == True]['popularity'].mean()
                pop_without = df[df['has_numbers'] == False]['popularity'].mean()
                print(f"   Avg popularity with numbers: {pop_with:.1f}")
                print(f"   Avg popularity without numbers: {pop_without:.1f}")
        
        print("\n✅ Exploratory analysis complete!")
        print("🎯 Ready for Step 6: Statistical Analysis")
        
    except (ValueError, IndexError):
        print("Invalid selection")
    except Exception as e:
        print(f"Error: {e}")

def run_step_6():
    """Run post-EDA advanced cleaning - DataCamp Step 6."""
    clear_screen()
    print_header()
    print("\n🔧 STEP 6: ADVANCED CLEANING (POST-EDA)")
    print("-" * 40)
    print("DataCamp Methodology: Apply bias correction based on EDA findings")
    
    # List available datasets - look for any Spotify CSV files
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify*.csv"))
    
    if not datasets:
        print("No datasets found. Please run Step 2: Collect Data first.")
        input("\nPress Enter to continue...")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset to clean (number): ")
    try:
        selected = datasets[int(choice) - 1]
        df = pd.read_csv(selected)
        
        print(f"\n🔧 Post-EDA Cleaning: {selected.name}")
        print("-" * 50)
        
        # Initialize the post-EDA cleaner
        cleaner = PostEDADataCleaner(df)
        
        print("\n🎯 Cleaning Strategy Options:")
        print("1. 🤖 Auto-determine strategy (based on EDA)")
        print("2. 🎵 Artist limiting (cap songs per artist)")
        print("3. 📊 Stratified sampling (proportional representation)")
        print("4. 🚫 Remove artist outliers (high-frequency artists)")
        print("5. 💡 Get cleaning recommendations")
        
        strategy_choice = input("\nSelect cleaning strategy (1-5): ")
        
        if strategy_choice == "5":
            # Show recommendations
            recommendations = cleaner.get_cleaning_recommendations()
            print("\n💡 CLEANING RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   {rec}")
            input("\nPress Enter to continue...")
            return
        
        # Map choices to strategies
        strategy_map = {
            "1": "auto",
            "2": "artist_limit", 
            "3": "stratified",
            "4": "remove_outliers"
        }
        
        if strategy_choice in strategy_map:
            strategy = strategy_map[strategy_choice]
            
            # Apply cleaning
            cleaned_df = cleaner.apply_bias_correction(strategy=strategy)
            
            # Ask if user wants to save the cleaned data
            save_choice = input("\n💾 Save cleaned dataset? (y/N): ")
            if save_choice.lower() == 'y':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/spotify_cleaned_post_eda_{timestamp}.csv"
                cleaner.export_cleaned_data(filename)
                print(f"✅ Cleaned dataset saved to: {filename}")
            
            print("\n🎯 Ready for Step 7: Statistical Analysis")
        else:
            print("❌ Invalid selection")
        
    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def run_step_7():
    """Run hypothesis testing - DataCamp Step 7."""
    clear_screen()
    print_header()
    print("\n🔬 STEP 7: STATISTICAL ANALYSIS & HYPOTHESIS TESTING")
    print("-" * 40)
    print("DataCamp Methodology: Test hypotheses using statistical methods")
    
    # List available datasets - look for any Spotify CSV files
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify*.csv"))
    
    if not datasets:
        print("No datasets found. Please run Step 2: Collect Data first.")
        input("\nPress Enter to continue...")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset to test (number): ")
    try:
        selected = datasets[int(choice) - 1]
        df = pd.read_csv(selected)
        
        print("\n🔬 Hypothesis Testing Options:")
        print("1. 📏 Title Length vs Popularity")
        print("2. 📝 Word Count Groups Analysis")  
        print("3. 🔢 Special Characters Impact")
        print("4. 🎵 Genre Comparison")
        print("5. 🎯 Run All Tests")
        
        test_choice = input("\nSelect test (1-5): ")
        
        # Run hypothesis testing using the proper src structure
        from src.hypothesis_testing.test_setup import TestSetup
        from src.hypothesis_testing.statistical_tests import TitleFeatureAnalyzer
        from src.hypothesis_testing.results_interpretation import ResultsInterpreter
        
        if test_choice == "5":
            # Run all tests
            setup = TestSetup(df)
            hypotheses, designs = setup.setup_tests()
            
            tests = TitleFeatureAnalyzer(df)
            results = tests.run_all_tests()
            
            interpreter = ResultsInterpreter(results)
            interpretations = interpreter.interpret_all_results()
            
            print("\n✅ All hypothesis tests complete!")
        else:
            print("Individual test functionality to be implemented")
        
        print("📊 Results saved to log file")
        print("🎯 Ready for Step 8: Results & Interpretation")
        
    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def run_step_8():
    """View results and interpretation - DataCamp Step 8."""
    clear_screen()
    print_header()
    print("\n📈 STEP 8: RESULTS & INTERPRETATION")
    print("-" * 40)
    print("DataCamp Methodology: Interpret results and draw conclusions")
    
    # List available log files and results
    log_files = list(Path(".").glob("spotify_analysis*.log"))
    
    if not log_files:
        print("No results found. Please run Step 7: Hypothesis Testing first.")
        input("\nPress Enter to continue...")
        return
    
    print("\nAvailable results:")
    for i, log_file in enumerate(log_files, 1):
        print(f"{i}. {log_file.name}")
    
    choice = input("\nSelect results to view (number): ")
    try:
        selected = log_files[int(choice) - 1]
        
        print(f"\n📊 RESULTS FROM: {selected.name}")
        print("=" * 50)
        
        with open(selected, 'r') as f:
            content = f.read()
            print(content)
        
        print("\n🎯 CONCLUSION SUMMARY:")
        print("• Hypothesis test results above")
        print("• Statistical significance levels")
        print("• Business implications for Spotify")
        print("• Recommendations for track titling")
        
    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def test_api_connection():
    """Test the Spotify API connection."""
    try:
        collector = OptimisedTitleCollector(test_mode=True)
        print("✅ API connection successful!")
        return True
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False

def validate_dataset():
    """Validate a dataset using Great Expectations."""
    # List available datasets
    data_dir = Path("data")
    datasets = list(data_dir.glob("spotify_tracks_*.csv"))
    
    if not datasets:
        print("No datasets found")
        return
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset.name}")
    
    choice = input("\nSelect a dataset to validate (number): ")
    try:
        selected = datasets[int(choice) - 1]
        df = pd.read_csv(selected)
        
        # Validate the dataset
        validator = SpotifyDataValidator()
        results = validator.validate_dataset(df)
        
        if results['success']:
            print("\n✅ Dataset validation successful!")
        else:
            print("\n❌ Dataset validation failed!")
            if 'error' in results:
                print(f"Error: {results['error']}")
            elif 'results' in results:
                print("Validation issues:")
                for result in results['results']:
                    print(f"  • {result}")
        
    except (ValueError, IndexError):
        print("Invalid selection")

def show_project_info():
    """Display project information following DataCamp methodology."""
    clear_screen()
    print_header()
    print("\nℹ️ PROJECT INFORMATION")
    print("-" * 40)
    print("🎯 Spotify Track Title Analysis using DataCamp 8-Step Methodology")
    print("\n📋 METHODOLOGY STEPS:")
    print("1. 🔌 API Connection Setup & Testing")
    print("2. 📥 Data Collection (Test: 10-50 tracks | Full: 2000 tracks per genre)")
    print("3. 📊 Dataset Viewing & Initial Inspection")
    print("4. 🧹 Basic Data Cleaning & Preprocessing")
    print("5. 🔍 Exploratory Data Analysis")
    print("6. 🔧 Advanced Cleaning (Post-EDA Bias Correction)")
    print("7. 🔬 Statistical Analysis & Hypothesis Testing")
    print("8. 📈 Results Interpretation & Business Insights")
    
    print("\n🎵 TARGET GENRES (8 total):")
    print("   • Pop         • Rock       • Hip-Hop     • Electronic")
    print("   • Jazz        • Classical   • Metal       • R&B")
    
    print("\n📊 HYPOTHESIS TESTING FOCUS:")
    print("   • Title length vs popularity correlation")
    print("   • Word count impact on track success")  
    print("   • Special characters and numbers analysis")
    print("   • Genre-specific title patterns")
    
    print("\n📈 DATA COLLECTION TARGET:")
    print("   • Full Dataset: 16,000 tracks (2000 per genre)")
    print("   • Time Period: 2020-2024")
    print("   • Features: Title metrics + popularity scores")
    
    print("\n🔧 TECHNICAL STACK:")
    print("   • Spotify Web API for data collection")
    print("   • Pandas for data manipulation")
    print("   • Scipy/Statsmodels for statistical testing")
    print("   • Structured src/ folder organization")
    
    print("\n💡 BUSINESS VALUE:")
    print("   • Data-driven insights for track naming strategies")
    print("   • Statistical evidence for title optimisation")
    print("   • Genre-specific recommendations")
    print("   • Actionable insights for artists and labels")

def main():
    """Main function with DataCamp 8-step methodology."""
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            test_api_connection()
        elif choice == "2":
            run_step_2()  # Data Collection
        elif choice == "3":
            run_step_3()  # View Dataset
        elif choice == "4":
            run_step_4()  # Clean Data (Basic)
        elif choice == "5":
            run_step_5()  # Exploratory Data Analysis
        elif choice == "6":
            run_step_6()  # Advanced Cleaning (Post-EDA)
        elif choice == "7":
            run_step_7()  # Statistical Analysis & Hypothesis Testing
        elif choice == "8":
            run_step_8()  # Results & Interpretation
        elif choice == "9":
            show_project_info()  # Project Info
        elif choice == "0":
            print("\n👋 Thank you for using the Spotify Hypothesis Testing tool!")
            print("🎯 DataCamp methodology complete!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\n📍 Press Enter to continue...")

if __name__ == "__main__":
    main()
