import streamlit as st
import pandas as pd
import report_generator # Assuming report_generator.py is in the same directory
import technical_indicators # Assuming technical_indicators.py is in the same directory
import os
import subprocess

# Ensure charts directory exists (Streamlit might run from a different context)
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

def display_stock_analysis(ticker_symbol):
    """
    Fetches, analyzes, and displays data for a single stock ticker.
    """
    st.subheader(f"Analysis for: {ticker_symbol}")

    # 1. Fetch Data
    stock_info = report_generator.get_stock_info(ticker_symbol)
    historical_data_full = report_generator.get_stock_data(ticker_symbol, period="1y") # For indicators

    if stock_info is None:
        st.error(f"Could not retrieve information for {ticker_symbol}. Please check the ticker symbol.")
        return

    if historical_data_full is None:
        st.error(f"Could not retrieve historical data for {ticker_symbol}.")
        return

    # Make a copy for display purposes if we only want to show a shorter period for the main price chart
    historical_data_display = report_generator.get_stock_data(ticker_symbol, period="6mo") # For display

    # 2. Calculate Technical Indicators (on full data)
    historical_data_full['SMA_50'] = technical_indicators.calculate_sma(historical_data_full, window=50)
    historical_data_full['SMA_200'] = technical_indicators.calculate_sma(historical_data_full, window=200)
    historical_data_full['RSI_14'] = technical_indicators.calculate_rsi(historical_data_full, window=14)
    macd_line, signal_line, hist = technical_indicators.calculate_macd(historical_data_full)
    historical_data_full['MACD'] = macd_line
    historical_data_full['Signal'] = signal_line
    historical_data_full['MACD_Hist'] = hist
    bb_middle, bb_upper, bb_lower = technical_indicators.calculate_bollinger_bands(historical_data_full)
    historical_data_full['BB_Middle'] = bb_middle
    historical_data_full['BB_Upper'] = bb_upper
    historical_data_full['BB_Lower'] = bb_lower

    # Sync relevant calculated indicators to the display dataframe (match indices)
    if historical_data_display is not None:
        for col in ['SMA_50', 'SMA_200', 'RSI_14', 'MACD', 'Signal', 'MACD_Hist', 'BB_Middle', 'BB_Upper', 'BB_Lower']:
            if col in historical_data_full.columns:
                 historical_data_display[col] = historical_data_full[col].reindex(historical_data_display.index)


    # 3. Display Key Metrics
    st.markdown("#### Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Current Price", value=report_generator.format_value(stock_info.get('regularMarketPrice')))
        st.metric(label="Market Cap", value=report_generator.format_value(stock_info.get('marketCap'), 'integer'))
        st.metric(label="P/E Ratio (TTM)", value=report_generator.format_value(stock_info.get('trailingPE')))
        st.metric(label="EPS (TTM)", value=report_generator.format_value(stock_info.get('trailingEps')))
    with col2:
        st.metric(label="Day's Change", value=f"{report_generator.format_value(stock_info.get('regularMarketChange'))} ({report_generator.format_value(stock_info.get('regularMarketChangePercent'), 'percentage')})")
        st.metric(label="52-Week High", value=report_generator.format_value(stock_info.get('fiftyTwoWeekHigh')))
        st.metric(label="52-Week Low", value=report_generator.format_value(stock_info.get('fiftyTwoWeekLow')))
        st.metric(label="Dividend Yield", value=report_generator.format_value(stock_info.get('dividendYield'), 'percentage'))

    st.text(f"Sector: {stock_info.get('sector', 'N/A')}, Industry: {stock_info.get('industry', 'N/A')}")

    # 4. Display Quick Inferences
    st.markdown("#### Quick Inferences")
    rsi_latest = historical_data_full['RSI_14'].iloc[-1] if 'RSI_14' in historical_data_full.columns and not historical_data_full['RSI_14'].empty and not pd.isna(historical_data_full['RSI_14'].iloc[-1]) else None
    rsi_inference = "N/A"
    if rsi_latest is not None:
        if rsi_latest > 70: rsi_inference = f"<span style='color: #e74c3c;'>Overbought ({report_generator.format_value(rsi_latest)})</span>"
        elif rsi_latest < 30: rsi_inference = f"<span style='color: #2ecc71;'>Oversold ({report_generator.format_value(rsi_latest)})</span>"
        else: rsi_inference = f"Neutral ({report_generator.format_value(rsi_latest)})"
    st.markdown(f"**RSI (14) Status:** {rsi_inference}", unsafe_allow_html=True)

    close_price = stock_info.get('regularMarketPrice')
    sma50_latest = historical_data_full['SMA_50'].iloc[-1] if 'SMA_50' in historical_data_full.columns and not historical_data_full['SMA_50'].empty and not pd.isna(historical_data_full['SMA_50'].iloc[-1]) else None
    sma_status = "N/A"
    if close_price is not None and sma50_latest is not None:
        if close_price > sma50_latest: sma_status = f"<span style='color: #2ecc71;'>Price above 50-Day SMA</span> (Price: {report_generator.format_value(close_price)}, SMA50: {report_generator.format_value(sma50_latest)}) - Potential Uptrend"
        elif close_price < sma50_latest: sma_status = f"<span style='color: #e74c3c;'>Price below 50-Day SMA</span> (Price: {report_generator.format_value(close_price)}, SMA50: {report_generator.format_value(sma50_latest)}) - Potential Downtrend"
        else: sma_status = f"Price near 50-Day SMA (Price: {report_generator.format_value(close_price)}, SMA50: {report_generator.format_value(sma50_latest)})"
    st.markdown(f"**Price vs SMA50:** {sma_status}", unsafe_allow_html=True)

    pe_ratio = stock_info.get('trailingPE')
    pe_inference = "N/A"
    if pe_ratio is not None and not pd.isna(pe_ratio):
        if pe_ratio > 30: pe_inference = f"High P/E ({report_generator.format_value(pe_ratio)}) - Potentially Overvalued or High Growth Expected"
        elif pe_ratio > 0 and pe_ratio < 15: pe_inference = f"Low P/E ({report_generator.format_value(pe_ratio)}) - Potentially Undervalued or Lower Growth Expected"
        elif pe_ratio <= 0: pe_inference = f"Negative/Zero P/E ({report_generator.format_value(pe_ratio)}) - Company may be loss-making"
        else: pe_inference = f"Moderate P/E ({report_generator.format_value(pe_ratio)})"
    st.markdown(f"**P/E Ratio Status:** {pe_inference}", unsafe_allow_html=True)

    # Display Buy/Sell/Hold Signal
    if not ticker_symbol.startswith('^') and stock_info: # Signals are for stocks with valid info
        signal, reasons = report_generator.get_buy_sell_hold_signal(historical_data_full, stock_info)
        signal_color = "orange" # Default for Hold or N/A
        if "Buy" in signal and "Cautiously" not in signal: signal_color = "green"
        elif "Sell" in signal and "Cautiously" not in signal: signal_color = "red"

        st.markdown(f"--- \n#### Algorithmic Signal: <span style='color:{signal_color}; font-weight:bold;'>{signal}</span>", unsafe_allow_html=True)

        if reasons:
            st.markdown("Key Observations:")
            reason_html = "<ul>"
            for reason in reasons:
                reason_html += f"<li>{reason}</li>"
            reason_html += "</ul>"
            st.markdown(reason_html, unsafe_allow_html=True)
    elif not stock_info and not ticker_symbol.startswith('^'):
        st.markdown("--- \n#### Algorithmic Signal: <span style='color:orange; font-weight:bold;'>N/A</span>", unsafe_allow_html=True)
        st.markdown("Reasons:<ul><li>Stock information could not be retrieved.</li></ul>", unsafe_allow_html=True)


    # 5. Display Charts (using Matplotlib figures directly with st.pyplot)
    st.markdown("--- \n#### Current Charts")
    if historical_data_display is not None:
        # Price Chart
        fig_price_path = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "price")
        if fig_price_path: st.image(fig_price_path)

        if not ticker_symbol.startswith('^'):
            fig_vol_path = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "volume")
            if fig_vol_path: st.image(fig_vol_path)

        fig_rsi_path = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "rsi")
        if fig_rsi_path: st.image(fig_rsi_path)

        fig_macd_path = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "macd")
        if fig_macd_path: st.image(fig_macd_path)
    else:
        st.warning("Could not generate current charts due to missing display data.")


