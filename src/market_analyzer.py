import pandas as pd
from typing import Dict
from src.fundamental_analyzer import FundamentalAnalyzer
from src.sector_analyzer import SectorAnalyzer
import numpy as np

class MarketAnalyzer:
    def __init__(self, df: pd.DataFrame, symbol: str):
        # Create a copy to avoid SettingWithCopyWarning
        self.df = df.copy()
        self.symbol = symbol
        self.fundamental_analyzer = FundamentalAnalyzer(symbol)
        
        # Initialize sector analyzer with major sectors
        self.sector_analyzer = SectorAnalyzer({
            "IT": "^CNXIT",
            "BANKING": "^CNXBANK",
            "PHARMA": "^CNXPHARMA",
            "AUTO": "^CNXAUTO",
            "FMCG": "^CNXFMCG",
            "METAL": "^CNXMETAL",
            "ENERGY": "^CNXENERGY"
        })
        
        # Calculate technical indicators
        self._calculate_technical_indicators()
        
    def _calculate_technical_indicators(self):
        """Calculate all technical indicators"""
        # Calculate SMAs with proper NaN handling
        self.df['SMA_50'] = self.df['Close'].rolling(window=50, min_periods=1).mean()
        self.df['SMA_200'] = self.df['Close'].rolling(window=200, min_periods=1).mean()
        
        # Forward fill NaN values for SMAs
        self.df['SMA_50'] = self.df['SMA_50'].ffill()
        self.df['SMA_200'] = self.df['SMA_200'].ffill()
        
        # Calculate RSI with proper NaN handling
        self._calculate_rsi()
        
        # Calculate MACD with proper NaN handling
        exp1 = self.df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['Close'].ewm(span=26, adjust=False).mean()
        self.df['MACD'] = exp1 - exp2
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Calculate Bollinger Bands with proper NaN handling
        self._calculate_bollinger_bands()
        
    def _calculate_rsi(self):
        """Calculate RSI with proper NaN handling"""
        # Calculate price changes
        delta = self.df['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate rolling averages
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        
        # Avoid division by zero
        avg_loss = avg_loss.replace(0, 1e-10)  # Small value to prevent division by zero
        
        # Calculate RS
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        # Forward fill NaN values
        self.df['RSI'] = self.df['RSI'].ffill()
        
    def _calculate_bollinger_bands(self):
        """Calculate Bollinger Bands with proper NaN handling"""
        rolling_mean = self.df['Close'].rolling(window=20, min_periods=1).mean()
        rolling_std = self.df['Close'].rolling(window=20, min_periods=1).std()
        
        # Forward fill NaN values
        rolling_mean = rolling_mean.ffill()
        rolling_std = rolling_std.ffill()
        
        self.df['BB_Upper'] = rolling_mean + (rolling_std * 2)
        self.df['BB_Lower'] = rolling_mean - (rolling_std * 2)
        
        # Forward fill final bands
        self.df['BB_Upper'] = self.df['BB_Upper'].ffill()
        self.df['BB_Lower'] = self.df['BB_Lower'].ffill()
    
    def analyze_market(self) -> Dict[str, str]:
        """
        Analyze market conditions based on technical indicators and sector rotation
        
        Returns:
            Dict[str, str]: Dictionary containing market analysis results
        """
        analysis = {}
        
        # Technical Analysis
        sma_analysis = self._analyze_sma()
        analysis['SMA'] = sma_analysis
        
        rsi_analysis = self._analyze_rsi()
        analysis['RSI'] = rsi_analysis
        
        macd_analysis = self._analyze_macd()
        analysis['MACD'] = macd_analysis
        
        bb_analysis = self._analyze_bollinger_bands()
        analysis['Bollinger Bands'] = bb_analysis
        
        # Try sector rotation analysis, but skip if data not available
        try:
            sector_analysis = self._analyze_sector_rotation()
            analysis.update(sector_analysis)
        except Exception as e:
            print(f"Warning: Could not perform sector analysis: {str(e)}")
            # Add a placeholder message
            analysis['Sector Analysis'] = "Sector analysis not available. Please check data sources."
        
        # Overall Market Status
        analysis['Overall Status'] = self._determine_overall_status(analysis)
        
        return analysis
    
    def _analyze_sma(self) -> str:
        """
        Analyze SMA crossovers
        
        Returns:
            str: SMA analysis result
        """
        latest_sma_50 = self.df['SMA_50'].iloc[-1]
        latest_sma_200 = self.df['SMA_200'].iloc[-1]
        
        if pd.isna(latest_sma_50) or pd.isna(latest_sma_200):
            return "Insufficient data for analysis"
            
        if latest_sma_50 > latest_sma_200:
            return "Bullish (Golden Cross)"
        elif latest_sma_50 < latest_sma_200:
            return "Bearish (Death Cross)"
        else:
            return "Neutral"
    
    def _analyze_rsi(self) -> str:
        """
        Analyze RSI levels
        
        Returns:
            str: RSI analysis result
        """
        latest_rsi = self.df['RSI'].iloc[-1]
        
        if pd.isna(latest_rsi):
            return "Insufficient data for analysis"
            
        if latest_rsi < 30:
            return "Oversold"
        elif latest_rsi > 70:
            return "Overbought"
        else:
            return "Neutral"
    
    def _analyze_macd(self) -> str:
        """
        Analyze MACD signals
        
        Returns:
            str: MACD analysis result
        """
        latest_macd = self.df['MACD'].iloc[-1]
        latest_signal = self.df['MACD_Signal'].iloc[-1]
        
        if pd.isna(latest_macd) or pd.isna(latest_signal):
            return "Insufficient data for analysis"
            
        if latest_macd > latest_signal:
            return "Bullish (MACD above Signal)"
        elif latest_macd < latest_signal:
            return "Bearish (MACD below Signal)"
        else:
            return "Neutral"
    
    def _analyze_bollinger_bands(self) -> str:
        """
        Analyze Bollinger Bands position
        
        Returns:
            str: Bollinger Bands analysis result
        """
        try:
            latest_close = self.df['Close'].iloc[-1]
            latest_bb_upper = self.df['BB_Upper'].iloc[-1]
            latest_bb_lower = self.df['BB_Lower'].iloc[-1]
            
            # Convert to float to ensure we're working with scalar values
            latest_close = float(latest_close)
            latest_bb_upper = float(latest_bb_upper)
            latest_bb_lower = float(latest_bb_lower)
            
            if latest_close > latest_bb_upper:
                return "Overbought (Above Upper Band)"
            elif latest_close < latest_bb_lower:
                return "Oversold (Below Lower Band)"
            else:
                return "Neutral (Within Bands)"
        except (ValueError, TypeError, IndexError):
            return "Insufficient data for analysis"
    
    def _determine_overall_status(self, analysis: Dict[str, str]) -> str:
        """
        Determine overall market status based on multiple indicators
        
        Args:
            analysis (Dict[str, str]): Dictionary containing individual indicator analysis
            
        Returns:
            str: Overall market status
        """
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        # Weighted scoring for different indicators
        weights = {
            'SMA': 0.2,
            'RSI': 0.2,
            'MACD': 0.2,
            'Bollinger Bands': 0.2,
            'Sector Trend': 0.2
        }
        
        # Calculate weighted scores
        total_weight = 0
        total_bullish_score = 0
        total_bearish_score = 0
        
        for indicator, status in analysis.items():
            # Skip sector analysis if it failed
            if indicator == 'Sector Analysis' and 'not available' in status.lower():
                continue
            
            weight = weights.get(indicator, 0)
            if weight > 0:
                total_weight += weight
                
                if "Bullish" in status or "Oversold" in status:
                    total_bullish_score += weight
                elif "Bearish" in status or "Overbought" in status:
                    total_bearish_score += weight
                else:
                    neutral_count += 1
        
        # Calculate percentages
        bullish_percentage = (total_bullish_score / total_weight) * 100
        bearish_percentage = (total_bearish_score / total_weight) * 100
        
        # Determine overall status
        if bullish_percentage > 60:
            return "Bullish Trend"
        elif bearish_percentage > 60:
            return "Bearish Trend"
        elif neutral_count >= 3:  # If most indicators are neutral
            return "Sideways Movement"
        else:
            return "Mixed Signals"
    
    def _analyze_sector_rotation(self) -> Dict[str, str]:
        """
        Analyze sector rotation and performance
        
        Returns:
            Dict[str, str]: Dictionary containing sector rotation analysis
        """
        try:
            # Fetch sector data
            sector_data = self.sector_analyzer.fetch_sector_data()
            
            if not sector_data:
                return {}
                
            # Calculate sector returns
            sector_returns = {}
            for sector, df in sector_data.items():
                if len(df) < 2:  # Need at least 2 data points for return calculation
                    continue
                    
                latest_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                
                if pd.isna(latest_close) or pd.isna(prev_close):
                    continue
                    
                # Calculate 1-week and 1-month returns
                if len(df) >= 5:  # Need at least 5 days for 1-week return
                    one_week_ago = df['Close'].iloc[-5]
                    if not pd.isna(one_week_ago):
                        week_return = ((latest_close - one_week_ago) / one_week_ago) * 100
                        sector_returns[sector] = {
                            '1_week_return': f'{week_return:.2f}%'
                        }
                
                if len(df) >= 20:  # Need at least 20 days for 1-month return
                    one_month_ago = df['Close'].iloc[-20]
                    if not pd.isna(one_month_ago):
                        month_return = ((latest_close - one_month_ago) / one_month_ago) * 100
                        if sector in sector_returns:
                            sector_returns[sector]['1_month_return'] = f'{month_return:.2f}%'
                        else:
                            sector_returns[sector] = {
                                '1_month_return': f'{month_return:.2f}%'
                            }
            
            if not sector_returns:
                return {}
                
            # Determine top and bottom performers
            week_returns = [float(v['1_week_return'].replace('%', '')) for v in sector_returns.values() if '1_week_return' in v]
            month_returns = [float(v['1_month_return'].replace('%', '')) for v in sector_returns.values() if '1_month_return' in v]
            
            if week_returns:
                top_performer_week = max(sector_returns.items(), key=lambda x: float(x[1]['1_week_return'].replace('%', '')) if '1_week_return' in x[1] else float('-inf'))[0]
                bottom_performer_week = min(sector_returns.items(), key=lambda x: float(x[1]['1_week_return'].replace('%', '')) if '1_week_return' in x[1] else float('inf'))[0]
            else:
                top_performer_week = bottom_performer_week = 'Insufficient data'
            
            if month_returns:
                top_performer_month = max(sector_returns.items(), key=lambda x: float(x[1]['1_month_return'].replace('%', '')) if '1_month_return' in x[1] else float('-inf'))[0]
                bottom_performer_month = min(sector_returns.items(), key=lambda x: float(x[1]['1_month_return'].replace('%', '')) if '1_month_return' in x[1] else float('inf'))[0]
            else:
                top_performer_month = bottom_performer_month = 'Insufficient data'
            
            # Determine overall sector trend
            avg_week_return = sum(week_returns) / len(week_returns) if week_returns else 0
            avg_month_return = sum(month_returns) / len(month_returns) if month_returns else 0
            
            if avg_week_return > 0 and avg_month_return > 0:
                trend = "Strong Uptrend"
            elif avg_week_return < 0 and avg_month_return < 0:
                trend = "Strong Downtrend"
            elif avg_week_return > 0 > avg_month_return:
                trend = "Short-term Reversal"
            elif avg_week_return < 0 < avg_month_return:
                trend = "Long-term Reversal"
            else:
                trend = "Mixed Trend"
            
            return {
                'sector_rotation': {
                    'top_performer_week': top_performer_week,
                    'bottom_performer_week': bottom_performer_week,
                    'top_performer_month': top_performer_month,
                    'bottom_performer_month': bottom_performer_month,
                    'trend': trend
                }
            }
            
        except Exception as e:
            print(f"Error in sector analysis: {str(e)}")
            return {}
