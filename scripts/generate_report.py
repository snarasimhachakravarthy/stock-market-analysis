import pandas as pd
from datetime import datetime
from src.market_analyzer import MarketAnalyzer
from src.report_generator import ReportGenerator
from src.config import load_config
import yfinance as yf

def generate_market_report():
    # Load configuration
    config = load_config()
    
    # Get real SENSEX data with more historical data
    symbol = "^BSESN"
    print(f"Fetching data for {symbol}...")
    df = yf.download(symbol, period='6mo', interval='1d')
    
    if len(df) == 0:
        print("Error: Could not fetch market data")
        return
    
    print("Initializing market analyzer...")
    analyzer = MarketAnalyzer(df, symbol)
    
    print("Performing market analysis...")
    analysis = analyzer.analyze_market()
    
    print("Generating report...")
    report_generator = ReportGenerator(config)
    report_path = report_generator.generate_report(analysis, analyzer.df)
    
    print("\nMarket Analysis Results:")
    for indicator, status in analysis.items():
        print(f"{indicator}: {status}")
    
    print(f"\nReport generated at: {report_path}")

if __name__ == '__main__':
    generate_market_report()