def display_historical_stock_analysis(ticker_symbol, analysis_date):
    st.subheader(f"Historical Analysis for: {ticker_symbol} as of {analysis_date.strftime('%Y-%m-%d')}")

    # 1. Fetch historical data up to the analysis_date
    # yfinance period parameter might need adjustment if '1y' is too short for older dates.
    # For simplicity, we fetch a fixed longer period and then slice.
    # Add one day to analysis_date for yfinance end date to include the analysis_date itself.
    end_date_for_fetch = analysis_date + pd.Timedelta(days=1)
    historical_data_all = report_generator.get_stock_data(ticker_symbol, period="5y", interval="1d") # Fetch up to 5 years

    if historical_data_all is None or historical_data_all.empty:
        st.error(f"Could not retrieve sufficient historical data for {ticker_symbol} to analyze as of {analysis_date.strftime('%Y-%m-%d')}.")
        return

    # Filter data up to the selected analysis_date
    historical_data_截至日 = historical_data_all[historical_data_all.index <= pd.to_datetime(end_date_for_fetch)]

    if historical_data_截至日.empty:
        st.error(f"No historical data available for {ticker_symbol} on or before {analysis_date.strftime('%Y-%m-%d')}.")
        return

    # Get the actual latest available date from the filtered data (could be before analysis_date if market was closed)
    actual_analysis_date = historical_data_截至日.index.max()
    st.info(f"Displaying data as of the closest available market day: {actual_analysis_date.strftime('%Y-%m-%d')}")

    # 2. Calculate Technical Indicators based on data up to actual_analysis_date
    historical_data_截至日['SMA_50'] = technical_indicators.calculate_sma(historical_data_截至日, window=50)
    historical_data_截至日['SMA_200'] = technical_indicators.calculate_sma(historical_data_截至日, window=200)
    historical_data_截至日['RSI_14'] = technical_indicators.calculate_rsi(historical_data_截至日, window=14)
    macd_line, signal_line, hist = technical_indicators.calculate_macd(historical_data_截至日)
    historical_data_截至日['MACD'] = macd_line
    historical_data_截至日['Signal'] = signal_line
    historical_data_截至日['MACD_Hist'] = hist
    # Note: Bollinger Bands might not be as relevant for a single historical point without chart context.

    # 3. Display Metrics as of actual_analysis_date
    st.markdown(f"#### Metrics as of {actual_analysis_date.strftime('%Y-%m-%d')}")

    latest_close = historical_data_截至日['Close'].iloc[-1] if not historical_data_截至日.empty else 'N/A'
    sma50_val = historical_data_截至日['SMA_50'].iloc[-1] if 'SMA_50' in historical_data_截至日.columns and not historical_data_截至日['SMA_50'].empty and not pd.isna(historical_data_截至日['SMA_50'].iloc[-1]) else 'N/A'
    sma200_val = historical_data_截至日['SMA_200'].iloc[-1] if 'SMA_200' in historical_data_截至日.columns and not historical_data_截至日['SMA_200'].empty and not pd.isna(historical_data_截至日['SMA_200'].iloc[-1]) else 'N/A'
    rsi14_val = historical_data_截至日['RSI_14'].iloc[-1] if 'RSI_14' in historical_data_截至日.columns and not historical_data_截至日['RSI_14'].empty and not pd.isna(historical_data_截至日['RSI_14'].iloc[-1]) else 'N/A'
    macd_val = historical_data_截至日['MACD'].iloc[-1] if 'MACD' in historical_data_截至日.columns and not historical_data_截至日['MACD'].empty and not pd.isna(historical_data_截至日['MACD'].iloc[-1]) else 'N/A'
    signal_val = historical_data_截至日['Signal'].iloc[-1] if 'Signal' in historical_data_截至日.columns and not historical_data_截至日['Signal'].empty and not pd.isna(historical_data_截至日['Signal'].iloc[-1]) else 'N/A'

    metrics_data = {
        "Closing Price": report_generator.format_value(latest_close),
        "50-Day SMA": report_generator.format_value(sma50_val),
        "200-Day SMA": report_generator.format_value(sma200_val),
        "RSI (14)": report_generator.format_value(rsi14_val),
        "MACD": report_generator.format_value(macd_val),
        "Signal Line": report_generator.format_value(signal_val)
    }
    st.table(pd.DataFrame(metrics_data.items(), columns=["Indicator", "Value"]))

    # Optionally, display a small chart of the historical period if desired
    # For now, focusing on point-in-time data as requested.


