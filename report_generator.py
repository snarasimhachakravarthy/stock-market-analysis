import yfinance as yf
import pandas as pd
import os
import datetime
import time
import matplotlib.pyplot as plt
from functools import lru_cache
from datetime import datetime, timedelta
from technical_indicators import calculate_sma, calculate_rsi, calculate_macd, calculate_bollinger_bands

# Rate limiting
import random
RATE_LIMIT_DELAY = 3  # Increased base delay to 3 seconds
last_api_call = 0

def rate_limit():
    global last_api_call
    current_time = time.time()
    time_since_last = current_time - last_api_call
    
    if time_since_last < RATE_LIMIT_DELAY:
        # Add jitter to prevent synchronized requests
        sleep_time = (RATE_LIMIT_DELAY - time_since_last) + random.uniform(0.5, 1.5)
        print(f"Rate limiting: Waiting {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    
    last_api_call = time.time()
    return

# Cache TTL (1 hour)
CACHE_TTL = 3600

# In-memory cache for stock data
stock_data_cache = {}

def get_cached_data(ticker_symbol: str, period: str, interval: str = "1d"):
    """Get data from cache or fetch if not available/expired"""
    cache_key = f"{ticker_symbol}_{period}_{interval}"
    now = time.time()
    
    if cache_key in stock_data_cache:
        data, timestamp = stock_data_cache[cache_key]
        if now - timestamp < CACHE_TTL:
            return data
    
    # Not in cache or expired, fetch fresh data
    rate_limit()
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period, interval=interval)
    
    if not data.empty:
        stock_data_cache[cache_key] = (data, now)
    
    return data

# Ensure charts directory exists
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

