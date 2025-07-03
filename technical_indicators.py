import pandas as pd

def calculate_sma(data: pd.DataFrame, window: int, price_col: str = 'Close'):
    """
    Calculates the Simple Moving Average (SMA).

    Args:
        data: Pandas DataFrame with historical price data. Must contain 'price_col'.
        window: The window period for the SMA.
        price_col: The name of the column containing the price data.

    Returns:
        Pandas Series with SMA values, or None if input is invalid.
    """
    if price_col not in data.columns:
        print(f"Error: Price column '{price_col}' not found in data.")
        return None
    if not isinstance(window, int) or window <= 0:
        print("Error: SMA window must be a positive integer.")
        return None
    if len(data) < window:
        print(f"Error: Data length ({len(data)}) is less than SMA window ({window}).")
        return None

    return data[price_col].rolling(window=window).mean()

def calculate_rsi(data: pd.DataFrame, window: int = 14, price_col: str = 'Close'):
    """
    Calculates the Relative Strength Index (RSI).

    Args:
        data: Pandas DataFrame with historical price data. Must contain 'price_col'.
        window: The window period for RSI (typically 14).
        price_col: The name of the column containing the price data.

    Returns:
        Pandas Series with RSI values, or None if input is invalid.
    """
    if price_col not in data.columns:
        print(f"Error: Price column '{price_col}' not found in data.")
        return None
    if not isinstance(window, int) or window <= 0:
        print("Error: RSI window must be a positive integer.")
        return None
    if len(data) < window + 1: # Need at least window + 1 data points for delta
        print(f"Error: Data length ({len(data)}) is insufficient for RSI window ({window}). Needs at least {window+1}.")
        return None

    delta = data[price_col].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9, price_col: str = 'Close'):
    """
    Calculates the Moving Average Convergence Divergence (MACD).

    Args:
        data: Pandas DataFrame with historical price data. Must contain 'price_col'.
        short_window: The window for the short-term EMA.
        long_window: The window for the long-term EMA.
        signal_window: The window for the signal line EMA.
        price_col: The name of the column containing the price data.

    Returns:
        A tuple containing three Pandas Series: (MACD line, Signal line, MACD Histogram),
        or (None, None, None) if input is invalid.
    """
    if price_col not in data.columns:
        print(f"Error: Price column '{price_col}' not found in data.")
        return None, None, None
    if not all(isinstance(w, int) and w > 0 for w in [short_window, long_window, signal_window]):
        print("Error: MACD windows must be positive integers.")
        return None, None, None
    if short_window >= long_window:
        print("Error: Short window for MACD must be less than long window.")
        return None, None, None
    if len(data) < long_window:
        print(f"Error: Data length ({len(data)}) is less than MACD long window ({long_window}).")
        return None, None, None

    short_ema = data[price_col].ewm(span=short_window, adjust=False).mean()
    long_ema = data[price_col].ewm(span=long_window, adjust=False).mean()

    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std_dev: int = 2, price_col: str = 'Close'):
    """
    Calculates Bollinger Bands.

    Args:
        data: Pandas DataFrame with historical price data. Must contain 'price_col'.
        window: The window period for the moving average and standard deviation.
        num_std_dev: The number of standard deviations for the upper and lower bands.
        price_col: The name of the column containing the price data.

    Returns:
        A tuple containing three Pandas Series: (Middle Band, Upper Band, Lower Band),
        or (None, None, None) if input is invalid.
    """
    if price_col not in data.columns:
        print(f"Error: Price column '{price_col}' not found in data.")
        return None, None, None
    if not isinstance(window, int) or window <= 0:
        print("Error: Bollinger Bands window must be a positive integer.")
        return None, None, None
    if not isinstance(num_std_dev, (int, float)) or num_std_dev <= 0:
        print("Error: Bollinger Bands num_std_dev must be a positive number.")
        return None, None, None
    if len(data) < window:
        print(f"Error: Data length ({len(data)}) is less than Bollinger Bands window ({window}).")
        return None, None, None

    middle_band = data[price_col].rolling(window=window).mean()
    std_dev = data[price_col].rolling(window=window).std()

    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    return middle_band, upper_band, lower_band

if __name__ == '__main__':
    # Create a sample DataFrame for testing
    sample_data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                                '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20']),
        'Close': [10, 12, 11, 13, 15, 14, 16, 17, 18, 20, 19, 21, 22, 23, 25, 24, 26, 28, 27, 29]
    }
    df = pd.DataFrame(sample_data)
    df.set_index('Date', inplace=True)

    print("--- Testing SMA ---")
    df['SMA_5'] = calculate_sma(df, window=5)
    print(df[['Close', 'SMA_5']].head(10))

    print("\n--- Testing RSI ---")
    # Need more data for a meaningful RSI, this is just a functional test
    # For a window of 14, we need at least 15 data points. Let's use a smaller window for this sample.
    df['RSI_5'] = calculate_rsi(df, window=5)
    print(df[['Close', 'RSI_5']].head(10))

    # Test RSI with insufficient data
    print("\n--- Testing RSI with insufficient data ---")
    small_df = df.head(3)
    small_df['RSI_5'] = calculate_rsi(small_df, window=5)
    print(small_df)


    print("\n--- Testing MACD ---")
    # Need more data for meaningful MACD. Using small windows for functional test.
    df['MACD'], df['Signal'], df['Hist'] = calculate_macd(df, short_window=5, long_window=10, signal_window=3)
    print(df[['Close', 'MACD', 'Signal', 'Hist']].head(15))

    print("\n--- Testing Bollinger Bands ---")
    df['BB_Middle'], df['BB_Upper'], df['BB_Lower'] = calculate_bollinger_bands(df, window=5, num_std_dev=2)
    print(df[['Close', 'BB_Middle', 'BB_Upper', 'BB_Lower']].head(10))

    print("\n--- Testing with invalid inputs ---")
    print("SMA with invalid window:", calculate_sma(df, window=0))
    print("RSI with invalid price column:", calculate_rsi(df, price_col='NonExistent'))
    print("MACD with short_window >= long_window:", calculate_macd(df, short_window=10, long_window=5))
    print("Bollinger Bands with insufficient data:", calculate_bollinger_bands(df.head(3), window=5))

    # Test with a larger, more realistic dataset if possible, or by fetching actual stock data
    # For now, this confirms the functions run and handle basic edge cases.
    print("\nTechnical indicator calculations script complete.")
