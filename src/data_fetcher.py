import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

class DataFetcher:
    def __init__(self, symbol: str, days: int):
        self.symbol = symbol
        self.days = days
        
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch historical market data from Yahoo Finance
        
        Returns:
            pd.DataFrame: DataFrame containing market data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        
        try:
            df = yf.download(self.symbol, start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return pd.DataFrame()

    def save_to_file(self, df: pd.DataFrame, filename: str) -> None:
        """
        Save market data to a CSV file
        
        Args:
            df (pd.DataFrame): DataFrame containing market data
            filename (str): Path to save the file
        """
        try:
            df.to_csv(filename)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """
        Get the latest market data
        
        Returns:
            Optional[pd.DataFrame]: Latest market data or None if error
        """
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period='1d')
            return df
        except Exception as e:
            print(f"Error getting latest data: {str(e)}")
            return None
