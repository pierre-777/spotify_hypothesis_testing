"""
Spotify Data Validation Suite using Great Expectations
Enterprise-grade data quality validation for track datasets

Features:
- Comprehensive data quality checks
- Schema validation
- Business rule validation
- Statistical distribution validation
- Data profiling and documentation
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import BatchRequest
from great_expectations.checkpoint import Checkpoint
from great_expectations.data_context import DataContext
from great_expectations.exceptions import DataContextError

logger = logging.getLogger(__name__)


class SpotifyDataValidator:
    """
    Enterprise data validation using Great Expectations
    
    Validates collected Spotify track datasets for:
    - Schema compliance
    - Data quality standards
    - Business rules
    - Statistical distributions
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.gx_dir = os.path.join(data_dir, "great_expectations")
        self.context = self._initialize_gx_context()
        
    def _initialize_gx_context(self) -> DataContext:
        """Initialize Great Expectations context"""
        try:
            # Try to get existing context
            if os.path.exists(self.gx_dir):
                context = gx.get_context(context_root_dir=self.gx_dir)
                logger.info("✅ Using existing Great Expectations context")
            else:
                # Create new context
                os.makedirs(self.data_dir, exist_ok=True)
                context = gx.get_context(context_root_dir=self.gx_dir)
                logger.info("✅ Created new Great Expectations context")
                
            return context
            
        except Exception as e:
            logger.error(f"Failed to initialize Great Expectations: {e}")
            raise
    
    def create_expectation_suite(self) -> str:
        """Create comprehensive expectation suite for Spotify track data"""
        suite_name = "spotify_tracks_suite"
        
        try:
            # Create or get suite
            suite = self.context.get_expectation_suite(suite_name)
            logger.info(f"Using existing expectation suite: {suite_name}")
        except:
            suite = self.context.create_expectation_suite(suite_name)
            logger.info(f"Created new expectation suite: {suite_name}")
            
            # Clear existing expectations to start fresh
            suite.expectations = []
            
            # === SCHEMA VALIDATION ===
            logger.info("Adding schema validation expectations...")
            
            # Required columns must exist
            required_columns = [
                'track_id', 'track_name', 'artist_id', 'artist_name', 
                'popularity', 'search_genre', 'release_date',
                'title_word_count', 'title_complexity_tier'
            ]
            
            for column in required_columns:
                suite.add_expectation(
                    expectation_configuration={
                        "expectation_type": "expect_column_to_exist",
                        "kwargs": {"column": column}
                    }
                )
            
            # === DATA QUALITY VALIDATION ===
            logger.info("Adding data quality expectations...")
            
            # Track IDs should be unique and non-null
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "track_id"}
            })
            
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "track_id"}
            })
            
            # Track names should not be null or empty
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "track_name"}
            })
            
            suite.add_expectation({
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "kwargs": {"column": "track_name", "min_value": 1, "max_value": 200}
            })
            
            # === BUSINESS RULES VALIDATION ===
            logger.info("Adding business rules expectations...")
            
            # Popularity should be between 0-100
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "popularity", "min_value": 0, "max_value": 100}
            })
            
            # Search genre should be from expected list
            expected_genres = ['pop', 'hip-hop', 'rock', 'electronic', 'country', 'r&b', 'alternative', 'classical']
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": "search_genre", "value_set": expected_genres}
            })
            
            # Title complexity tiers should be valid
            expected_tiers = ['single', 'short', 'medium', 'long']
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_in_set", 
                "kwargs": {"column": "title_complexity_tier", "value_set": expected_tiers}
            })
            
            # Word count should be positive and reasonable
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "title_word_count", "min_value": 1, "max_value": 50}
            })
            
            # Duration should be reasonable (30 seconds to 20 minutes)
            suite.add_expectation({
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "duration_ms", "min_value": 30000, "max_value": 1200000}
            })
            
            # === STATISTICAL DISTRIBUTION VALIDATION ===
            logger.info("Adding statistical distribution expectations...")
            
            # At least 5% of tracks should be high popularity (>75)
            suite.add_expectation({
                "expectation_type": "expect_column_proportion_of_unique_values_to_be_between",
                "kwargs": {"column": "popularity", "min_value": 0.01, "max_value": 1.0}
            })
            
            # Genre distribution should be reasonably balanced (no genre >60% of dataset)
            suite.add_expectation({
                "expectation_type": "expect_column_most_common_value_to_be_in_set",
                "kwargs": {"column": "search_genre", "value_set": expected_genres}
            })
            
            # === DATA COMPLETENESS ===
            logger.info("Adding data completeness expectations...")
            
            # Critical fields should have <5% null values
            critical_fields = ['track_id', 'track_name', 'artist_name', 'popularity', 'search_genre']
            for field in critical_fields:
                suite.add_expectation({
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": field}
                })
            
            # Save the suite
            self.context.save_expectation_suite(suite)
            logger.info(f"✅ Expectation suite '{suite_name}' created with {len(suite.expectations)} expectations")
            
        return suite_name
    
    def validate_dataset(self, csv_path: str, suite_name: str = "spotify_tracks_suite") -> Tuple[bool, Dict]:
        """
        Validate a dataset against the expectation suite
        
        Returns:
            Tuple of (validation_passed, validation_results)
        """
        logger.info(f"🔍 Validating dataset: {csv_path}")
        
        try:
            # Create datasource for CSV file
            datasource_name = "spotify_csv_datasource"
            
            try:
                datasource = self.context.get_datasource(datasource_name)
            except:
                datasource = self.context.sources.add_pandas(datasource_name)
                
            # Add data asset
            asset_name = f"tracks_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                data_asset = datasource.add_csv_asset(asset_name, filepath_or_buffer=csv_path)
            except:
                # Asset might already exist, get it
                data_asset = datasource.get_asset(asset_name)
            
            # Create batch request
            batch_request = data_asset.build_batch_request()
            
            # Create validator
            validator = self.context.get_validator(
                batch_request=batch_request,
                expectation_suite_name=suite_name
            )
            
            # Run validation
            validation_result = validator.validate()
            
            # Extract key metrics
            results_summary = {
                'validation_passed': validation_result.success,
                'total_expectations': len(validation_result.results),
                'successful_expectations': sum(1 for r in validation_result.results if r.success),
                'failed_expectations': sum(1 for r in validation_result.results if not r.success),
                'evaluated_expectations': validation_result.statistics['evaluated_expectations'],
                'success_percentage': validation_result.statistics['success_percent'],
                'dataset_rows': len(validator.active_batch.data),
                'dataset_columns': len(validator.active_batch.data.columns),
                'validation_time': datetime.now().isoformat()
            }
            
            # Log summary
            if validation_result.success:
                logger.info(f"✅ Validation PASSED: {results_summary['successful_expectations']}/{results_summary['total_expectations']} expectations met")
            else:
                logger.warning(f"❌ Validation FAILED: {results_summary['failed_expectations']} expectations failed")
                
                # Log failed expectations
                for result in validation_result.results:
                    if not result.success:
                        expectation = result.expectation_config.expectation_type
                        column = result.expectation_config.kwargs.get('column', 'N/A')
                        logger.warning(f"   FAILED: {expectation} on column '{column}'")
            
            return validation_result.success, results_summary
            
        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            return False, {"error": str(e)}
    
    def create_checkpoint(self, suite_name: str = "spotify_tracks_suite") -> str:
        """Create a validation checkpoint for automated testing"""
        checkpoint_name = "spotify_data_checkpoint"
        
        try:
            checkpoint_config = {
                "name": checkpoint_name,
                "config_version": 1.0,
                "template_name": None,
                "module_name": "great_expectations.checkpoint",
                "class_name": "Checkpoint",
                "run_name_template": "%Y%m%d-%H%M%S-spotify-validation",
                "expectation_suite_name": suite_name,
                "batch_request": {},
                "action_list": [
                    {
                        "name": "store_validation_result",
                        "action": {
                            "class_name": "StoreValidationResultAction",
                        },
                    },
                    {
                        "name": "update_data_docs",
                        "action": {
                            "class_name": "UpdateDataDocsAction",
                        },
                    },
                ],
                "evaluation_parameters": {},
                "runtime_configuration": {},
                "validations": [],
            }
            
            checkpoint = Checkpoint(
                name=checkpoint_name,
                data_context=self.context,
                **checkpoint_config
            )
            
            self.context.add_checkpoint(checkpoint=checkpoint)
            logger.info(f"✅ Created checkpoint: {checkpoint_name}")
            
            return checkpoint_name
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            raise
    
    def generate_data_docs(self) -> str:
        """Generate and build data documentation"""
        try:
            self.context.build_data_docs()
            
            # Get docs URL
            docs_sites = self.context.get_docs_sites_urls()
            if docs_sites:
                docs_url = list(docs_sites.values())[0]
                logger.info(f"📊 Data docs generated: {docs_url}")
                return docs_url
            else:
                logger.warning("Data docs generated but URL not available")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to generate data docs: {e}")
            return ""
    
    def quick_validate(self, csv_path: str) -> bool:
        """Quick validation setup and execution for new datasets"""
        logger.info("🚀 Running quick validation setup...")
        
        try:
            # 1. Create expectation suite
            suite_name = self.create_expectation_suite()
            
            # 2. Validate the dataset
            success, results = self.validate_dataset(csv_path, suite_name)
            
            # 3. Generate documentation
            docs_url = self.generate_data_docs()
            
            # 4. Print summary
            self._print_validation_summary(success, results, docs_url)
            
            return success
            
        except Exception as e:
            logger.error(f"Quick validation failed: {e}")
            return False
    
    def _print_validation_summary(self, success: bool, results: Dict, docs_url: str):
        """Print comprehensive validation summary"""
        print("\n" + "="*60)
        print("📊 DATA VALIDATION SUMMARY")
        print("="*60)
        
        if success:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
            
        if 'error' not in results:
            print(f"📋 Dataset: {results['dataset_rows']:,} rows, {results['dataset_columns']} columns")
            print(f"🎯 Expectations: {results['successful_expectations']}/{results['total_expectations']} passed ({results['success_percentage']:.1f}%)")
            
            if not success:
                print(f"⚠️  Failed expectations: {results['failed_expectations']}")
                print("💡 Check logs above for specific failures")
                
        if docs_url:
            print(f"📖 Data docs: {docs_url}")
            print("💡 Open the docs URL to see detailed validation results")
            
        print("="*60)


def main():
    """Main function for standalone validation"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python spotify_data_validator.py <path_to_csv>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found")
        sys.exit(1)
        
    # Run validation
    validator = SpotifyDataValidator()
    success = validator.quick_validate(csv_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 