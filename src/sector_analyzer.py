import yfinance as yf
import pandas as pd
from typing import Dict, List, Tuple

class SectorAnalyzer:
    def __init__(self, sector_symbols: Dict[str, str]):
        """
        Initialize with sector symbols
        
        Args:
            sector_symbols (Dict[str, str]): Dictionary mapping sector names to their index symbols
                e.g., {"IT": "^CNXIT", "BANKING": "^CNXBANK", "PHARMA": "^CNXPHARMA"}
        """
        self.sector_symbols = sector_symbols
        self.sector_data = {}
        
    def fetch_sector_data(self) -> None:
        """
        Fetch data for all sectors
        """
        for sector, symbol in self.sector_symbols.items():
            try:
                # Get sector index data
                sector_df = yf.download(symbol, period='1mo', interval='1d')
                self.sector_data[sector] = {
                    'df': sector_df,
                    'symbol': symbol
                }
            except Exception as e:
                print(f"Error fetching data for {sector}: {str(e)}")
                self.sector_data[sector] = None
    
    def calculate_sector_performance(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate sector performance metrics
        
        Returns:
            Dict[str, Dict[str, float]]: Dictionary containing sector performance metrics
        """
        performance = {}
        
        for sector, data in self.sector_data.items():
            if data is None:
                continue
            
            df = data['df']
            
            # Calculate 1-week and 1-month returns
            latest_close = df['Close'].iloc[-1]
            week_ago_close = df['Close'].iloc[-5] if len(df) >= 5 else latest_close
            month_ago_close = df['Close'].iloc[-20] if len(df) >= 20 else latest_close
            
            performance[sector] = {
                '1_week_return': ((latest_close - week_ago_close) / week_ago_close) * 100,
                '1_month_return': ((latest_close - month_ago_close) / month_ago_close) * 100,
                'latest_close': latest_close,
                'symbol': data['symbol']
            }
        
        return performance
    
    def analyze_sector_rotation(self) -> Dict[str, Dict[str, str]]:
        """
        Analyze sector rotation and performance
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary containing sector rotation analysis
        """
        performance = self.calculate_sector_performance()
        analysis = {}
        
        # Sort sectors by performance
        sorted_by_week = sorted(
            performance.items(),
            key=lambda x: x[1]['1_week_return'],
            reverse=True
        )
        
        sorted_by_month = sorted(
            performance.items(),
            key=lambda x: x[1]['1_month_return'],
            reverse=True
        )
        
        # Get top and bottom performers
        top_week = sorted_by_week[0][0]
        bottom_week = sorted_by_week[-1][0]
        top_month = sorted_by_month[0][0]
        bottom_month = sorted_by_month[-1][0]
        
        # Create analysis
        analysis['sector_rotation'] = {
            'top_performer_week': top_week,
            'bottom_performer_week': bottom_week,
            'top_performer_month': top_month,
            'bottom_performer_month': bottom_month,
            'trend': self._determine_trend(sorted_by_week)
        }
        
        # Add performance details
        analysis['sector_performance'] = {
            sector: {
                '1_week_return': f"{perf['1_week_return']:.2f}%",
                '1_month_return': f"{perf['1_month_return']:.2f}%",
                'latest_close': perf['latest_close'],
                'symbol': perf['symbol']
            }
            for sector, perf in performance.items()
        }
        
        return analysis
    
    def _determine_trend(self, sorted_sectors: List[Tuple[str, Dict]]) -> str:
        """
        Determine overall market trend based on sector performance
        
        Args:
            sorted_sectors (List[Tuple[str, Dict]]): List of sectors sorted by performance
            
        Returns:
            str: Market trend description
        """
        total_sectors = len(sorted_sectors)
        positive_sectors = sum(1 for _, perf in sorted_sectors if perf['1_week_return'] > 0)
        
        if positive_sectors / total_sectors > 0.6:
            return "Bullish Rotation - Most sectors performing well"
        elif positive_sectors / total_sectors < 0.4:
            return "Bearish Rotation - Most sectors underperforming"
        else:
            return "Mixed Rotation - Sectors divided in performance"
