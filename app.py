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

    # 5. Display Charts (using Matplotlib figures directly with st.pyplot)
    # For Streamlit, we will regenerate charts to display them directly instead of linking to files.
    st.markdown("#### Charts")

    if historical_data_display is not None:
        # Price Chart
        fig_price = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "price") # This saves the file
        if fig_price: st.image(fig_price) # Display the saved file

        # Volume Chart (if not an index)
        if not ticker_symbol.startswith('^'):
            fig_vol = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "volume")
            if fig_vol: st.image(fig_vol)

        # RSI Chart
        fig_rsi = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "rsi")
        if fig_rsi: st.image(fig_rsi)

        # MACD Chart
        fig_macd = report_generator.generate_stock_chart(historical_data_display, ticker_symbol, "macd")
        if fig_macd: st.image(fig_macd)
    else:
        st.warning("Could not generate charts due to missing display data.")


# Main App UI
st.set_page_config(layout="wide", page_title="Stock Analysis Tool")
st.title("📈 Stock Analysis Tool")

st.sidebar.header("Single Ticker Analysis")
ticker_input = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, AAPL)", "RELIANCE.NS")
analyze_button = st.sidebar.button("Analyze Ticker")

st.sidebar.header("Full Report Generation")
report_button = st.sidebar.button("Generate Full Report (for stocks_list.csv)")

if analyze_button and ticker_input:
    with st.spinner(f"Fetching and analyzing {ticker_input}..."):
        display_stock_analysis(ticker_input)
elif 'analysis_done' in st.session_state and st.session_state.analysis_done:
    # Keep displaying last analysis if no new button is pressed
    # This part might need refinement based on desired UX for re-runs or clearing
    pass


if report_button:
    st.sidebar.info("Generating full report... This may take a few moments.")
    try:
        # Using subprocess to call the report_generator.py script
        # This ensures it runs in its own context and generates the HTML file as designed
        process = subprocess.run(['python', 'report_generator.py'], capture_output=True, text=True, check=True)
        st.sidebar.success(f"Full report 'stock_report.html' generated successfully!")
        st.sidebar.markdown(f"[Open Full Report](stock_report.html)", unsafe_allow_html=True) # Provides a link
        # st.sidebar.code(process.stdout) # Optionally display script output
        if process.stderr:
            st.sidebar.warning("Report generation script ran with some warnings/errors:")
            st.sidebar.code(process.stderr)

    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Error generating full report:")
        st.sidebar.code(e.stdout)
        st.sidebar.code(e.stderr)
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred: {e}")

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
