"""
Test Setup Module
Step 4: Set up statistical tests for hypothesis testing
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy import stats

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Hypothesis:
    """Data class for hypothesis definition"""
    name: str
    description: str
    null_hypothesis: str
    alternative_hypothesis: str
    test_type: str
    alpha: float = 0.05

@dataclass
class AnalysisDesign:
    """Data class for analysis design"""
    name: str
    description: str
    test_method: str
    assumptions: List[str]
    effect_size: str
    sample_size: Dict[str, int]

class TestSetup:
    """Set up statistical tests for hypothesis testing"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize test setup with data"""
        self.df = df
        self.hypotheses = {}
        self.analysis_designs = {}
    
    def setup_tests(self) -> Tuple[Dict, Dict]:
        """
        Set up all statistical tests
        Returns:
            Tuple of (hypotheses, analysis_designs)
        """
        logger.info("🔬 Setting up statistical tests...")
        
        print("\n🔬 STEP 4: TEST SETUP")
        print("=" * 50)
        
        # 4.1: Define hypotheses
        self._define_hypotheses()
        
        # 4.2: Design analyses
        self._design_analyses()
        
        # 4.3: Check assumptions
        self._check_assumptions()
        
        logger.info("✅ Test setup completed")
        
        return self.hypotheses, self.analysis_designs
    
    def _define_hypotheses(self):
        """Define statistical hypotheses"""
        print("\n📋 HYPOTHESES")
        print("-" * 40)
        
        # Primary hypothesis: Title length vs popularity
        self.hypotheses['correlation'] = Hypothesis(
            name="Title Length-Popularity Correlation",
            description="Test the relationship between title length and track popularity",
            null_hypothesis="There is no correlation between title length and track popularity",
            alternative_hypothesis="There is a significant correlation between title length and track popularity",
            test_type="correlation"
        )
        
        # Secondary hypothesis: Word count groups
        self.hypotheses['group_comparison'] = Hypothesis(
            name="Word Count Group Comparison",
            description="Compare popularity across different word count groups",
            null_hypothesis="There is no difference in popularity between word count groups",
            alternative_hypothesis="There are significant differences in popularity between word count groups",
            test_type="group_comparison"
        )
        
        # Tertiary hypothesis: Title features
        self.hypotheses['anova'] = Hypothesis(
            name="Title Features ANOVA",
            description="Test differences in popularity based on title features",
            null_hypothesis="There is no difference in popularity based on title features",
            alternative_hypothesis="There are significant differences in popularity based on title features",
            test_type="anova"
        )
        
        # Display hypotheses
        for name, hypothesis in self.hypotheses.items():
            print(f"\n🔍 {hypothesis.name}:")
            print(f"   Description: {hypothesis.description}")
            print(f"   H₀: {hypothesis.null_hypothesis}")
            print(f"   H₁: {hypothesis.alternative_hypothesis}")
    
    def _design_analyses(self):
        """Design statistical analyses"""
        print("\n📊 ANALYSIS DESIGNS")
        print("-" * 40)
        
        # Get sample sizes
        sample_sizes = self._get_sample_sizes()
        
        # Correlation analysis
        self.analysis_designs['correlation'] = AnalysisDesign(
            name="Title Length-Popularity Correlation",
            description="Analyse the relationship between title length and popularity using Pearson correlation",
            test_method="Pearson correlation coefficient",
            assumptions=[
                "Linear relationship between variables",
                "Normally distributed variables",
                "No significant outliers"
            ],
            effect_size="Pearson's r",
            sample_size=sample_sizes
        )
        
        # Group comparison
        self.analysis_designs['group_comparison'] = AnalysisDesign(
            name="Word Count Group Comparison",
            description="Compare popularity across word count groups using ANOVA",
            test_method="One-way ANOVA",
            assumptions=[
                "Normally distributed groups",
                "Equal variances between groups",
                "Independent observations"
            ],
            effect_size="η² (eta-squared)",
            sample_size=sample_sizes
        )
        
        # Title features analysis
        self.analysis_designs['anova'] = AnalysisDesign(
            name="Title Features ANOVA",
            description="Analyse popularity differences based on title features using ANOVA",
            test_method="One-way ANOVA",
            assumptions=[
                "Normally distributed groups",
                "Equal variances between groups",
                "Independent observations"
            ],
            effect_size="η² (eta-squared)",
            sample_size=sample_sizes
        )
        
        # Display analysis designs
        for name, design in self.analysis_designs.items():
            print(f"\n📈 {design.name}:")
            print(f"   Method: {design.test_method}")
            print(f"   Effect Size: {design.effect_size}")
            print(f"   Assumptions:")
            for assumption in design.assumptions:
                print(f"     • {assumption}")
    
    def _check_assumptions(self):
        """Check statistical assumptions"""
        print("\n✅ ASSUMPTION CHECKS")
        print("-" * 40)
        
        # Check normality
        print("\n📊 Normality Tests:")
        
        # Title length normality
        title_stat, title_p = stats.shapiro(self.df['title_length'].sample(5000))
        print(f"   Title Length: statistic={title_stat:.4f}, p-value={title_p:.4f}")
        
        # Word count normality
        word_stat, word_p = stats.shapiro(self.df['word_count'].sample(5000))
        print(f"   Word Count: statistic={word_stat:.4f}, p-value={word_p:.4f}")
        
        # Popularity normality
        pop_stat, pop_p = stats.shapiro(self.df['popularity'].sample(5000))
        print(f"   Popularity: statistic={pop_stat:.4f}, p-value={pop_p:.4f}")
        
        # Check group sizes
        print("\n👥 Group Sizes:")
        if 'word_count_group' in self.df.columns:
            group_sizes = self.df['word_count_group'].value_counts()
            print("   Word Count Groups:")
            for group, size in group_sizes.items():
                print(f"     • {group}: {size:,}")
        
        if 'title_feature_group' in self.df.columns:
            feature_sizes = self.df['title_feature_group'].value_counts()
            print("   Title Feature Groups:")
            for group, size in feature_sizes.items():
                print(f"     • {group}: {size:,}")
    
    def _get_sample_sizes(self) -> Dict[str, int]:
        """Get sample sizes for each group"""
        sample_sizes = {
            'total': len(self.df),
            'by_genre': self.df['genre'].value_counts().to_dict() if 'genre' in self.df.columns else {}
        }
        
        # Add word count group sizes
        if 'word_count_group' in self.df.columns:
            sample_sizes.update(self.df['word_count_group'].value_counts().to_dict())
        
        # Add title feature group sizes
        if 'title_feature_group' in self.df.columns:
            sample_sizes.update(self.df['title_feature_group'].value_counts().to_dict())
        
        return sample_sizes

def run_test_setup():
    """Main function to run test setup"""
    print("\n🔬 STEP 4: TEST SETUP")
    print("=" * 50)
    
    # Load data
    from ..data_processing.data_loader import SpotifyDataLoader
    loader = SpotifyDataLoader()
    df = loader.load_data("spotify_tracks.csv")
    
    # Set up tests
    setup = TestSetup(df)
    hypotheses, analysis_designs = setup.setup_tests()
    
    return hypotheses, analysis_designs

if __name__ == "__main__":
    hypotheses, analysis_designs = run_test_setup() 