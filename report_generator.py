import yfinance as yf
import pandas as pd

def get_stock_data(ticker_symbol: str, period: str = "1y", interval: str = "1d"):
    """
    Fetches historical market data for a given stock ticker.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., "RELIANCE.NS").
        period: The period for which to fetch data (e.g., "1mo", "1y", "max").
        interval: The interval of data points (e.g., "1d", "1wk", "1mo").

    Returns:
        A pandas DataFrame with historical data (Date, Open, High, Low, Close, Volume),
        or None if an error occurs.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period=period, interval=interval)
        if history.empty:
            print(f"No historical data found for {ticker_symbol} for the period {period}.")
            return None
        return history
    except Exception as e:
        print(f"Error fetching historical data for {ticker_symbol}: {e}")
        return None

def get_stock_info(ticker_symbol: str):
    """
    Fetches company information for a given stock ticker.

    Args:
        ticker_symbol: The stock ticker symbol.

    Returns:
        A dictionary containing company information, or None if an error occurs.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        if not info or info.get('regularMarketPrice') is None: # Check if info is empty or lacks key data
            print(f"Could not retrieve valid company info for {ticker_symbol}. Ticker might be invalid or delisted.")
            return None
        return info
    except Exception as e:
        print(f"Error fetching company info for {ticker_symbol}: {e}")
        return None

if __name__ == '__main__':
    # Example Usage
    sample_indian_ticker = "RELIANCE.NS"  # Example: Reliance Industries on NSE
    sample_index_ticker = "^NSEI"      # Example: NIFTY 50 Index

    print(f"--- Fetching Historical Data for {sample_indian_ticker} ---")
    historical_data = get_stock_data(sample_indian_ticker, period="1mo")
    if historical_data is not None:
        print(historical_data.head())
        print(f"\n--- Fetching Company Info for {sample_indian_ticker} ---")
        company_info = get_stock_info(sample_indian_ticker)
        if company_info:
            print(f"Company Name: {company_info.get('longName')}")
            print(f"Sector: {company_info.get('sector')}")
            print(f"Industry: {company_info.get('industry')}")
            print(f"Market Cap: {company_info.get('marketCap')}")
            print(f"P/E Ratio: {company_info.get('trailingPE')}")
            print(f"Forward P/E Ratio: {company_info.get('forwardPE')}")
            print(f"EPS (TTM): {company_info.get('trailingEps')}")
            print(f"Price/Book: {company_info.get('priceToBook')}")
            print(f"Dividend Yield: {company_info.get('dividendYield')}")
            print(f"52 Week High: {company_info.get('fiftyTwoWeekHigh')}")
            print(f"52 Week Low: {company_info.get('fiftyTwoWeekLow')}")


    print(f"\n--- Fetching Historical Data for Index {sample_index_ticker} ---")
    index_data = get_stock_data(sample_index_ticker, period="1mo")
    if index_data is not None:
        print(index_data.head())

    print(f"\n--- Fetching Info for Index {sample_index_ticker} ---")
    # .info often works for indices too, providing general market data
    index_info = get_stock_info(sample_index_ticker)
    if index_info:
        print(f"Index Name: {index_info.get('longName', index_info.get('shortName'))}")
        print(f"Previous Close: {index_info.get('regularMarketPreviousClose')}")
        print(f"Open: {index_info.get('regularMarketOpen')}")
        print(f"Day's High: {index_info.get('dayHigh')}")
        print(f"Day's Low: {index_info.get('dayLow')}")

    # Example of a potentially problematic ticker
    invalid_ticker = "NONEXISTENTTICKER.NS"
    print(f"\n--- Fetching Data for Invalid Ticker {invalid_ticker} ---")
    invalid_data = get_stock_data(invalid_ticker)
    if invalid_data is None:
        print("Correctly handled invalid ticker for historical data.")
    invalid_info = get_stock_info(invalid_ticker)
    if invalid_info is None:
        print("Correctly handled invalid ticker for company info.")

    # Example of a ticker that might not have all info fields (e.g., a less common stock or different type of security)
    # For instance, some ETFs or smaller caps might miss certain fields like PEG ratio directly in .info
    # Using a known valid ticker for this test, but the principle applies
    less_common_ticker = "INFY.NS" # Infosys as an example, usually has good data
    print(f"\n--- Fetching Company Info for {less_common_ticker} to check field availability ---")
    less_common_info = get_stock_info(less_common_ticker)
    if less_common_info:
        print(f"Company Name: {less_common_info.get('longName')}")
        print(f"PEG Ratio (from .info): {less_common_info.get('pegRatio')}") # PEG is often not directly available
        print(f"Trailing P/E: {less_common_info.get('trailingPE')}")
        print(f"Forward P/E: {less_common_info.get('forwardPE')}")

    # It's important to note that not all fundamental ratios are directly available in .info
    # Some, like D/E, might need to be calculated from balance sheet data if required.
