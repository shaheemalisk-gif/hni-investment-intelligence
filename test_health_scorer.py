"""
Test the Company Health Scorer
"""

import sys
sys.path.append('.')

from src.models.health_scorer import CompanyHealthScorer

def main():
    print("\n" + "="*80)
    print("🏥 COMPANY HEALTH SCORER - INTERACTIVE TEST")
    print("="*80 + "\n")
    
    # Initialize scorer
    scorer = CompanyHealthScorer()
    
    # Test with predefined examples
    test_symbols = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'JNJ']
    
    print("Testing with sample companies...\n")
    
    for symbol in test_symbols:
        print("\n" + "█"*80)
        
        # Analyze
        analysis = scorer.analyze_company(symbol)
        
        # Format and print
        print(scorer.format_analysis(analysis))
        
        input("\nPress Enter to continue to next company...")
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80 + "\n")
    print("Enter a stock symbol to analyze (or 'quit' to exit)\n")
    
    while True:
        symbol = input("Symbol: ").strip().upper()
        
        if symbol in ['QUIT', 'EXIT', 'Q']:
            print("\nGoodbye!")
            break
        
        if not symbol:
            continue
        
        print("\n")
        analysis = scorer.analyze_company(symbol)
        print(scorer.format_analysis(analysis))
        print("\n")

if __name__ == "__main__":
    main()