# Main App UI
st.set_page_config(layout="wide", page_title="Stock Analysis Tool")
st.title("📈 Stock Analysis Tool")

st.sidebar.header("Single Ticker Analysis")
ticker_input = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, AAPL)", "RELIANCE.NS")

# Date input for historical analysis
st.sidebar.subheader("Historical View")
# Max date is yesterday to ensure data is typically available. Min date can be set further back.
yesterday = pd.Timestamp('today').normalize() - pd.Timedelta(days=1)
historical_date_input = st.sidebar.date_input("Select Historical Date", value=yesterday, max_value=yesterday, help="View indicators as of this date.")

analyze_button = st.sidebar.button("Analyze Ticker (Current & Historical)")


st.sidebar.header("Full Report Generation")
report_button = st.sidebar.button("Generate Full Report (for stocks_list.csv)")

if analyze_button and ticker_input:
    with st.spinner(f"Fetching and analyzing {ticker_input} for current data..."):
        display_stock_analysis(ticker_input)

    if historical_date_input:
        with st.spinner(f"Fetching and analyzing {ticker_input} for historical date {historical_date_input.strftime('%Y-%m-%d')}..."):
            display_historical_stock_analysis(ticker_input, historical_date_input)
    st.session_state.analysis_done = True


if report_button:
    st.sidebar.info("Generating full report... This may take a few moments.")
    try:
        # Using subprocess to call the report_generator.py script
        # This ensures it runs in its own context and generates the PDF file as designed
        process = subprocess.run(['python', 'report_generator.py'], capture_output=True, text=True, check=True)

        pdf_file_path = "stock_report.pdf" # Expected output filename from report_generator.py
        if os.path.exists(pdf_file_path):
            st.sidebar.success(f"Full PDF report '{pdf_file_path}' generated successfully!")
            with open(pdf_file_path, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
            st.sidebar.download_button(label="Download PDF Report",
                                data=PDFbyte,
                                file_name="stock_analysis_report.pdf",
                                mime='application/octet-stream')
        else:
            st.sidebar.error("PDF report file not found after generation.")

        # Display script output if any
        if process.stdout:
             st.sidebar.text_area("Report Generation Log:", process.stdout, height=100)
        if process.stderr:
            st.sidebar.warning("Report generation script ran with some warnings/errors:")
            st.sidebar.code(process.stderr)

    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Error generating full PDF report:")
        st.sidebar.code(e.stdout)
        st.sidebar.code(e.stderr)
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred during PDF report generation: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("Data sourced from Yahoo Finance. Not financial advice.")

# Placeholder for main content area if no analysis is run yet or to show general info
if not analyze_button and not report_button :
    st.markdown("""
    Welcome to the Stock Analysis Tool!

    **How to use:**
    1.  **Single Ticker Analysis:** Enter a stock ticker in the sidebar (e.g., `INFY.NS` for Infosys India, `AAPL` for Apple Inc.) and click "Analyze Ticker".
    2.  **Full Report:** Click "Generate Full Report" to create an HTML report for all tickers listed in `stocks_list.csv`.

    The tool provides key metrics, technical indicators, basic inferences, and charts.
    """)
    # Optionally, display a default analysis or a list of available tickers from csv
    # default_tickers = report_generator.read_tickers_from_csv()
    # if default_tickers:
    #     st.markdown("Tickers in `stocks_list.csv` for full report:")
    #     st.json(default_tickers)

# To run this app: streamlit run app.py
