import unittest
from datetime import datetime
from src.fundamental_analyzer import FundamentalAnalyzer

class TestFundamentalAnalyzer(unittest.TestCase):
    def setUp(self):
        # Using a stock symbol instead of index for testing
        self.symbol = "RELIANCE.NS"  # Reliance Industries
        self.analyzer = FundamentalAnalyzer(self.symbol)
        
    def test_fetch_fundamentals(self):
        """Test fetching fundamental metrics"""
        fundamentals = self.analyzer.get_fundamental_metrics()
        print("\nFundamental Metrics:")
        print(f"P/E Ratio: {fundamentals['pe_ratio']}")
        print(f"P/B Ratio: {fundamentals['pb_ratio']}")
        print(f"Dividend Yield: {fundamentals['dividend_yield']}%")
        print(f"Forward P/E: {fundamentals['forward_pe']}")
        print(f"Earnings Growth: {fundamentals['earnings_growth']}")
        
        # Verify we got some values (not all may be available)
        self.assertIsNotNone(fundamentals)
        
        # Check if we got at least one value
        self.assertTrue(any(value is not None for value in fundamentals.values()))
        
    def test_analyze_fundamentals(self):
        """Test fundamental analysis"""
        analysis = self.analyzer.analyze_fundamentals()
        print("\nFundamental Analysis:")
        
        # Print analysis results
        for metric, result in analysis.items():
            print(f"\n{metric.replace('_', ' ').title()}")
            print(f"Value: {result['value']}")
            print(f"Status: {result['status']}")
            print(f"Interpretation: {result['interpretation']}")
        
        # Verify analysis results
        self.assertGreater(len(analysis), 0)
        
        # Check at least one metric has analysis
        for metric in analysis.values():
            self.assertIn('value', metric)
            self.assertIn('status', metric)
            self.assertIn('interpretation', metric)

if __name__ == '__main__':
    unittest.main()
