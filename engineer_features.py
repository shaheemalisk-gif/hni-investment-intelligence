"""
Apply feature engineering to stock universe
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
from src.analysis.feature_engineering import FeatureEngineer
from src.utils.logger import logger

def main():
    print("\n" + "="*80)
    print("🧠 ADVANCED FEATURE ENGINEERING")
    print("="*80 + "\n")
    
    # Load data
    print("Loading stock universe...")
    df = pd.read_csv('data/processed/stock_universe_full.csv')
    
    print(f"Loaded {len(df)} companies")
    print(f"Original features: {len(df.columns)}")
    
    # Create feature engineer instance
    feature_engineer = FeatureEngineer()
    
    # Apply feature engineering
    print("\n" + "-"*80)
    print("Engineering features...")
    print("-"*80 + "\n")
    
    df_engineered = feature_engineer.engineer_all_features(df)
    
    print("\n" + "="*80)
    print("📊 FEATURE ENGINEERING RESULTS")
    print("="*80 + "\n")
    
    print(f"✅ Total features: {len(df_engineered.columns)}")
    print(f"✅ New features created: {len(feature_engineer.features_created)}")
    
    print("\n" + "-"*80)
    print("NEW FEATURES CREATED:")
    print("-"*80)
    for feature in feature_engineer.features_created:
        print(f"  ✓ {feature}")
    
    # Display sample scores
    print("\n" + "-"*80)
    print("SAMPLE SCORES - Top 5 by Composite Score:")
    print("-"*80)
    
    top5 = df_engineered.nlargest(5, 'composite_score')[
        ['symbol', 'company_name', 'composite_score', 'quality_score', 
         'value_score', 'growth_score', 'risk_category']
    ]
    
    print(top5.to_string(index=False))
    
    # Risk distribution
    print("\n" + "-"*80)
    print("RISK DISTRIBUTION:")
    print("-"*80)
    print(df_engineered['risk_category'].value_counts())
    
    # Profitability distribution
    print("\n" + "-"*80)
    print("PROFITABILITY DISTRIBUTION:")
    print("-"*80)
    print(df_engineered['profitability_status'].value_counts())
    
    # Financial health
    print("\n" + "-"*80)
    print("FINANCIAL HEALTH (Altman Z-Score):")
    print("-"*80)
    print(df_engineered['financial_health'].value_counts())
    
    # Save enhanced dataset
    output_file = 'data/processed/stock_universe_engineered.csv'
    df_engineered.to_csv(output_file, index=False)
    
    print("\n" + "="*80)
    print("💾 SAVED ENHANCED DATASET")
    print("="*80)
    print(f"File: {output_file}")
    print(f"Rows: {len(df_engineered)}")
    print(f"Columns: {len(df_engineered.columns)}")
    
    # Show score statistics
    print("\n" + "="*80)
    print("📈 SCORE STATISTICS")
    print("="*80 + "\n")
    
    score_cols = ['composite_score', 'quality_score', 'value_score', 
                  'growth_score', 'momentum_score']
    
    for col in score_cols:
        if col in df_engineered.columns:
            print(f"{col}:")
            print(f"  Mean: {df_engineered[col].mean():.2f}")
            print(f"  Median: {df_engineered[col].median():.2f}")
            print(f"  Std: {df_engineered[col].std():.2f}")
            print()
    
    print("="*80)
    print("🎉 FEATURE ENGINEERING COMPLETE!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()