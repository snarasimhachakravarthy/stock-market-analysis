"""Integration tests for the Stock Market Analysis application."""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import report_generator
import technical_indicators

class TestStockAnalysisIntegration(unittest.TestCase):
    """Integration tests for stock analysis functionality."""

    def setUp(self):
        """Set up test data with sufficient points for technical indicators."""
        # Generate 100 days of sample data
        np.random.seed(42)
        n_days = 100
        base_price = 100
        volatility = 0.02
        
        # Generate random walk for prices
        returns = np.random.normal(0, volatility, n_days)
        prices = base_price * (1 + returns).cumprod()
        
        # Create DataFrame with OHLCV data
        self.test_data = pd.DataFrame({
            'Open': prices * (1 + np.random.normal(0, 0.01, n_days)),
            'High': prices * (1 + np.abs(np.random.normal(0, 0.01, n_days))),
            'Low': prices * (1 - np.abs(np.random.normal(0, 0.01, n_days))),
            'Close': prices,
            'Volume': np.random.randint(1000, 10000, n_days)
        }, index=pd.date_range(end=datetime.today(), periods=n_days, freq='D'))

    @patch('yfinance.Ticker')
    def test_get_stock_data_success(self, mock_yfinance):
        """Test successful stock data retrieval."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.test_data
        mock_yfinance.return_value = mock_ticker
        
        # Test
        result = report_generator.get_stock_data("AAPL", period="1y")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertFalse(result.empty)
        self.assertIn('Close', result.columns)
        # We expect 100 days of data as per our test setup
        self.assertEqual(len(result), 100)

    @patch('yfinance.Ticker')
    def test_get_stock_info_success(self, mock_yfinance):
        """Test successful stock info retrieval."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.info = {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'currentPrice': 175.50,
            'sector': 'Technology'
        }
        mock_yfinance.return_value = mock_ticker
        
        # Test
        result = report_generator.get_stock_info("AAPL")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertIn('currentPrice', result)

    def test_technical_indicators(self):
        """Test technical indicator calculations."""
        # Test SMA
        sma = technical_indicators.calculate_sma(self.test_data, window=20)
        self.assertEqual(len(sma), len(self.test_data))
        # Just test that the last value is a reasonable number
        self.assertFalse(pd.isna(sma.iloc[-1]))
        self.assertGreater(sma.iloc[-1], 0)
        
        # Test RSI with valid window size
        rsi_window = 14
        rsi = technical_indicators.calculate_rsi(self.test_data, window=rsi_window)
        self.assertEqual(len(rsi), len(self.test_data))
        # First (window-1) values should be NaN
        self.assertTrue(pd.isna(rsi.iloc[:rsi_window-1]).all())
        # Remaining values should be between 0 and 100
        self.assertTrue(all(0 <= r <= 100 for r in rsi.dropna()))
        
        # Test MACD
        macd, signal, hist = technical_indicators.calculate_macd(self.test_data)
        self.assertEqual(len(macd), len(self.test_data))
        self.assertEqual(len(signal), len(self.test_data))
        self.assertEqual(len(hist), len(self.test_data))

    @patch('yfinance.Ticker')
    def test_end_to_end_analysis(self, mock_yfinance):
        """Test end-to-end analysis workflow."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.test_data
        mock_ticker.info = {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'currentPrice': 104.5,
            'sector': 'Technology'
        }
        mock_yfinance.return_value = mock_ticker
        
        # Test data retrieval
        data = report_generator.get_stock_data("AAPL")
        self.assertIsNotNone(data)
        
        # Test technical indicators with appropriate window sizes
        sma_window = 20  # Reduced from 50 for testing with 100 data points
        rsi_window = 14
        data['SMA_20'] = technical_indicators.calculate_sma(data, window=sma_window)
        data['RSI_14'] = technical_indicators.calculate_rsi(data, window=rsi_window)
        macd, signal, _ = technical_indicators.calculate_macd(data)
        
        # Ensure SMA has correct number of NaN values at the start
        self.assertEqual(pd.isna(data['SMA_20']).sum(), sma_window - 1)
        # Ensure RSI has correct number of NaN values at the start
        self.assertEqual(pd.isna(data['RSI_14']).sum(), rsi_window - 1)
        
        # Basic validation
        self.assertIn('SMA_20', data.columns)
        self.assertIn('RSI_14', data.columns)
        self.assertEqual(len(macd), len(data))
        self.assertEqual(len(signal), len(data))

if __name__ == '__main__':
    unittest.main()