import os
import datetime
import matplotlib.pyplot as plt
from technical_indicators import calculate_sma, calculate_rsi, calculate_macd, calculate_bollinger_bands

# Ensure charts directory exists
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

def generate_stock_chart(data: pd.DataFrame, ticker_symbol: str, chart_type: str = "price"):
    """
    Generates and saves a chart for the given stock data.

    Args:
        data: Pandas DataFrame with historical data and calculated indicators.
        ticker_symbol: The stock ticker symbol for naming the chart.
        chart_type: Type of chart to generate ("price", "volume", "rsi", "macd").

    Returns:
        Filepath of the generated chart image, or None if error.
    """
    plt.style.use('seaborn-v0_8-darkgrid') # Using a seaborn style
    fig, ax = plt.subplots(figsize=(12, 6))
    filename_safe_ticker = ticker_symbol.replace("^", "_") # Make ticker safe for filenames
    chart_path = os.path.join(CHARTS_DIR, f"{filename_safe_ticker}_{chart_type}.png")

    try:
        if chart_type == "price":
            ax.plot(data.index, data['Close'], label='Close Price', color='blue')
            if 'SMA_50' in data.columns:
                ax.plot(data.index, data['SMA_50'], label='50-Day SMA', color='orange', linestyle='--')
            if 'SMA_200' in data.columns:
                ax.plot(data.index, data['SMA_200'], label='200-Day SMA', color='green', linestyle='--')
            if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns and 'BB_Middle' in data.columns:
                ax.plot(data.index, data['BB_Middle'], label='BB Middle', color='grey', linestyle=':')
                ax.plot(data.index, data['BB_Upper'], label='BB Upper', color='lightcoral', linestyle='-.')
                ax.plot(data.index, data['BB_Lower'], label='BB Lower', color='lightcoral', linestyle='-.')
                ax.fill_between(data.index, data['BB_Lower'], data['BB_Upper'], color='lightcoral', alpha=0.1)
            ax.set_title(f"{ticker_symbol} - Price, SMAs, Bollinger Bands")
            ax.set_ylabel("Price")

        elif chart_type == "volume":
            if 'Volume' not in data.columns:
                print(f"Volume data not available for {ticker_symbol}")
                return None
            ax.bar(data.index, data['Volume'], label='Volume', color='purple', alpha=0.7)
            ax.set_title(f"{ticker_symbol} - Trading Volume")
            ax.set_ylabel("Volume")

        elif chart_type == "rsi":
            if 'RSI_14' not in data.columns:
                print(f"RSI data not available for {ticker_symbol}")
                return None
            ax.plot(data.index, data['RSI_14'], label='RSI (14)', color='teal')
            ax.axhline(70, linestyle='--', alpha=0.5, color='red')
            ax.axhline(30, linestyle='--', alpha=0.5, color='green')
            ax.set_title(f"{ticker_symbol} - Relative Strength Index (RSI)")
            ax.set_ylabel("RSI")

        elif chart_type == "macd":
            if 'MACD' not in data.columns or 'Signal' not in data.columns or 'MACD_Hist' not in data.columns:
                print(f"MACD data not available for {ticker_symbol}")
                return None
            ax.plot(data.index, data['MACD'], label='MACD', color='blue')
            ax.plot(data.index, data['Signal'], label='Signal Line', color='red', linestyle='--')
            ax.bar(data.index, data['MACD_Hist'], label='Histogram', color='grey', alpha=0.5)
            ax.set_title(f"{ticker_symbol} - MACD")
            ax.set_ylabel("MACD Value")

        else:
            print(f"Unknown chart type: {chart_type}")
            return None

        ax.legend()
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close(fig) # Close the figure to free memory
        return chart_path
    except Exception as e:
        print(f"Error generating {chart_type} chart for {ticker_symbol}: {e}")
        if os.path.exists(chart_path): # Attempt to remove partially created file
             os.remove(chart_path)
        return None


