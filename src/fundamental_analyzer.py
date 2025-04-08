import yfinance as yf
import pandas as pd
from typing import Dict, Tuple

class FundamentalAnalyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.fundamentals = self._fetch_fundamentals()
        
    def _fetch_fundamentals(self) -> Dict:
        """
        Fetch fundamental metrics from Yahoo Finance
        
        Returns:
            Dict: Dictionary containing fundamental metrics
        """
        try:
            # Get ticker information
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # Extract fundamental metrics
            fundamentals = {
                'pe_ratio': info.get('trailingPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'dividend_yield': info.get('dividendYield', None),
                'forward_pe': info.get('forwardPE', None),
                'earnings_growth': info.get('earningsGrowth', None)
            }
            
            # Convert percentages to decimal
            if fundamentals['dividend_yield'] is not None:
                fundamentals['dividend_yield'] *= 100
            
            return fundamentals
        except Exception as e:
            print(f"Error fetching fundamentals: {str(e)}")
            return {
                'pe_ratio': None,
                'pb_ratio': None,
                'dividend_yield': None,
                'forward_pe': None,
                'earnings_growth': None
            }
    
    def analyze_fundamentals(self) -> Dict:
        """
        Analyze fundamental metrics and provide interpretations
        
        Returns:
            Dict: Dictionary containing analysis results
        """
        analysis = {}
        
        # Check if we have valid data
        if all(value is None for value in self.fundamentals.values()):
            return {
                'fundamentals': {
                    'value': None,
                    'status': 'Not Available',
                    'interpretation': 'Fundamental data not available for this symbol.'
                }
            }
        
        # P/E Ratio Analysis
        pe_ratio = self.fundamentals['pe_ratio']
        if pe_ratio is not None:
            if pe_ratio < 15:
                pe_status = "Undervalued"
            elif pe_ratio < 25:
                pe_status = "Fairly Valued"
            else:
                pe_status = "Overvalued"
            analysis['pe_ratio'] = {
                'value': pe_ratio,
                'status': pe_status,
                'interpretation': "P/E < 15 = Undervalued, 15-25 = Fairly Valued, >25 = Overvalued"
            }
        
        # P/B Ratio Analysis
        pb_ratio = self.fundamentals['pb_ratio']
        if pb_ratio is not None:
            if pb_ratio < 1.5:
                pb_status = "Undervalued"
            elif pb_ratio < 3.0:
                pb_status = "Fairly Valued"
            else:
                pb_status = "Overvalued"
            analysis['pb_ratio'] = {
                'value': pb_ratio,
                'status': pb_status,
                'interpretation': "P/B < 1.5 = Undervalued, 1.5-3.0 = Fairly Valued, >3.0 = Overvalued"
            }
        
        # Dividend Yield Analysis
        div_yield = self.fundamentals['dividend_yield']
        if div_yield is not None:
            if div_yield > 3.0:
                div_status = "High Yield"
            elif div_yield > 2.0:
                div_status = "Good Yield"
            else:
                div_status = "Low Yield"
            analysis['dividend_yield'] = {
                'value': div_yield,
                'status': div_status,
                'interpretation': "Div Yield > 3% = High, 2-3% = Good, <2% = Low"
            }
        
        return analysis
    
    def get_fundamental_metrics(self) -> Dict:
        """
        Get raw fundamental metrics
        
        Returns:
            Dict: Dictionary containing raw fundamental metrics
        """
        return self.fundamentals
