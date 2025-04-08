import os
import yaml
from src.data_fetcher import DataFetcher
from src.technical_analysis import TechnicalAnalysis
from src.market_analyzer import MarketAnalyzer

def test_data_fetcher():
    """Test data fetching functionality"""
    fetcher = DataFetcher(symbol="^BSESN", days=30)
    df = fetcher.fetch_data()
    assert not df.empty, "Data fetching failed"
    print(f"Successfully fetched {len(df)} days of data")

def test_technical_analysis():
    """Test technical analysis calculations"""
    fetcher = DataFetcher(symbol="^BSESN", days=30)
    df = fetcher.fetch_data()
    
    ta = TechnicalAnalysis(df)
    df_with_indicators = ta.add_all_indicators({
        'sma': {'short_period': 50, 'long_period': 200},
        'rsi': {'period': 14},
        'macd': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
    })
    
    assert 'SMA_50' in df_with_indicators.columns, "SMA_50 not calculated"
    assert 'RSI' in df_with_indicators.columns, "RSI not calculated"
    assert 'MACD' in df_with_indicators.columns, "MACD not calculated"
    print("Technical analysis tests passed")

def test_market_analyzer():
    """Test market analysis functionality"""
    fetcher = DataFetcher(symbol="^BSESN", days=30)
    df = fetcher.fetch_data()
    
    ta = TechnicalAnalysis(df)
    df_with_indicators = ta.add_all_indicators({
        'sma': {'short_period': 50, 'long_period': 200},
        'rsi': {'period': 14},
        'macd': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
    })
    
    analyzer = MarketAnalyzer(df_with_indicators)
    analysis = analyzer.analyze_market()
    
    assert 'Overall Status' in analysis, "Overall status not calculated"
    print(f"Market status: {analysis['Overall Status']}")
    print("Market analysis tests passed")

if __name__ == "__main__":
    print("\nRunning tests...\n")
    test_data_fetcher()
    test_technical_analysis()
    test_market_analyzer()
