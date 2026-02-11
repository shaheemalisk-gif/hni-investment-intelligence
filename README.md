# 🏆 HNI Investment Intelligence Platform

**AI-Powered Stock Analysis & Portfolio Recommendation System**

Built for high-net-worth individuals seeking data-driven investment insights across multiple market cap categories.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Sample Results](#sample-results)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

This platform provides comprehensive stock analysis and investment recommendations across 102 major US companies, categorized into:

- **Magnificent 7** - Tech giants (AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META)
- **Giant Cap** - Companies >$500B market cap
- **Large Cap** - Companies $100B-$500B
- **Mid Cap** - Companies <$100B

### Core Deliverables

1. **Portfolio Recommender** - Ranks companies within each category and selects top picks
2. **Company Health Scorer** - Analyzes individual companies with health percentage and pros/cons

---

## ✨ Key Features

### 1. Multi-Dimensional Analysis
- **Financial Strength**: Debt levels, cash flow, liquidity
- **Profitability**: Margins, ROE, ROA
- **Growth Trajectory**: Revenue & earnings growth
- **Valuation**: P/E, PEG, Price/Book ratios
- **Risk Management**: Beta, volatility, Altman Z-Score
- **Market Position**: Market cap, momentum

### 2. Advanced Feature Engineering
- Composite scoring system (0-100 scale)
- Quality, Value, Growth, Momentum scores
- Altman Z-Score for bankruptcy prediction
- Risk categorization (Low/Medium/High)
- Profitability status flags

### 3. Machine Learning Ready
- 59 engineered features per company
- Normalized scores for ML model training
- Sector-relative performance metrics
- Historical performance indicators

### 4. Intelligent Ranking
- Weighted multi-factor scoring
- Category-specific recommendations
- Investment thesis generation
- Pros/cons analysis

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION                          │
│  Yahoo Finance API → 102 Companies → 30+ Raw Metrics        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING                         │
│  • Composite Scores (Quality, Value, Growth, Momentum)      │
│  • Risk Categorization (Altman Z-Score, Beta Analysis)      │
│  • Profitability Flags & Financial Health Metrics           │
│  • Sector Benchmarking & Percentile Rankings               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ANALYSIS ENGINES                           │
│                                                              │
│  ┌──────────────────────┐    ┌─────────────────────────┐   │
│  │  Health Scorer       │    │  Portfolio Ranker       │   │
│  │  • 6 Health Dims     │    │  • Multi-factor Ranking │   │
│  │  • Pros/Cons Gen     │    │  • Top Picks Selection  │   │
│  │  • Risk Assessment   │    │  • Investment Thesis    │   │
│  └──────────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        OUTPUTS                               │
│  • Portfolio Recommendations (CSV + TXT Reports)            │
│  • Health Analysis (Interactive + Batch)                    │
│  • Investment Thesis & Executive Summaries                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download the Project
```bash
cd hni-investment-analyzer
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure (Optional)
Edit `.env` file to add API keys:
```bash
ALPHA_VANTAGE_KEY=your_key_here
FRED_KEY=your_key_here
```

---

## 💡 Usage

### Quick Start: Run Complete Analysis

```bash
# 1. Generate portfolio recommendations (Part 1)
python generate_portfolio.py

# 2. Test health scorer on sample companies (Part 2)
python test_health_scorer.py

# 3. Run full demo
python demo.py
```

### Individual Components

#### 1. Portfolio Recommendations
```bash
python generate_portfolio.py
```
**Output:**
- `data/processed/portfolio_mag7_recommendations.csv`
- `data/processed/portfolio_giant_recommendations.csv`
- `data/processed/portfolio_large_recommendations.csv`
- `data/processed/portfolio_mid_recommendations.csv`
- `data/processed/PORTFOLIO_RECOMMENDATIONS.txt`

#### 2. Company Health Analysis
```bash
python test_health_scorer.py
```
**Interactive Mode:**
- Enter any stock symbol (e.g., NVDA, AAPL, TSLA)
- Get instant health score (0-100%)
- See detailed pros/cons
- Receive investment recommendation

#### 3. Data Collection (if needed)
```bash
python build_universe.py
```

#### 4. Feature Engineering
```bash
python engineer_features.py
```

---

## 📁 Project Structure

```
hni-investment-analyzer/
├── config/
│   ├── config.yaml              # System configuration
│   └── symbols.yaml             # Stock universe definitions
├── data/
│   ├── raw/                     # Raw market data
│   ├── processed/               # Engineered datasets
│   │   ├── stock_universe_full.csv
│   │   ├── stock_universe_engineered.csv
│   │   ├── category_*.csv
│   │   ├── portfolio_*_recommendations.csv
│   │   └── PORTFOLIO_RECOMMENDATIONS.txt
│   ├── cache/                   # Cached API responses
│   └── models/                  # Trained ML models (future)
├── src/
│   ├── data/
│   │   ├── collectors.py        # Data fetching & processing
│   │   ├── universe.py          # Stock universe builder
│   │   └── cache_manager.py    # Data caching
│   ├── models/
│   │   ├── health_scorer.py    # Company health analysis
│   │   └── portfolio_ranker.py # Portfolio ranking engine
│   ├── analysis/
│   │   └── feature_engineering.py  # Feature creation
│   └── utils/
│       ├── logger.py            # Logging system
│       ├── config.py            # Configuration manager
│       └── helpers.py           # Utility functions
├── logs/                        # Application logs
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── README.md                    # This file
└── demo.py                      # Quick demonstration script
```

---

## 🔧 Technical Details

### Data Sources
- **Primary**: Yahoo Finance (yfinance library)
- **Backup**: Alpha Vantage API
- **Macro Data**: FRED API

### Key Technologies
- **Python 3.12**: Core language
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **scikit-learn**: ML preprocessing
- **yfinance**: Market data

### Performance Metrics
- **Data Collection**: ~7.5 minutes for 100 companies
- **Feature Engineering**: <1 second
- **Health Scoring**: Instant (<0.1s per company)
- **Portfolio Ranking**: <1 second for all categories

### Scoring Methodology

#### Health Score (0-100%)
```
Health Score = Weighted Average of:
  • Financial Strength (25%): Debt, Cash Flow, Liquidity
  • Profitability (20%): Margins, ROE, ROA
  • Growth Trajectory (20%): Revenue & Earnings Growth
  • Valuation (15%): P/E, PEG, Price/Book
  • Risk Management (10%): Beta, Volatility, Z-Score
  • Market Position (10%): Size, Momentum
```

#### Ranking Score
```
Rank Score = Weighted Average of:
  • Composite Score (30%)
  • Quality Score (20%)
  • Growth Score (20%)
  • Value Score (15%)
  • Momentum Score (15%)
```

---

## 📊 Sample Results

### Top Overall Picks (as of Feb 10, 2026)

| Rank | Symbol | Company | Score | Category |
|------|--------|---------|-------|----------|
| 1 | NVDA | NVIDIA Corporation | 100.00 | Mag7 |
| 2 | JNJ | Johnson & Johnson | 68.02 | Giant |
| 3 | GILD | Gilead Sciences | 67.84 | Large |
| 4 | LRCX | Lam Research | 67.44 | Large |
| 5 | MPC | Marathon Petroleum | 66.84 | Mid |

### Health Score Examples

**NVIDIA (NVDA)**: 80.7% - Excellent
- ✅ Exceptional margins (53%)
- ✅ Explosive growth (62.5%)
- ✅ Strong cash flow ($53B)
- ⚠️ High volatility (Beta: 2.31)
- **Recommendation**: Buy

**Tesla (TSLA)**: 23.2% - Poor
- ✅ Large company ($1.57T)
- ⚠️ Thin margins (4%)
- ⚠️ Declining revenue (-3.1%)
- ⚠️ Extreme P/E (382.9)
- **Recommendation**: Sell

---

## 🔮 Future Enhancements

### Phase 1 (Immediate)
- [ ] Streamlit web interface
- [ ] Real-time data updates
- [ ] Email alerts for top picks
- [ ] PDF report generation

### Phase 2 (Advanced)
- [ ] Machine learning models (Random Forest, XGBoost)
- [ ] Outlier detection (Isolation Forest)
- [ ] Sentiment analysis from news
- [ ] Portfolio optimization (Modern Portfolio Theory)
- [ ] Backtesting framework

### Phase 3 (Enterprise)
- [ ] RESTful API
- [ ] Multi-user support
- [ ] Custom watchlists
- [ ] Integration with brokers
- [ ] Mobile app

---

## 📈 Data Freshness

- **Market Data**: Real-time via Yahoo Finance
- **Fundamentals**: Updated quarterly (company filings)
- **Cache Expiry**: 24 hours
- **Recommended Refresh**: Daily for active portfolios

---

## ⚠️ Disclaimer

**This tool is for educational and informational purposes only.**

- Not financial advice
- Past performance ≠ future results
- Always consult a licensed financial advisor
- Conduct your own due diligence
- The authors assume no liability for investment decisions

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Contributors

Built by: Muhammed Shaheem OP
Date: February 2026
Purpose: HNI Investment Platform Technical Assessment

---

## 📧 Contact

For questions or issues:
- Email: mhdshaheemop@gmail.com
- GitHub: github.com/shaheemalisk-gif

---

## 🙏 Acknowledgments

- Yahoo Finance for market data
- Anthropic Claude for development assistance
- Open source Python community

---

**Last Updated**: February 10, 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
