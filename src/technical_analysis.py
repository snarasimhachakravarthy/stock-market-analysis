import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from typing import Tuple

class TechnicalAnalysis:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def calculate_sma(self, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            period (int): Number of periods for SMA
            
        Returns:
            pd.Series: SMA values
        """
        return self.df['Close'].rolling(window=period).mean()
    
    def calculate_ema(self, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            period (int): Number of periods for EMA
            
        Returns:
            pd.Series: EMA values
        """
        return self.df['Close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, period: int) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            period (int): Number of periods for RSI
            
        Returns:
            pd.Series: RSI values
        """
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, fast_period: int, slow_period: int, signal_period: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD indicators
        
        Args:
            fast_period (int): Fast EMA period
            slow_period (int): Slow EMA period
            signal_period (int): Signal line period
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: MACD line, Signal line, and Histogram
        """
        fast_ema = self.calculate_ema(fast_period)
        slow_ema = self.calculate_ema(slow_period)
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, period: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            period (int): Number of periods for BB
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: Upper band, Middle band, Lower band
        """
        rolling_mean = self.df['Close'].rolling(window=period).mean()
        rolling_std = self.df['Close'].rolling(window=period).std()
        upper_band = rolling_mean + (rolling_std * 2)
        lower_band = rolling_mean - (rolling_std * 2)
        return upper_band, rolling_mean, lower_band
    
    def add_all_indicators(self, config: dict) -> pd.DataFrame:
        """
        Add all technical indicators to the DataFrame
        
        Args:
            config (dict): Configuration dictionary containing indicator periods
            
        Returns:
            pd.DataFrame: DataFrame with all indicators
        """
        # Calculate all indicators
        self.df['SMA_50'] = self.calculate_sma(config['sma']['short_period'])
        self.df['SMA_200'] = self.calculate_sma(config['sma']['long_period'])
        self.df['RSI'] = self.calculate_rsi(config['rsi']['period'])
        
        macd, macd_signal, macd_hist = self.calculate_macd(
            config['macd']['fast_period'],
            config['macd']['slow_period'],
            config['macd']['signal_period']
        )
        
        self.df['MACD'] = macd
        self.df['MACD_Signal'] = macd_signal
        self.df['MACD_Hist'] = macd_hist
        
        # Calculate Bollinger Bands
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(20)
        self.df['BB_Upper'] = upper_bb
        self.df['BB_Middle'] = middle_bb
        self.df['BB_Lower'] = lower_bb
        
        return self.df
