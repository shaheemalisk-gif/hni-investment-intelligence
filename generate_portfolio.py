"""
Generate Investment Portfolio Recommendations
Part 1 Deliverable: Rank companies and select top picks
"""

import sys
sys.path.append('.')

from src.models.portfolio_ranker import PortfolioRanker
import pandas as pd

def main():
    print("\n" + "="*100)
    print("🏆 INVESTMENT PORTFOLIO RECOMMENDATION SYSTEM")
    print("="*100 + "\n")
    
    # Initialize ranker
    ranker = PortfolioRanker()
    
    print("Analyzing and ranking all companies...\n")
    
    # Generate rankings for all categories
    results = ranker.rank_all_categories()
    
    # Print comprehensive summary
    print(ranker.create_portfolio_summary(results))
    
    # Category reports
    categories = ['mag7', 'giant', 'large', 'mid']
    category_names = {
        'mag7': 'Magnificent 7',
        'giant': 'Giant Cap',
        'large': 'Large Cap',
        'mid': 'Mid Cap'
    }
    
    for cat in categories:
        print(ranker.format_category_report(results[cat]))
        print(ranker.generate_investment_thesis(results[cat]))
        input("\nPress Enter to continue to next category...")
    
    # Overall Top 20
    print("\n" + "="*100)
    print("OVERALL TOP 20 PICKS ACROSS ALL CATEGORIES")
    print("="*100 + "\n")
    
    top20 = results['overall_top20']['top_picks']
    
    print(f"{'Rank':<6}{'Symbol':<8}{'Company':<40}{'Score':<8}{'Category':<12}{'Market Cap':<15}")
    print("-" * 100)
    
    for _, row in top20.iterrows():
        # Determine category
        market_cap = row['market_cap']
        if market_cap > 500e9:
            cat = "Mag7/Giant"
        elif market_cap > 100e9:
            cat = "Large Cap"
        else:
            cat = "Mid Cap"
        
        company_name = row['company_name'][:38]
        market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap < 1e12 else f"${market_cap/1e12:.2f}T"
        
        print(f"{int(row['rank']):<6}{row['symbol']:<8}{company_name:<40}"
              f"{row['rank_score']:.2f}    {cat:<12}{market_cap_str:<15}")
    
    print("\n" + "="*100)
    
    # Save results
    print("\nSaving portfolio recommendations...")
    
    # Save each category's top picks
    for cat in categories:
        filename = f"data/processed/portfolio_{cat}_recommendations.csv"
        results[cat]['top_picks'].to_csv(filename, index=False)
        print(f"  ✓ Saved {category_names[cat]} recommendations: {filename}")
    
    # Save overall top 20
    results['overall_top20']['top_picks'].to_csv(
        'data/processed/portfolio_overall_top20.csv', index=False
    )
    print(f"  ✓ Saved Overall Top 20: data/processed/portfolio_overall_top20.csv")
    
    # Create summary report
    with open('data/processed/PORTFOLIO_RECOMMENDATIONS.txt', 'w') as f:
        f.write(ranker.create_portfolio_summary(results))
        f.write("\n\n")
        
        for cat in categories:
            f.write(ranker.format_category_report(results[cat]))
            f.write("\n")
            f.write(ranker.generate_investment_thesis(results[cat]))
            f.write("\n\n")
        
        # Overall top 20
        f.write("="*100 + "\n")
        f.write("OVERALL TOP 20 PICKS\n")
        f.write("="*100 + "\n\n")
        
        for _, row in top20.iterrows():
            market_cap = row['market_cap']
            if market_cap > 500e9:
                cat = "Mag7/Giant"
            elif market_cap > 100e9:
                cat = "Large Cap"
            else:
                cat = "Mid Cap"
            
            f.write(f"{int(row['rank'])}. {row['symbol']} - {row['company_name']}\n")
            f.write(f"   Score: {row['rank_score']:.2f} | Category: {cat} | "
                   f"Market Cap: ${row['market_cap']/1e9:.1f}B\n\n")
    
    print(f"  ✓ Saved Full Report: data/processed/PORTFOLIO_RECOMMENDATIONS.txt")
    
    print("\n" + "="*100)
    print("🎉 PORTFOLIO GENERATION COMPLETE!")
    print("="*100 + "\n")
    
    print("Files created:")
    print("  • portfolio_mag7_recommendations.csv")
    print("  • portfolio_giant_recommendations.csv")
    print("  • portfolio_large_recommendations.csv")
    print("  • portfolio_mid_recommendations.csv")
    print("  • portfolio_overall_top20.csv")
    print("  • PORTFOLIO_RECOMMENDATIONS.txt (Full Report)")
    print()

if __name__ == "__main__":
    main()