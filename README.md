# Spotify Song Title Hypothesis Testing

## 🎯 Project Overview

**Research Question**: Does song title complexity influence track popularity on Spotify?

**Primary Hypothesis**: Single-word song titles achieve different popularity metrics compared to multi-word titles, controlling for genre, artist popularity, and temporal factors.

**Business Value**: Understanding title optimisation strategies for music marketing, playlist curation, and A/B testing methodologies in the music industry.

---

## 📊 Research Design & Methodology

### Experimental Framework
- **Design**: Stratified sampling across 8 mainstream genres
- **Sample Size**: 16,000 tracks (2,000 per genre)
- **Primary Comparison**: Single-word vs Multi-word titles
- **Control Variables**: Genre, artist popularity, release timing, explicit content
- **Analysis Types**: t-tests, ANOVA, multiple regression, logistic regression

### Genres Selected
- **Pop** - Mainstream commercial appeal
- **Hip-Hop/Rap** - Contemporary urban music
- **Rock** - Traditional guitar-driven music
- **Electronic/Dance** - Electronic music & EDM
- **Country** - American country music
- **R&B/Soul** - Rhythm & blues
- **Alternative/Indie** - Independent & alternative rock
- **Classical** - Orchestral & contemporary classical

### Advanced Feature Engineering
**Title Complexity Variables:**
- Word count & character length
- Punctuation, numbers, parentheses usage
- Emotional content (positive/negative words)
- Common word ratios & average word length
- Complexity tiers: Single/Short/Medium/Long

**Control Variables:**
- Artist popularity & follower count
- Release year & temporal trends
- Genre classifications & sub-genres
- Track duration & explicit content
- Album context & preview availability

---

## 🚀 Technical Architecture

### Enterprise-Grade 3-Phase Optimised Collection System

**Phase 1: Bulk Track ID Collection (15-20 minutes)**
- High-throughput search queries across genre strategies
- Temporal filtering (2020-2024) for relevance
- Quality controls: max 3 tracks per artist
- Progress tracking with real-time metrics
- Robust error handling & exponential backoff

**Phase 2: Detailed Information Gathering (20-25 minutes)**
- Batch API calls for track & artist details
- Efficient artist data caching & deduplication
- Comprehensive metadata extraction
- Connection pooling & retry mechanisms
- Memory-optimised processing

**Phase 3: Feature Engineering & Analysis Preparation (3-8 minutes)**
- Advanced title complexity analysis & categorisation
- Derived variable creation with 19 features
- Interaction effect preparation
- Statistical readiness validation
- Data quality assurance

**Total Estimated Time: ~43 minutes** (370 tracks/minute)

---

## 🔬 Statistical Analysis Plan

### Primary Analyses
1. **Independent t-test**: Single-word vs multi-word title popularity
2. **One-way ANOVA**: Complexity tiers (Single/Short/Medium/Long)
3. **Multiple regression**: 19+ title features predicting popularity
4. **Logistic regression**: High popularity prediction (>75th percentile)

### Advanced Analyses
5. **Genre-stratified analysis**: 8 subgroup comparisons
6. **Interaction effects**: Title complexity × genre interactions
7. **Effect size calculations**: Cohen's d, eta-squared
8. **Power analysis**: Statistical significance validation

### Business Intelligence
9. **Temporal trends**: Title complexity evolution 2020-2024
10. **Artist tier analysis**: Title strategies by artist popularity
11. **Genre-specific insights**: Optimisation by music category
12. **Actionable recommendations**: Industry application strategies

---

## 📁 Project Structure

```
spotify_hypothesis_testing/
├── data/                              # Dataset storage
│   └── optimised_title_dataset_*.csv  # Production datasets
├── src/                               # Source code modules
│   ├── data_collection/               # Collection components
│   │   └── optimised_title_collector.py  # Main collection system
│   ├── data_processing/               # Processing utilities  
│   ├── hypothesis_testing/            # Statistical analysis
│   └── reporting/                     # Visualisation & reports
├── reports/                           # Generated analysis reports
├── main.py                           # Legacy API testing (reference)
├── requirements.txt                  # Python dependencies
├── .env                             # Environment variables (local)
└── README.md                        # This documentation
```

