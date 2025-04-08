import unittest
from datetime import datetime
from src.fundamental_analyzer import FundamentalAnalyzer

class TestFundamentalAnalyzerIndex(unittest.TestCase):
    def setUp(self):
        # Using SENSEX symbol
        self.symbol = "^BSESN"
        self.analyzer = FundamentalAnalyzer(self.symbol)
        
    def test_fetch_fundamentals(self):
        """Test fetching fundamental metrics for index"""
        fundamentals = self.analyzer.get_fundamental_metrics()
        print("\nFundamental Metrics for SENSEX:")
        for key, value in fundamentals.items():
            print(f"{key}: {value}")
        
        # Verify we got some values (not all may be available)
        self.assertIsNotNone(fundamentals)
        
    def test_analyze_fundamentals(self):
        """Test fundamental analysis for index"""
        analysis = self.analyzer.analyze_fundamentals()
        print("\nFundamental Analysis for SENSEX:")
        
        # Print analysis results
        for metric, result in analysis.items():
            print(f"\n{metric.replace('_', ' ').title()}")
            print(f"Value: {result['value']}")
            print(f"Status: {result['status']}")
            print(f"Interpretation: {result['interpretation']}")
        
        # Verify analysis results
        self.assertIn('fundamentals', analysis)
        self.assertEqual(analysis['fundamentals']['status'], 'Not Available')
        self.assertIn('Use individual stock analysis', analysis['fundamentals']['interpretation'])

if __name__ == '__main__':
    unittest.main()