def format_value(value, data_type="number", precision=2):
    """Formats value for HTML display, handling Nones."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if data_type == "number":
        try:
            return f"{float(value):,.{precision}f}"
        except (ValueError, TypeError):
            return str(value) # fallback for non-numeric that slipped through
    if data_type == "integer":
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)
    if data_type == "percentage":
        try:
            return f"{float(value) * 100:.{precision}f}%"
        except (ValueError, TypeError):
            return str(value)
    return str(value)


def generate_html_report(stocks_data: list, report_filepath: str = "stock_report.html"):
    """
    Generates an HTML report from the collected stock data and charts.

    Args:
        stocks_data: A list of dictionaries, where each dictionary contains
                     data for a single stock (info, historical_data, chart_paths).
        report_filepath: Path to save the HTML report.
    """
    html_content = """
    <html>
    <head>
        <title>Daily Stock Market Analysis Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #eef1f5;
                color: #333;
                line-height: 1.6;
            }
            header {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 20px 0;
                text-align: center;
                border-bottom: 4px solid #3498db;
            }
            header h1 {
                margin: 0;
                font-size: 2.5em;
            }
            header p {
                margin: 5px 0 0;
                font-size: 1em;
                color: #bdc3c7;
            }
            .report-container {
                width: 90%;
                max-width: 1200px;
                margin: 20px auto;
                padding: 15px;
            }
            .stock-container {
                background-color: #fff;
                padding: 20px;
                margin-bottom: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 15px rgba(0,0,0,0.08);
                border-left: 5px solid #3498db; /* Accent border */
            }
            .stock-container h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
                font-size: 1.8em;
            }
            .stock-container h3 {
                color: #34495e;
                border-bottom: 1px dashed #bdc3c7;
                padding-bottom: 8px;
                margin-top: 25px;
                font-size: 1.4em;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                text-align: left;
                padding: 10px 12px;
                border: 1px solid #dfe6e9;
            }
            th {
                background-color: #3498db;
                color: #ffffff;
                font-weight: 600;
            }
            td {
                 background-color: #fdfdfd;
            }
            tr:nth-child(even) td {
                background-color: #f8f9fa;
            }
            .charts-container {
                text-align: center; /* Center charts */
            }
            .charts-container img {
                max-width: 95%; /* Slightly less than 100% to prevent overflow with borders/padding */
                height: auto;
                margin: 10px auto;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                box-shadow: 0 1px 5px rgba(0,0,0,0.05);
                display: block; /* Ensures margin auto works for centering */
            }
            .error {
                color: #e74c3c;
                font-weight: bold;
                padding: 10px;
                background-color: #fadbd8;
                border-left: 3px solid #e74c3c;
                border-radius: 4px;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                font-size: 0.9em;
                color: #7f8c8d;
                background-color: #ecf0f1;
                border-top: 1px solid #d4d8d9;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Daily Stock Market Analysis Report</h1>
            <p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </header>
        <div class='report-container'>
    """

    for stock_item in stocks_data:
        ticker = stock_item['ticker']
        info = stock_item['info']
        charts = stock_item['chart_paths']
        is_index = stock_item.get('is_index', False)

        html_content += f"<div class='stock-container'>"
        html_content += f"<h2>{(info.get('longName', info.get('shortName', ticker)) if info else ticker)} ({ticker})</h2>"

        if info:
            html_content += "<h3>Key Metrics</h3><table>"
            if is_index:
                html_content += f"<tr><th>Current Value</th><td>{format_value(info.get('regularMarketPrice'))}</td></tr>"
                html_content += f"<tr><th>Day's Change</th><td>{format_value(info.get('regularMarketChange'))} ({format_value(info.get('regularMarketChangePercent'), 'percentage')})</td></tr>"
                html_content += f"<tr><th>Day's High</th><td>{format_value(info.get('regularMarketDayHigh'))}</td></tr>"
                html_content += f"<tr><th>Day's Low</th><td>{format_value(info.get('regularMarketDayLow'))}</td></tr>"
                html_content += f"<tr><th>Previous Close</th><td>{format_value(info.get('regularMarketPreviousClose'))}</td></tr>"
                html_content += f"<tr><th>Open</th><td>{format_value(info.get('regularMarketOpen'))}</td></tr>"
            else: # Individual Stock
                html_content += f"<tr><th>Current Price</th><td>{format_value(info.get('regularMarketPrice'))}</td></tr>"
                html_content += f"<tr><th>Day's Change</th><td>{format_value(info.get('regularMarketChange'))} ({format_value(info.get('regularMarketChangePercent'), 'percentage')})</td></tr>"
                html_content += f"<tr><th>Day's High / Low</th><td>{format_value(info.get('regularMarketDayHigh'))} / {format_value(info.get('regularMarketDayLow'))}</td></tr>"
                html_content += f"<tr><th>Volume</th><td>{format_value(info.get('regularMarketVolume'), 'integer')}</td></tr>"
                html_content += f"<tr><th>52-Week High / Low</th><td>{format_value(info.get('fiftyTwoWeekHigh'))} / {format_value(info.get('fiftyTwoWeekLow'))}</td></tr>"
                html_content += f"<tr><th>Market Cap</th><td>{format_value(info.get('marketCap'), 'integer')}</td></tr>"
                html_content += f"<tr><th>Sector</th><td>{info.get('sector', 'N/A')}</td></tr>"
                html_content += f"<tr><th>Industry</th><td>{info.get('industry', 'N/A')}</td></tr>"

                html_content += "<tr><th colspan='2' style='text-align:center; background-color:#3498db; color:white;'>Fundamental Ratios</th></tr>" # Updated style for sub-header
                html_content += f"<tr><th>P/E Ratio (TTM)</th><td>{format_value(info.get('trailingPE'))}</td></tr>"
                html_content += f"<tr><th>EPS (TTM)</th><td>{format_value(info.get('trailingEps'))}</td></tr>"
                html_content += f"<tr><th>P/B Ratio</th><td>{format_value(info.get('priceToBook'))}</td></tr>"
                html_content += f"<tr><th>Debt-to-Equity Ratio</th><td>{'N/A (Requires balance sheet data)'}</td></tr>"
                html_content += f"<tr><th>Dividend Yield</th><td>{format_value(info.get('dividendYield'), 'percentage')}</td></tr>"
                html_content += f"<tr><th>PEG Ratio</th><td>{format_value(info.get('pegRatio'))}</td></tr>"
            html_content += "</table>"

            # Basic Inferences Section
            if not is_index and stock_item.get('historical_data') is not None and info: # Ensure info is available for close_price
                historical_df = stock_item['historical_data']
                html_content += "<h3>Quick Inferences</h3><table>"

                # RSI Inference
                rsi_latest = historical_df['RSI_14'].iloc[-1] if 'RSI_14' in historical_df.columns and not historical_df['RSI_14'].empty and not pd.isna(historical_df['RSI_14'].iloc[-1]) else None
                rsi_inference = "N/A"
                if rsi_latest is not None:
                    if rsi_latest > 70: rsi_inference = f"<span style='color: #e74c3c;'>Overbought ({format_value(rsi_latest)})</span>"
                    elif rsi_latest < 30: rsi_inference = f"<span style='color: #2ecc71;'>Oversold ({format_value(rsi_latest)})</span>"
                    else: rsi_inference = f"Neutral ({format_value(rsi_latest)})"
                html_content += f"<tr><th>RSI (14) Status</th><td>{rsi_inference}</td></tr>"

                # SMA Inference (Price vs SMA50)
                close_price = info.get('regularMarketPrice') # Use current price from info
                sma50_latest = historical_df['SMA_50'].iloc[-1] if 'SMA_50' in historical_df.columns and not historical_df['SMA_50'].empty and not pd.isna(historical_df['SMA_50'].iloc[-1]) else None
                sma_status = "N/A"
                if close_price is not None and sma50_latest is not None:
                    if close_price > sma50_latest: sma_status = f"<span style='color: #2ecc71;'>Price above 50-Day SMA</span> (Price: {format_value(close_price)}, SMA50: {format_value(sma50_latest)}) - Potential Uptrend"
                    elif close_price < sma50_latest: sma_status = f"<span style='color: #e74c3c;'>Price below 50-Day SMA</span> (Price: {format_value(close_price)}, SMA50: {format_value(sma50_latest)}) - Potential Downtrend"
                    else: sma_status = f"Price near 50-Day SMA (Price: {format_value(close_price)}, SMA50: {format_value(sma50_latest)})"
                html_content += f"<tr><th>Price vs SMA50</th><td>{sma_status}</td></tr>"

                # P/E Ratio (very basic, no industry comparison yet)
                pe_ratio = info.get('trailingPE')
                pe_inference = "N/A"
                if pe_ratio is not None and not pd.isna(pe_ratio) :
                    if pe_ratio > 30: pe_inference = f"High P/E ({format_value(pe_ratio)}) - Potentially Overvalued or High Growth Expected"
                    elif pe_ratio > 0 and pe_ratio < 15: pe_inference = f"Low P/E ({format_value(pe_ratio)}) - Potentially Undervalued or Lower Growth Expected"
                    elif pe_ratio <=0 : pe_inference = f"Negative/Zero P/E ({format_value(pe_ratio)}) - Company may be loss-making"
                    else: pe_inference = f"Moderate P/E ({format_value(pe_ratio)})"
                html_content += f"<tr><th>P/E Ratio Status</th><td>{pe_inference}</td></tr>"

                html_content += "</table>"
        elif not info and not is_index: # Case where info is None for a stock
             html_content += "<p class='error'>Could not retrieve company information to generate inferences.</p>"
        elif not stock_item.get('historical_data') and not is_index:
             html_content += "<p class='error'>Could not retrieve historical data to generate inferences.</p>"


        if charts:
            html_content += "<h3>Charts</h3><div class='charts-container'>"
            if charts.get("price"): html_content += f"<img src='{charts['price']}' alt='{ticker} Price Chart'><br>"
            if charts.get("volume") and not is_index : html_content += f"<img src='{charts['volume']}' alt='{ticker} Volume Chart'><br>"
            if charts.get("rsi"): html_content += f"<img src='{charts['rsi']}' alt='{ticker} RSI Chart'><br>"
            if charts.get("macd"): html_content += f"<img src='{charts['macd']}' alt='{ticker} MACD Chart'><br>"
            html_content += "</div>"

        if stock_item.get('error'):
             html_content += f"<p class='error'>Error processing this stock: {stock_item['error']}</p>"

        html_content += "</div>" # End stock-container

    html_content += """
        </div> <!-- End report-container -->
        <div class='footer'>
            <p>Disclaimer: Data sourced from Yahoo Finance. For informational purposes only. Not financial advice.</p>
        </div>
    </body>
    </html>
    """
    try:
        with open(report_filepath, 'w') as f:
            f.write(html_content)
        print(f"Report generated: {report_filepath}")
    except Exception as e:
        print(f"Error writing HTML report: {e}")


def read_tickers_from_csv(csv_filepath: str = "stocks_list.csv"):
    """Reads a list of tickers from a CSV file. Expects a column named 'Ticker'."""
    try:
        df = pd.read_csv(csv_filepath)
        if 'Ticker' not in df.columns:
            print(f"Error: CSV file '{csv_filepath}' must contain a 'Ticker' column.")
            return []
        return df['Ticker'].dropna().unique().tolist()
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_filepath}' not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file '{csv_filepath}': {e}")
        return []

def main():
    tickers = read_tickers_from_csv()
    if not tickers:
        print("No tickers to process. Exiting.")
        return

    all_stocks_data = []
    data_period = "1y" # Fetch 1 year of data for indicators

    for ticker_symbol in tickers:
        print(f"\nProcessing {ticker_symbol}...")
        stock_data_item = {'ticker': ticker_symbol, 'info': None, 'historical_data': None, 'chart_paths': {}, 'error': None}

        is_index_ticker = ticker_symbol.startswith('^')

        # Fetch data
        stock_info = get_stock_info(ticker_symbol)
        stock_data_item['info'] = stock_info

        historical_data = get_stock_data(ticker_symbol, period=data_period)
        if historical_data is None:
            stock_data_item['error'] = f"Could not fetch historical data for {ticker_symbol}."
            all_stocks_data.append(stock_data_item)
            continue

        stock_data_item['historical_data'] = historical_data

        # Calculate technical indicators
        historical_data['SMA_50'] = calculate_sma(historical_data, window=50)
        historical_data['SMA_200'] = calculate_sma(historical_data, window=200)
        historical_data['RSI_14'] = calculate_rsi(historical_data, window=14)
        macd_line, signal_line, hist = calculate_macd(historical_data)
        historical_data['MACD'] = macd_line
        historical_data['Signal'] = signal_line
        historical_data['MACD_Hist'] = hist
        bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(historical_data)
        historical_data['BB_Middle'] = bb_middle
        historical_data['BB_Upper'] = bb_upper
        historical_data['BB_Lower'] = bb_lower

        # Generate charts
        stock_data_item['chart_paths']['price'] = generate_stock_chart(historical_data, ticker_symbol, "price")
        if not is_index_ticker : # Volume chart only for stocks, not indices
             stock_data_item['chart_paths']['volume'] = generate_stock_chart(historical_data, ticker_symbol, "volume")
        stock_data_item['chart_paths']['rsi'] = generate_stock_chart(historical_data, ticker_symbol, "rsi")
        stock_data_item['chart_paths']['macd'] = generate_stock_chart(historical_data, ticker_symbol, "macd")

        stock_data_item['is_index'] = is_index_ticker
        all_stocks_data.append(stock_data_item)

    generate_html_report(all_stocks_data)
    print("\nReport generation process complete.")


if __name__ == '__main__':
    # Example Usage (Commented out specific examples as main() will run)
    # sample_indian_ticker = "RELIANCE.NS"
    # sample_index_ticker = "^NSEI"
    #
    # print(f"--- Fetching Historical Data for {sample_indian_ticker} ---")
    # historical_data = get_stock_data(sample_indian_ticker, period="1y") # Changed to 1y
    # if historical_data is not None:
    #     print(historical_data.head())
    #     print(f"\n--- Fetching Company Info for {sample_indian_ticker} ---")
    #     company_info = get_stock_info(sample_indian_ticker)
    #     if company_info:
    #         # ... (print statements from before) ...
    #         pass

    # print(f"\n--- Fetching Historical Data for Index {sample_index_ticker} ---")
    # index_data = get_stock_data(sample_index_ticker, period="1mo")
    # if index_data is not None:
    #     print(index_data.head())
    #
    # print(f"\n--- Fetching Info for Index {sample_index_ticker} ---")
    # index_info = get_stock_info(sample_index_ticker)
    # if index_info:
    #     # ... (print statements from before) ...
    #     pass
    #
    # invalid_ticker = "NONEXISTENTTICKER.NS"
    # # ... (invalid ticker tests from before) ...
    #
    # less_common_ticker = "INFY.NS"
    # # ... (less common ticker tests from before) ...


    # print("\n--- Testing Technical Indicators ---")
    # if historical_data is not None:
    #     # ... (technical indicator calculations from before, ensure data period is sufficient) ...
    #     # For example, if historical_data was fetched for "1mo", SMA_50/200 will be mostly NaN.
    #     # Need to fetch "1y" or more for those.
    #
    #     # SMA
    #     historical_data['SMA_50'] = calculate_sma(historical_data, window=50)
    #     historical_data['SMA_200'] = calculate_sma(historical_data, window=200)
    #     print("\nSMA 50 & 200 (last 5 rows):")
    #     # Check if columns exist before printing, as they might be all NaN if data is short
    #     if 'SMA_50' in historical_data.columns : print(historical_data[['Close', 'SMA_50', 'SMA_200']].tail())
    #
    #     # RSI
    #     historical_data['RSI_14'] = calculate_rsi(historical_data, window=14)
    #     print("\nRSI 14 (last 5 rows):")
    #     if 'RSI_14' in historical_data.columns: print(historical_data[['Close', 'RSI_14']].tail())
    #
    #     # MACD
    #     macd_line, signal_line, hist = calculate_macd(historical_data)
    #     historical_data['MACD'] = macd_line
    #     historical_data['Signal'] = signal_line
    #     historical_data['MACD_Hist'] = hist
    #     print("\nMACD, Signal, Hist (last 5 rows):")
    #     if 'MACD' in historical_data.columns: print(historical_data[['Close', 'MACD', 'Signal', 'MACD_Hist']].tail())
    #
    #     # Bollinger Bands
    #     bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(historical_data)
    #     historical_data['BB_Middle'] = bb_middle
    #     historical_data['BB_Upper'] = bb_upper
    #     historical_data['BB_Lower'] = bb_lower
    #     print("\nBollinger Bands (last 5 rows):")
    #     if 'BB_Middle' in historical_data.columns: print(historical_data[['Close', 'BB_Middle', 'BB_Upper', 'BB_Lower']].tail())


    # print("\nData fetching and initial indicator test script complete. Review output for success/failures.")
    main()
