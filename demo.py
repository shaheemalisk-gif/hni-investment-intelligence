"""
HNI Investment Platform - Quick Demo
Showcases both Part 1 and Part 2 deliverables
"""

import sys
sys.path.append('.')

from src.models.health_scorer import CompanyHealthScorer
from src.models.portfolio_ranker import PortfolioRanker
import pandas as pd

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def print_section(text):
    """Print formatted section"""
    print("\n" + "-"*80)
    print(text)
    print("-"*80 + "\n")

def demo_health_scorer():
    """Demonstrate Part 2: Company Health Checker"""
    
    print_header("PART 2: COMPANY HEALTH CHECKER DEMO")
    
    scorer = CompanyHealthScorer()
    
    # Demo companies
    demo_symbols = ['NVDA', 'AAPL', 'TSLA', 'JNJ']
    
    print("Analyzing health of 4 sample companies...\n")
    
    for symbol in demo_symbols:
        print(f"\n{'█'*80}")
        analysis = scorer.analyze_company(symbol)
        
        if 'error' in analysis:
            print(f"Error: {analysis['error']}")
            continue
        
        # Print concise summary
        print(f"\n{analysis['symbol']} - {analysis['company_name']}")
        print(f"{'─'*80}")
        print(f"Overall Health:  {analysis['overall_health']:.1f}% ({scorer._health_rating(analysis['overall_health'])})")
        print(f"Risk Level:      {analysis['risk_level']}")
        print(f"Recommendation:  {analysis['recommendation']}")
        
        # Top 3 strengths
        print(f"\nTop Strengths:")
        for i, pro in enumerate(analysis['pros'][:3], 1):
            print(f"  ✓ {pro}")
        
        # Top 3 concerns
        print(f"\nKey Concerns:")
        for i, con in enumerate(analysis['cons'][:3], 1):
            print(f"  ⚠ {con}")
        
        print()
        input("Press Enter to continue...")
    
    print_section("✅ Health Scorer Demo Complete!")

def demo_portfolio_ranker():
    """Demonstrate Part 1: Portfolio Recommender"""
    
    print_header("PART 1: PORTFOLIO RECOMMENDER DEMO")
    
    ranker = PortfolioRanker()
    
    print("Generating investment recommendations across all categories...\n")
    
    # Generate rankings
    results = ranker.rank_all_categories()
    
    # Show summary for each category
    categories = [
        ('mag7', 'Magnificent 7 Tech Giants'),
        ('giant', 'Giant Cap (>$500B)'),
        ('large', 'Large Cap ($100B-$500B)'),
        ('mid', 'Mid Cap (<$100B)')
    ]
    
    for cat, name in categories:
        print_section(f"{name.upper()}")
        
        result = results[cat]
        top_picks = result['top_picks'].head(3)
        
        print(f"Total Companies: {result['total_companies']}")
        print(f"Average Score: {result['statistics']['avg_composite_score']:.2f}")
        print(f"\nTop 3 Picks:\n")
        
        for i, (_, row) in enumerate(top_picks.iterrows(), 1):
            print(f"{i}. {row['symbol']:6s} - {row['company_name'][:40]:<40s} Score: {row['rank_score']:.2f}")
            print(f"   Quality: {row['quality_score']:.1f} | "
                  f"Value: {row['value_score']:.1f} | "
                  f"Growth: {row['growth_score']:.1f} | "
                  f"Risk: {row['risk_category']}")
            print()
    
    # Overall Top 10
    print_section("OVERALL TOP 10 ACROSS ALL CATEGORIES")
    
    top10 = results['overall_top20']['top_picks'].head(10)
    
    print(f"{'Rank':<6}{'Symbol':<8}{'Company':<45}{'Score':<8}")
    print("─"*80)
    
    for _, row in top10.iterrows():
        company_name = row['company_name'][:43]
        print(f"{int(row['rank']):<6}{row['symbol']:<8}{company_name:<45}{row['rank_score']:.2f}")
    
    print_section("✅ Portfolio Ranker Demo Complete!")

def show_statistics():
    """Show overall system statistics"""
    
    print_header("SYSTEM STATISTICS")
    
    # Load data
    df = pd.read_csv('data/processed/stock_universe_engineered.csv')
    
    print(f"Total Companies Analyzed:     {len(df)}")
    print(f"Total Features per Company:   {len(df.columns)}")
    print(f"Total Data Points:            {len(df) * len(df.columns):,}")
    print()
    
    # Sector distribution
    print("Sector Distribution:")
    sector_counts = df['sector_category'].value_counts()
    for sector, count in sector_counts.items():
        print(f"  {sector:20s}: {count:3d} companies")
    print()
    
    # Market cap distribution
    print("Market Cap Distribution:")
    mag7_count = len(df[df['market_cap'] > 1e12])
    giant_count = len(df[(df['market_cap'] > 500e9) & (df['market_cap'] <= 1e12)])
    large_count = len(df[(df['market_cap'] > 100e9) & (df['market_cap'] <= 500e9)])
    mid_count = len(df[df['market_cap'] <= 100e9])
    
    print(f"  Trillion+ (Mag7):     {mag7_count}")
    print(f"  $500B - $1T (Giant):  {giant_count}")
    print(f"  $100B - $500B:        {large_count}")
    print(f"  <$100B:               {mid_count}")
    print()
    
    # Score statistics
    print("Composite Score Statistics:")
    print(f"  Mean:                 {df['composite_score'].mean():.2f}")
    print(f"  Median:               {df['composite_score'].median():.2f}")
    print(f"  Std Dev:              {df['composite_score'].std():.2f}")
    print(f"  Best:                 {df['composite_score'].max():.2f}")
    print(f"  Worst:                {df['composite_score'].min():.2f}")
    print()
    
    # Risk distribution
    print("Risk Distribution:")
    risk_dist = df['risk_category'].value_counts()
    for risk, count in risk_dist.items():
        pct = (count / len(df)) * 100
        print(f"  {risk:15s}: {count:3d} ({pct:5.1f}%)")
    print()
    
    # Profitability
    profitable = df['is_profitable'].sum()
    print(f"Profitable Companies:         {profitable} ({profitable/len(df)*100:.1f}%)")
    print()

def main():
    """Main demo function"""
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "HNI INVESTMENT INTELLIGENCE PLATFORM - INTERACTIVE DEMO".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    print("This demo showcases both deliverables:")
    print("  • Part 1: Portfolio Recommendation System")
    print("  • Part 2: Company Health Checker")
    print()
    
    while True:
        print("\n" + "─"*80)
        print("DEMO MENU")
        print("─"*80)
        print("1. Part 1: Portfolio Recommender Demo")
        print("2. Part 2: Company Health Checker Demo")
        print("3. Show System Statistics")
        print("4. Run Full Demo (All of the above)")
        print("5. Exit")
        print()
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == '1':
            demo_portfolio_ranker()
        elif choice == '2':
            demo_health_scorer()
        elif choice == '3':
            show_statistics()
        elif choice == '4':
            show_statistics()
            demo_portfolio_ranker()
            demo_health_scorer()
            print_header("🎉 FULL DEMO COMPLETE!")
            print("\nAll deliverables demonstrated successfully!")
            print("\nNext steps:")
            print("  • Review README.md for detailed documentation")
            print("  • Check data/processed/ for output files")
            print("  • Run generate_portfolio.py for full reports")
            break
        elif choice == '5':
            print("\nThank you for reviewing the HNI Investment Platform!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("  1. You're in the project root directory")
        print("  2. Virtual environment is activated")
        print("  3. Data has been generated (run build_universe.py)")
