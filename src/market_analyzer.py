import pandas as pd
from typing import Dict, Tuple

class MarketAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def analyze_market(self) -> Dict[str, str]:
        """
        Analyze market conditions based on technical indicators
        
        Returns:
            Dict[str, str]: Dictionary containing market analysis results
        """
        analysis = {}
        
        # SMA Crossover Analysis
        sma_analysis = self._analyze_sma()
        analysis['SMA'] = sma_analysis
        
        # RSI Analysis
        rsi_analysis = self._analyze_rsi()
        analysis['RSI'] = rsi_analysis
        
        # MACD Analysis
        macd_analysis = self._analyze_macd()
        analysis['MACD'] = macd_analysis
        
        # Bollinger Bands Analysis
        bb_analysis = self._analyze_bollinger_bands()
        analysis['Bollinger Bands'] = bb_analysis
        
        # Overall Market Status
        analysis['Overall Status'] = self._determine_overall_status(analysis)
        
        return analysis
    
    def _analyze_sma(self) -> str:
        """
        Analyze SMA crossovers
        
        Returns:
            str: SMA analysis result
        """
        latest_sma_50 = float(self.df['SMA_50'].iloc[-1])
        latest_sma_200 = float(self.df['SMA_200'].iloc[-1])
        
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
        latest_rsi = float(self.df['RSI'].iloc[-1])
        
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
        latest_macd = float(self.df['MACD'].iloc[-1])
        latest_signal = float(self.df['MACD_Signal'].iloc[-1])
        
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
        latest_close = float(self.df['Close'].iloc[-1])
        latest_bb_upper = float(self.df['BB_Upper'].iloc[-1])
        latest_bb_lower = float(self.df['BB_Lower'].iloc[-1])
        
        if latest_close > latest_bb_upper:
            return "Overbought (Above Upper Band)"
        elif latest_close < latest_bb_lower:
            return "Oversold (Below Lower Band)"
        else:
            return "Neutral (Within Bands)"
    
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
        
        for indicator, status in analysis.items():
            if "Bullish" in status or "Oversold" in status:
                bullish_count += 1
            elif "Bearish" in status or "Overbought" in status:
                bearish_count += 1
        
        total_indicators = len(analysis)
        bullish_percentage = (bullish_count / total_indicators) * 100
        bearish_percentage = (bearish_count / total_indicators) * 100
        
        if bullish_percentage > 70:
            return "Undervalued"
        elif bearish_percentage > 70:
            return "Overvalued"
        else:
            return "Fairly Valued"