---

## 🛠️ Technology Stack

**Data Collection**:
- `spotipy` - Spotify Web API integration
- `pandas` - Data manipulation & analysis
- `tqdm` - Progress tracking & optimisation

**Statistical Analysis**:
- `scipy.stats` - Hypothesis testing
- `statsmodels` - Advanced regression modelling
- `scikit-learn` - Machine learning analysis

**Visualisation & Reporting**:
- `matplotlib` & `seaborn` - Statistical plots
- `plotly` - Interactive dashboards
- `jupyter` - Analysis notebooks

**Development & Deployment**:
- `python-dotenv` - Environment management
- `black` - Code formatting
- `pytest` - Testing framework

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd spotify_hypothesis_testing

# Create virtual environment
python -m venv spotify_env
source spotify_env/bin/activate  # macOS/Linux
# spotify_env\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Spotify API Configuration
```bash
# Copy environment template
cp env_template.txt .env

# Add your Spotify API credentials to .env:
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### 3. Data Collection
```bash
# Run optimised collection (16,000 tracks, ~43 minutes)
python -m src.data_collection.optimised_title_collector

# Monitor progress with real-time progress bars
# Dataset saved to: data/optimised_title_dataset_TIMESTAMP.csv
```

### 4. Analysis Execution
```bash
# Launch analysis environment
jupyter notebook

# Or run individual analysis modules
python -m src.hypothesis_testing.primary_analysis
python -m src.reporting.generate_report
```

---

## 📈 Expected Outcomes

### Statistical Deliverables
- **Hypothesis test results** with p-values & effect sizes
- **Regression models** explaining popularity variance
- **Genre-specific insights** for targeted strategies
- **Confidence intervals** for business decision-making

### Business Applications
- **Title optimisation guidelines** for new releases
- **Genre-specific strategies** for different music categories
- **A/B testing frameworks** for music marketing
- **Data-driven insights** for playlist curation

### Portfolio Demonstration
- **Advanced sampling methodology** (stratified, controlled)
- **Large-scale data collection** (16,000+ observations)
- **Sophisticated feature engineering** (19+ variables)
- **Multiple statistical techniques** (parametric & non-parametric)
- **Business-relevant insights** with actionable recommendations

---

## 🔐 Data Privacy & Security

- **API credentials** secured via environment variables
- **Cache files** excluded from version control
- **No personal data** collection (only public metadata)
- **Rate limiting** implemented for API respect
- **Error handling** for robust data collection

---

## 📚 Academic Rigour

### Methodology Validation
- **Stratified sampling** ensures genre representation
- **Control variables** address confounding factors
- **Effect size reporting** beyond statistical significance
- **Multiple hypothesis corrections** when appropriate
- **Reproducible pipeline** with version control

### Statistical Best Practices
- **Assumption testing** (normality, homoscedasticity)
- **Power analysis** for adequate sample sizes
- **Cross-validation** for model reliability
- **Confidence interval reporting** for practical significance
- **Transparent methodology** documentation

---

## 🎵 Why This Matters

Music streaming platforms process billions of tracks, where small optimisations in discoverability can have massive business impact. Understanding how title complexity affects popularity provides:

1. **Strategic insights** for artists and labels
2. **Algorithm optimisation** for recommendation systems  
3. **Marketing intelligence** for campaign development
4. **Academic contribution** to music industry analytics

This project demonstrates sophisticated A/B testing capabilities applicable across industries, from tech to entertainment to e-commerce.

---

## 📞 Contact & Collaboration

**Technical Questions**: Advanced statistical methodology, API optimisation
**Business Applications**: Music industry insights, A/B testing strategies  
**Academic Discussion**: Hypothesis testing, experimental design

*This project showcases production-ready data science capabilities with real-world business applications and academic rigour.*
