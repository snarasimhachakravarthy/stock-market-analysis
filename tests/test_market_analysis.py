import unittest
import pandas as pd
from datetime import datetime
from src.market_analyzer import MarketAnalyzer
from src.report_generator import ReportGenerator
from src.config import load_config
import yfinance as yf
import os

class TestMarketAnalysis(unittest.TestCase):
    def setUp(self):
        # Load configuration
        self.config = load_config()
        
        # Get real SENSEX data with more historical data
        self.symbol = "^BSESN"
        # Fetch 6 months of data to ensure we have enough for 200-day SMA
        self.df = yf.download(self.symbol, period='6mo', interval='1d')
        
        # Initialize analyzers
        self.analyzer = MarketAnalyzer(self.df, self.symbol)
        self.report_generator = ReportGenerator(self.config)
        
    def test_complete_analysis(self):
        """Test complete market analysis and report generation"""
        # Perform market analysis
        analysis = self.analyzer.analyze_market()
        
        # Get the modified DataFrame with indicators
        df_with_indicators = self.analyzer.df
        
        # Remove sector analysis results since we're skipping it
        analysis.pop('Top Performing Sector', None)
        analysis.pop('Bottom Performing Sector', None)
        analysis.pop('Sector Trend', None)
        
        # Generate report using the modified DataFrame
        report_path = self.report_generator.generate_report(analysis, df_with_indicators)
        
        # Print analysis results
        print("\nMarket Analysis Results:")
        for indicator, status in analysis.items():
            print(f"{indicator}: {status}")
        
        # Verify report was generated
        self.assertTrue(os.path.exists(report_path))
        
        # Print report path
        print(f"\nReport generated at: {report_path}")

if __name__ == '__main__':
    unittest.main()