def get_stock_data(ticker_symbol: str, period: str = "1y", interval: str = "1d", start: str = None, end: str = None, max_retries: int = 3):
    """
    Fetches historical market data for a given stock ticker with rate limiting, caching, and retry logic.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL')
        period: Data period to download (e.g., '1y', '2y', '6mo')
        interval: Data interval (e.g., '1d' for daily, '1wk' for weekly)
        start: Start date in 'YYYY-MM-DD' format (alternative to period)
        end: End date in 'YYYY-MM-DD' format (defaults to today)
        max_retries: Maximum number of retry attempts on failure
    """
    print(f"\n=== Fetching data for {ticker_symbol} ===")
    print(f"Period: {period}, Interval: {interval}")
    if start and end:
        print(f"Date range: {start} to {end}")
    
    attempt = 0
    while attempt < max_retries:
        try:
            # Try to get data from cache first if not using specific dates
            cache_key = f"{ticker_symbol}_{period if not start else start}_{interval}"
            if start is None and end is None:
                data = get_cached_data(ticker_symbol, period, interval)
                if data is not None and not data.empty:
                    print(f"✅ Using cached data for {ticker_symbol} ({len(data)} data points)")
                    return data
            else:
                data = None
            
            print(f"Attempt {attempt + 1} of {max_retries}...")
            rate_limit()  # Rate limit before each API call
            
            ticker = yf.Ticker(ticker_symbol)
            
            # Add a small delay to prevent rapid API calls
            time.sleep(1 + random.random())  # 1-2 second delay
            
            if start and end:
                print(f"Fetching data from {start} to {end}")
                data = ticker.history(start=start, end=end, interval=interval)
                if not data.empty:
                    print(f"✅ Successfully fetched {len(data)} data points for the specified date range")
            else:
                # Fall back to period-based fetching with retries
                for p in [period, "2y", "1y", "6mo"]:
                    print(f"Trying period: {p}")
                    data = ticker.history(period=p, interval=interval)
                    if not data.empty:
                        print(f"✅ Successfully fetched {len(data)} data points for period {p}")
                        break
            
            if data is not None and not data.empty:
                # Validate the data before returning
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if missing_columns:
                    print(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    print(f"Available columns: {', '.join(data.columns)}")
                    raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
                # Cache the successful fetch if not using specific dates
                if start is None and end is None:
                    stock_data_cache[cache_key] = (data, time.time())
                return data
                
        except Exception as fetch_error:
            wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
            print(f"❌ Attempt {attempt + 1} failed: {str(fetch_error)}")
            print(f"Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        attempt += 1
    
    print(f"❌ All {max_retries} attempts failed for {ticker_symbol}")
    return None

def get_stock_info(ticker_symbol: str):
    """
    Fetches company information for a given stock ticker with rate limiting.
    Returns an empty dict if info is incomplete or error occurs.
    """
    cache_key = f"info_{ticker_symbol}"
    now = time.time()
    
    # Check cache first
    if cache_key in stock_data_cache and (now - stock_data_cache[cache_key][1] < CACHE_TTL):
        return stock_data_cache[cache_key][0]
    
    try:
        rate_limit()
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Check for a few key fields to ensure info is somewhat populated
        required_fields = ['regularMarketPrice', 'currentPrice', 'longName', 'symbol', 'sector']
        if not info or not any(key in info for key in required_fields):
            print(f"Incomplete or invalid info for {ticker_symbol}.")
            return {}
            
        # Cache the result
        stock_data_cache[cache_key] = (info, now)
        return info
        
    except Exception as e:
        print(f"Error in get_stock_info for {ticker_symbol}: {str(e)}")
        return {}


def generate_stock_chart(data: pd.DataFrame, ticker_symbol: str, chart_type: str = "price"):
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(10, 5))
    filename_safe_ticker = ticker_symbol.replace("^", "_").replace(":", "_")
    chart_path = os.path.join(CHARTS_DIR, f"{filename_safe_ticker}_{chart_type}.png")

    try:
        if chart_type == "price":
            ax.plot(data.index, data['Close'], label='Close Price', color='blue', linewidth=1.5)
            if 'SMA_50' in data.columns and not data['SMA_50'].isnull().all():
                ax.plot(data.index, data['SMA_50'], label='50-Day SMA', color='orange', linestyle='--', linewidth=1)
            if 'SMA_200' in data.columns and not data['SMA_200'].isnull().all():
                ax.plot(data.index, data['SMA_200'], label='200-Day SMA', color='green', linestyle='--', linewidth=1)
            if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns and 'BB_Middle' in data.columns and \
               not data['BB_Upper'].isnull().all() and not data['BB_Lower'].isnull().all() and not data['BB_Middle'].isnull().all():
                ax.plot(data.index, data['BB_Middle'], label='BB Middle', color='grey', linestyle=':', linewidth=1)
                ax.plot(data.index, data['BB_Upper'], label='BB Upper', color='lightcoral', linestyle='-.', linewidth=1)
                ax.plot(data.index, data['BB_Lower'], label='BB Lower', color='lightcoral', linestyle='-.', linewidth=1)
                ax.fill_between(data.index, data['BB_Lower'], data['BB_Upper'], color='lightcoral', alpha=0.1)
            ax.set_title(f"{ticker_symbol} - Price Chart", fontsize=12)
            ax.set_ylabel("Price", fontsize=10)
        elif chart_type == "volume":
            if 'Volume' not in data.columns or data['Volume'].isnull().all():
                # print(f"Volume data not available or all NaN for {ticker_symbol} for chart.")
                plt.close(fig)
                return None
            ax.bar(data.index, data['Volume'], label='Volume', color='purple', alpha=0.7)
            ax.set_title(f"{ticker_symbol} - Trading Volume", fontsize=12)
            ax.set_ylabel("Volume", fontsize=10)
        elif chart_type == "rsi":
            if 'RSI_14' not in data.columns or data['RSI_14'].isnull().all():
                # print(f"RSI data not available or all NaN for {ticker_symbol} for chart.")
                plt.close(fig)
                return None
            ax.plot(data.index, data['RSI_14'], label='RSI (14)', color='teal', linewidth=1.5)
            ax.axhline(70, linestyle='--', alpha=0.5, color='red', linewidth=1)
            ax.axhline(30, linestyle='--', alpha=0.5, color='green', linewidth=1)
            ax.set_title(f"{ticker_symbol} - Relative Strength Index (RSI)", fontsize=12)
            ax.set_ylabel("RSI", fontsize=10)
        elif chart_type == "macd":
            if not all(col in data.columns and not data[col].isnull().all() for col in ['MACD', 'Signal', 'MACD_Hist']):
                # print(f"MACD data not available or all NaN for {ticker_symbol} for chart.")
                plt.close(fig)
                return None
            ax.plot(data.index, data['MACD'], label='MACD', color='blue', linewidth=1.5)
            ax.plot(data.index, data['Signal'], label='Signal Line', color='red', linestyle='--', linewidth=1)
            ax.bar(data.index, data['MACD_Hist'], label='Histogram', color='grey', alpha=0.5)
            ax.set_title(f"{ticker_symbol} - MACD", fontsize=12)
            ax.set_ylabel("MACD Value", fontsize=10)
        else:
            print(f"Unknown chart type: {chart_type}")
            plt.close(fig)
            return None

        ax.legend(fontsize=8)
        ax.tick_params(axis='x', rotation=30, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close(fig)
        return chart_path
    except Exception as e:
        print(f"Error generating {chart_type} chart for {ticker_symbol}: {e}")
        plt.close(fig)
        if os.path.exists(chart_path):
             os.remove(chart_path)
        return None

def format_value(value, data_type="number", precision=2):
    if value is None or (isinstance(value, (float, int)) and pd.isna(value)):
        return "N/A"
    if data_type == "number":
        try: return f"{float(value):,.{precision}f}"
        except (ValueError, TypeError): return str(value)
    if data_type == "integer":
        try: return f"{int(value):,}"
        except (ValueError, TypeError): return str(value)
    if data_type == "percentage":
        try: return f"{float(value) * 100:.{precision}f}%"
        except (ValueError, TypeError): return str(value)
    return str(value)

def get_buy_sell_hold_signal(historical_data: pd.DataFrame, stock_info: dict):
    if historical_data is None or historical_data.empty or not stock_info:
        return "N/A", ["Insufficient data for signal generation."]

    required_cols = ['Close', 'SMA_50', 'SMA_200', 'RSI_14', 'MACD', 'Signal', 'MACD_Hist']
    missing_cols = [col for col in required_cols if col not in historical_data.columns or historical_data[col].isnull().all()]
    if missing_cols:
        return "N/A", [f"Signal generation failed: Missing/incomplete indicator data for {', '.join(missing_cols)}."]

    latest_data = historical_data.iloc[-1]
    current_price = stock_info.get('regularMarketPrice', latest_data['Close'])

    if pd.isna(current_price):
        return "N/A", ["Current price data unavailable for signal."]

    buy_score = 0
    sell_score = 0
    reasons = []

    # SMA
    sma50 = latest_data['SMA_50']
    sma200 = latest_data['SMA_200']
    if not pd.isna(sma50) and not pd.isna(sma200):
        if sma50 > sma200:
            buy_score += 1
            reasons.append(f"SMA50 ({format_value(sma50)}) > SMA200 ({format_value(sma200)}) (Golden Cross) - Bullish long-term.")
        else: # sma50 <= sma200
            sell_score += 1
            reasons.append(f"SMA50 ({format_value(sma50)}) < SMA200 ({format_value(sma200)}) (Death Cross) - Bearish long-term.")

    if not pd.isna(sma50):
        if current_price > sma50:
            buy_score += 1
            reasons.append(f"Price ({format_value(current_price)}) > SMA50 ({format_value(sma50)}) - Bullish short-term momentum.")
        else: # current_price <= sma50
            sell_score += 1
            reasons.append(f"Price ({format_value(current_price)}) < SMA50 ({format_value(sma50)}) - Bearish short-term momentum.")

    # RSI
    rsi = latest_data['RSI_14']
    if not pd.isna(rsi):
        if rsi < 30:
            buy_score += 1.5
            reasons.append(f"RSI ({format_value(rsi)}) < 30 (Oversold).")
        elif rsi > 70:
            sell_score += 1.5
            reasons.append(f"RSI ({format_value(rsi)}) > 70 (Overbought).")
        else:
            reasons.append(f"RSI ({format_value(rsi)}) is Neutral (30-70).")

    # MACD
    macd_val = latest_data['MACD']
    signal_val = latest_data['Signal']
    hist_val = latest_data['MACD_Hist']
    if not pd.isna(macd_val) and not pd.isna(signal_val):
        if macd_val > signal_val:
            buy_score += 1
            reasons.append("MACD line > Signal line - Bullish momentum.")
        else: # macd_val <= signal_val
            sell_score += 1
            reasons.append("MACD line < Signal line - Bearish momentum.")
    if not pd.isna(hist_val):
        if hist_val > 0: # Increasing bullish or decreasing bearish momentum
            buy_score += 0.5
            reasons.append("MACD Histogram > 0.")
        else: # hist_val <= 0, Increasing bearish or decreasing bullish momentum
            sell_score += 0.5
            reasons.append("MACD Histogram < 0.")

    if not reasons: return "N/A", ["Not enough valid indicator data to form reasons."]

    # Decision Logic (can be tuned)
    if buy_score > sell_score and buy_score >= 2.0:
        if not pd.isna(rsi) and rsi > 75:
            return "Hold (Buy Cautiously)", reasons + ["RSI is highly overbought (>75), indicating potential for pullback despite buy signals."]
        return "Buy", reasons
    elif sell_score > buy_score and sell_score >= 2.0:
        if not pd.isna(rsi) and rsi < 25:
            return "Hold (Sell Cautiously)", reasons + ["RSI is highly oversold (<25), indicating potential for bounce despite sell signals."]
        return "Sell", reasons
    else:
        return "Hold", reasons + ["Signals are mixed or indecisive."]


def generate_html_report(stocks_data: list, for_pdf_charts: bool = False):
    html_content = """
    <html><head><title>Stock Analysis Report</title><style>
    body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;margin:0;padding:0;background-color:#eef1f5;color:#333;line-height:1.6;}
    header{background-color:#2c3e50;color:#ecf0f1;padding:20px 0;text-align:center;border-bottom:4px solid #3498db;}
    header h1{margin:0;font-size:2.5em;}header p{margin:5px 0 0;font-size:1em;color:#bdc3c7;}
    .report-container{width:90%;max-width:1200px;margin:20px auto;padding:15px;}
    .stock-container{background-color:#fff;padding:20px;margin-bottom:25px;border-radius:8px;box-shadow:0 2px 15px rgba(0,0,0,0.08);border-left:5px solid #3498db;}
    .stock-container h2{color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px;margin-top:0;font-size:1.8em;}
    .stock-container h3{color:#34495e;border-bottom:1px dashed #bdc3c7;padding-bottom:8px;margin-top:25px;font-size:1.4em;}
    table{width:100%;border-collapse:collapse;margin-bottom:20px;}th,td{text-align:left;padding:10px 12px;border:1px solid #dfe6e9;}
    th{background-color:#3498db;color:#fff;font-weight:600;}td{background-color:#fdfdfd;}tr:nth-child(even) td{background-color:#f8f9fa;}
    .charts-container img{max-width:95%;height:auto;margin:10px auto;border:1px solid #bdc3c7;border-radius:6px;box-shadow:0 1px 5px rgba(0,0,0,0.05);display:block;}
    .error{color:#e74c3c;font-weight:bold;padding:10px;background-color:#fadbd8;border-left:3px solid #e74c3c;border-radius:4px;}
    .footer{text-align:center;margin-top:40px;padding:20px;font-size:0.9em;color:#7f8c8d;background-color:#ecf0f1;border-top:1px solid #d4d8d9;}
    .signal-Buy{color:green;font-weight:bold;}.signal-Sell{color:red;font-weight:bold;}
    .signal-Hold, .signal-NA, .signal-Hold span{color:orange;font-weight:bold;} /* Catch all holds and N/A - Fixed N/A */
    .reasons ul{list-style-type:disc;margin-left:20px;padding-left:0;}
    </style></head><body>
    <header><h1>Stock Market Analysis Report</h1><p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p></header>
    <div class='report-container'>"""

    for stock_item in stocks_data:
        ticker = stock_item['ticker']
        info = stock_item.get('info', {})
        charts = stock_item.get('chart_paths', {})
        is_index = stock_item.get('is_index', False)
        signal = stock_item.get('signal', "N/A")
        reasons = stock_item.get('reasons', [])

        html_content += f"<div class='stock-container'>"
        html_content += f"<h2>{(info.get('longName', info.get('shortName', ticker)))} ({ticker})</h2>"

        if info : # Check if info dictionary is not empty
            html_content += "<h3>Key Metrics</h3><table>"
            if is_index:
                html_content += f"<tr><th>Current Value</th><td>{format_value(info.get('regularMarketPrice', info.get('currentPrice')))}</td></tr>"
                html_content += f"<tr><th>Day's Change</th><td>{format_value(info.get('regularMarketChange'))} ({format_value(info.get('regularMarketChangePercent'), 'percentage')})</td></tr>"
                html_content += f"<tr><th>Day's High</th><td>{format_value(info.get('regularMarketDayHigh'))}</td></tr>"
                html_content += f"<tr><th>Day's Low</th><td>{format_value(info.get('regularMarketDayLow'))}</td></tr>"
                html_content += f"<tr><th>Previous Close</th><td>{format_value(info.get('regularMarketPreviousClose'))}</td></tr>"
                html_content += f"<tr><th>Open</th><td>{format_value(info.get('regularMarketOpen'))}</td></tr>"
            else:
                html_content += f"<tr><th>Current Price</th><td>{format_value(info.get('regularMarketPrice', info.get('currentPrice')))}</td></tr>"
                html_content += f"<tr><th>Day's Change</th><td>{format_value(info.get('regularMarketChange'))} ({format_value(info.get('regularMarketChangePercent'), 'percentage')})</td></tr>"
                html_content += f"<tr><th>Day's High / Low</th><td>{format_value(info.get('regularMarketDayHigh'))} / {format_value(info.get('regularMarketDayLow'))}</td></tr>"
                html_content += f"<tr><th>Volume</th><td>{format_value(info.get('regularMarketVolume'), 'integer')}</td></tr>"
                html_content += f"<tr><th>52-Week High / Low</th><td>{format_value(info.get('fiftyTwoWeekHigh'))} / {format_value(info.get('fiftyTwoWeekLow'))}</td></tr>"
                html_content += f"<tr><th>Market Cap</th><td>{format_value(info.get('marketCap'), 'integer')}</td></tr>"
                html_content += f"<tr><th>Sector</th><td>{info.get('sector', 'N/A')}</td></tr>"
                html_content += f"<tr><th>Industry</th><td>{info.get('industry', 'N/A')}</td></tr>"

                html_content += "<tr><th colspan='2' style='text-align:center; background-color:#3498db; color:white;'>Fundamental Ratios</th></tr>"
                html_content += f"<tr><th>P/E Ratio (TTM)</th><td>{format_value(info.get('trailingPE'))}</td></tr>"
                html_content += f"<tr><th>EPS (TTM)</th><td>{format_value(info.get('trailingEps'))}</td></tr>"
                html_content += f"<tr><th>P/B Ratio</th><td>{format_value(info.get('priceToBook'))}</td></tr>"
                html_content += f"<tr><th>Debt-to-Equity Ratio</th><td>{'N/A (Requires balance sheet data)'}</td></tr>"
                html_content += f"<tr><th>Dividend Yield</th><td>{format_value(info.get('dividendYield'), 'percentage')}</td></tr>"
                html_content += f"<tr><th>PEG Ratio</th><td>{format_value(info.get('pegRatio'))}</td></tr>"
            html_content += "</table>"

            if not is_index: # Actionable insights and signals only for stocks
                html_content += "<h3>Signal & Technical Insights</h3>"
                # Normalize signal for CSS class (e.g., "Hold (Buy Cautiously)" -> "signal-Hold")
                signal_class_key = signal.split(" ")[0].replace("(", "").strip()
                signal_class = f"signal-{signal_class_key if signal_class_key in ['Buy', 'Sell', 'Hold', 'N/A'] else 'Hold'}"

                html_content += f"<p><strong>Signal: <span class='{signal_class}'>{signal}</span></strong></p>"
                if reasons:
                    html_content += "<div class='reasons'><strong>Key Reasons / Observations:</strong><ul>"
                    for reason in reasons:
                        html_content += f"<li>{reason}</li>"
                    html_content += "</ul></div>"
        else: # Info is empty
            html_content += "<p class='error'>Could not retrieve company/index information. Analysis incomplete.</p>"

        if charts: # Charts section
            html_content += "<h3>Charts</h3><div class='charts-container'>"
            price_chart_path = charts.get("price", "")
            if price_chart_path: html_content += f"<img src='{price_chart_path}' alt='{ticker} Price Chart'><br>"

            if not for_pdf_charts and not is_index: # Volume and MACD only for HTML full report & stocks
                volume_chart_path = charts.get("volume", "")
                if volume_chart_path: html_content += f"<img src='{volume_chart_path}' alt='{ticker} Volume Chart'><br>"
                macd_chart_path = charts.get("macd", "")
                if macd_chart_path: html_content += f"<img src='{macd_chart_path}' alt='{ticker} MACD Chart'><br>"

            rsi_chart_path = charts.get("rsi", "") # RSI for all (stocks/indices, PDF/HTML)
            if rsi_chart_path: html_content += f"<img src='{rsi_chart_path}' alt='{ticker} RSI Chart'><br>"
            html_content += "</div>"

        if stock_item.get('error') and not info : # Display error only if info was also missing
             html_content += f"<p class='error'>Error processing this stock: {stock_item['error']}</p>"
        html_content += "</div>"
    html_content += """</div><div class='footer'><p>Disclaimer: Data from Yahoo Finance. For informational purposes only. Not financial advice.</p></div></body></html>"""
    return html_content

def write_html_to_file(html_content: str, report_filepath: str):
    try:
        with open(report_filepath, 'w', encoding='utf-8') as f: f.write(html_content) # Added encoding
        print(f"HTML report generated and saved to: {report_filepath}")
    except Exception as e: print(f"Error writing HTML report to file: {e}")

def read_tickers_from_csv(csv_filepath: str = "stocks_list.csv"):
    try:
        df = pd.read_csv(csv_filepath)
        if 'Ticker' not in df.columns: return []
        return df['Ticker'].dropna().unique().tolist()
    except FileNotFoundError: return []
    except Exception: return []

def main():
    tickers = read_tickers_from_csv()
    if not tickers:
        print("No tickers to process. Exiting.")
        return

    all_stocks_data = []
    data_period = "1y"

    for ticker_symbol in tickers:
        print(f"\nProcessing {ticker_symbol} for HTML report...")
        stock_data_item = {'ticker': ticker_symbol, 'info': {}, 'historical_data': None, 'chart_paths': {}, 'error': None, 'signal': "N/A", 'reasons': []}
        is_index_ticker = ticker_symbol.startswith('^')
        stock_data_item['is_index'] = is_index_ticker

        stock_info = get_stock_info(ticker_symbol)
        stock_data_item['info'] = stock_info # Store even if empty

        historical_data = get_stock_data(ticker_symbol, period=data_period)
        if historical_data is None and not stock_info : # If both fail, then major error
            stock_data_item['error'] = f"Could not fetch historical data or info."
            all_stocks_data.append(stock_data_item)
            continue
        stock_data_item['historical_data'] = historical_data

        if historical_data is not None:
            historical_data['SMA_50'] = calculate_sma(historical_data, window=50)
            historical_data['SMA_200'] = calculate_sma(historical_data, window=200)
            historical_data['RSI_14'] = calculate_rsi(historical_data, window=14)
            macd_line, signal_line, hist = calculate_macd(historical_data)
            if macd_line is not None: historical_data['MACD'] = macd_line
            if signal_line is not None: historical_data['Signal'] = signal_line # MACD's signal line
            if hist is not None: historical_data['MACD_Hist'] = hist
            bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(historical_data)
            if bb_middle is not None: historical_data['BB_Middle'] = bb_middle
            if bb_upper is not None: historical_data['BB_Upper'] = bb_upper
            if bb_lower is not None: historical_data['BB_Lower'] = bb_lower

            stock_data_item['chart_paths']['price'] = generate_stock_chart(historical_data, ticker_symbol, "price")
            if not is_index_ticker:
                 stock_data_item['chart_paths']['volume'] = generate_stock_chart(historical_data, ticker_symbol, "volume")
            stock_data_item['chart_paths']['rsi'] = generate_stock_chart(historical_data, ticker_symbol, "rsi")
            stock_data_item['chart_paths']['macd'] = generate_stock_chart(historical_data, ticker_symbol, "macd")

            if not is_index_ticker and stock_info:
                signal, reasons = get_buy_sell_hold_signal(historical_data, stock_info)
                stock_data_item['signal'] = signal
                stock_data_item['reasons'] = reasons
        else: # Historical data is None, but stock_info might be present
            stock_data_item['error'] = stock_data_item.get('error', "") + " Missing historical data for full analysis."

        all_stocks_data.append(stock_data_item)

    html_output = generate_html_report(all_stocks_data, for_pdf_charts=False)
    if html_output:
        write_html_to_file(html_output, "stock_analysis_full_report.html") # Save full HTML report
    print("\nHTML Report generation process complete.")


if __name__ == '__main__':
    from weasyprint import HTML

    tickers_for_pdf = read_tickers_from_csv()
    if not tickers_for_pdf:
        print("No tickers in stocks_list.csv to generate PDF report. Exiting.")
    else:
        print(f"Generating PDF for tickers: {tickers_for_pdf}")
        pdf_stocks_data = []
        data_period_pdf = "1y"

        for ticker_symbol in tickers_for_pdf:
            print(f"\nProcessing {ticker_symbol} for PDF...")
            stock_data_item = {'ticker': ticker_symbol, 'info': {}, 'historical_data': None, 'chart_paths': {}, 'error': None, 'signal': "N/A", 'reasons': []}
            is_index_ticker = ticker_symbol.startswith('^')
            stock_data_item['is_index'] = is_index_ticker

            stock_info = get_stock_info(ticker_symbol)
            stock_data_item['info'] = stock_info

            historical_data = get_stock_data(ticker_symbol, period=data_period_pdf)
            if historical_data is None and not stock_info:
                stock_data_item['error'] = f"Could not fetch historical data or info."
                pdf_stocks_data.append(stock_data_item)
                continue
            stock_data_item['historical_data'] = historical_data

            if historical_data is not None:
                historical_data['SMA_50'] = calculate_sma(historical_data, window=50)
                historical_data['SMA_200'] = calculate_sma(historical_data, window=200)
                historical_data['RSI_14'] = calculate_rsi(historical_data, window=14)
                bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(historical_data)
                if bb_middle is not None: historical_data['BB_Middle'] = bb_middle
                if bb_upper is not None: historical_data['BB_Upper'] = bb_upper
                if bb_lower is not None: historical_data['BB_Lower'] = bb_lower

                # MACD for signals
                if 'MACD' not in historical_data.columns or historical_data['MACD'].isnull().all():
                    macd_line, signal_line, hist = calculate_macd(historical_data)
                    if macd_line is not None: historical_data['MACD'] = macd_line
                    if signal_line is not None: historical_data['Signal'] = signal_line
                    if hist is not None: historical_data['MACD_Hist'] = hist

                stock_data_item['chart_paths']['price'] = generate_stock_chart(historical_data, ticker_symbol, "price")
                stock_data_item['chart_paths']['rsi'] = generate_stock_chart(historical_data, ticker_symbol, "rsi")

                if not is_index_ticker and stock_info:
                    signal, reasons = get_buy_sell_hold_signal(historical_data, stock_info)
                    stock_data_item['signal'] = signal
                    stock_data_item['reasons'] = reasons
            else: # Historical data is None
                 stock_data_item['error'] = stock_data_item.get('error', "") + " Missing historical data for PDF analysis."

            pdf_stocks_data.append(stock_data_item)

        html_string_for_pdf = generate_html_report(pdf_stocks_data, for_pdf_charts=True)

        if html_string_for_pdf:
            try:
                html = HTML(string=html_string_for_pdf, base_url=f"file://{os.getcwd()}/")
                pdf_path = "stock_report.pdf"
                html.write_pdf(pdf_path)
                print(f"\nPDF report generated: {pdf_path}")
            except Exception as e:
                print(f"Error generating PDF: {e}")
                print("Ensure WeasyPrint and its OS dependencies (Pango, Cairo, GDK-PixBuf) are installed.")
        else:
            print("Could not generate HTML string for PDF conversion.")

    # Call main() if you want to generate the full HTML report when running script directly
    # main()
