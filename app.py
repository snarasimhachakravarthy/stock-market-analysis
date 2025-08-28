import streamlit as st
import pandas as pd
import report_generator
import technical_indicators
import os
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.express as px
from plotly.subplots import make_subplots

# Initialize session state
if 'generate_full_report' not in st.session_state:
    st.session_state.generate_full_report = False
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# Configure the page
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .error {
        color: #ff4b4b;
    }
    .success {
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

def create_interactive_stock_chart(data, ticker_symbol):
    """Create an interactive stock chart with price, volume, and indicators"""
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=(
            f'{ticker_symbol} Price and Moving Averages',
            'Volume',
            'Technical Indicators'
        )
    )

    # Price and Moving Averages
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )
    
    # Add moving averages if they exist
    if 'SMA_50' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['SMA_50'],
                name='SMA 50',
                line=dict(color='blue', width=1.5)
            ),
            row=1, col=1
        )
    
    if 'SMA_200' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['SMA_200'],
                name='SMA 200',
                line=dict(color='orange', width=1.5)
            ),
            row=1, col=1
        )
    
    # Volume
    colors = ['green' if row['Close'] >= row['Open'] else 'red' 
              for _, row in data.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )
    
    # RSI
    if 'RSI_14' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI_14'],
                name='RSI 14',
                line=dict(color='purple', width=1.5)
            ),
            row=3, col=1
        )
        
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash='dash', line_color='red', row=3, col=1)
        fig.add_hline(y=30, line_dash='dash', line_color='green', row=3, col=1)
    
    # MACD if available
    if all(col in data.columns for col in ['MACD', 'Signal']):
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['MACD_Hist'],
                name='MACD Histogram',
                marker_color=['green' if val > 0 else 'red' for val in data['MACD_Hist']]
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD'],
                name='MACD',
                line=dict(color='blue', width=1.5)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Signal'],
                name='Signal',
                line=dict(color='orange', width=1.5)
            ),
            row=3, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=1000,
        showlegend=True,
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Update y-axes titles
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Indicator", row=3, col=1)
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def show_loading_spinner():
    """Display a loading spinner"""
    return st.spinner("Processing your request...")

# Ensure charts directory exists (Streamlit might run from a different context)
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

def display_stock_analysis(ticker_symbol):
    """
    Fetches, analyzes, and displays data for a single stock ticker with interactive charts.
    """
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        st.subheader(f"📊 Analysis for: {ticker_symbol}")
        
        # Add a refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.experimental_rerun()

        # 1. Fetch Data with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                stock_info = report_generator.get_stock_info(ticker_symbol)
                if not stock_info:
                    raise ValueError("No stock info returned")
                    
                # Get 2 years of data for better technical analysis
                historical_data_full = report_generator.get_stock_data(ticker_symbol, period="2y")
                if historical_data_full is None or historical_data_full.empty:
                    raise ValueError("No historical data returned")
                
                # If we get here, data is good
                break
                
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    st.error(f"❌ Failed to fetch data for {ticker_symbol} after {max_retries} attempts.")
                    st.error(f"Error: {str(e)}")
                    st.info("Please try again in a few minutes or check if the ticker symbol is correct.")
                    return
                
                # Wait before retrying
                time.sleep(retry_delay * (attempt + 1))
                continue

    # 2. Calculate Technical Indicators (on full data)
    with st.spinner("Calculating technical indicators..."):
        # Calculate indicators
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

    # 3. Display the interactive chart
    st.markdown("### 📈 Interactive Chart")
    st.markdown("""
        <div style="font-size: 0.9em; color: #666; margin-bottom: 1em;">
        <b>Tip:</b> Use the range selector below to zoom in/out, or hover over the chart for detailed information.
        </div>
    """, unsafe_allow_html=True)
    
    # Create and display the interactive chart
    fig = create_interactive_stock_chart(historical_data_full, ticker_symbol)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display key metrics in a clean layout
    st.markdown("### 📊 Key Metrics")
    
    if stock_info:
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", 
                     f"${stock_info.get('currentPrice', 'N/A'):.2f}",
                     delta=f"{stock_info.get('dayChangePercent', 0):.2f}%")
            st.metric("Market Cap", 
                     f"${stock_info.get('marketCap', 0)/1e9:.2f}B" if stock_info.get('marketCap') else 'N/A')
            
        with col2:
            st.metric("P/E Ratio", 
                     f"{stock_info.get('trailingPE', 'N/A')}")
            st.metric("52-Week Range", 
                     f"${stock_info.get('fiftyTwoWeekLow', 'N/A'):.2f} - ${stock_info.get('fiftyTwoWeekHigh', 'N/A'):.2f}")
            
        with col3:
            st.metric("Volume", 
                     f"{stock_info.get('volume', 0)/1e6:.2f}M" if stock_info.get('volume') else 'N/A')
            st.metric("Avg. Volume", 
                     f"{stock_info.get('averageVolume', 0)/1e6:.2f}M" if stock_info.get('averageVolume') else 'N/A')
    
    # 4. Add technical analysis insights
    st.markdown("### 🔍 Technical Analysis")
    
    # Create columns for technical analysis
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("#### 📊 Moving Averages")
        if 'SMA_50' in historical_data_full.columns and 'SMA_200' in historical_data_full.columns:
            latest_close = historical_data_full['Close'].iloc[-1]
            sma50 = historical_data_full['SMA_50'].iloc[-1]
            sma200 = historical_data_full['SMA_200'].iloc[-1]
            
            st.metric("50-Day SMA", f"${sma50:.2f}", 
                     delta=f"{(sma50 - historical_data_full['SMA_50'].iloc[-2]):.2f}")
            st.metric("200-Day SMA", f"${sma200:.2f}",
                     delta=f"{(sma200 - historical_data_full['SMA_200'].iloc[-2]):.2f}")
            
            # Golden/Death Cross detection
            if pd.notna(sma50) and pd.notna(sma200):
                if sma50 > sma200 and historical_data_full['SMA_50'].iloc[-2] <= historical_data_full['SMA_200'].iloc[-2]:
                    st.success("💰 Golden Cross Detected (50-day crossed above 200-day)")
                elif sma50 < sma200 and historical_data_full['SMA_50'].iloc[-2] >= historical_data_full['SMA_200'].iloc[-2]:
                    st.error("💀 Death Cross Detected (50-day crossed below 200-day)")
    
    with tech_col2:
        st.markdown("#### 📈 Momentum Indicators")
        if 'RSI_14' in historical_data_full.columns:
            rsi = historical_data_full['RSI_14'].iloc[-1]
            rsi_color = "red" if rsi > 70 else "green" if rsi < 30 else "orange"
            st.markdown(f"**RSI (14):** <span style='color: {rsi_color}'>{rsi:.2f}</span>", 
                       unsafe_allow_html=True)
            
            if rsi > 70:
                st.warning("⚠️ Overbought: Consider taking profits or waiting for a pullback.")
            elif rsi < 30:
                st.info("ℹ️ Oversold: Potential buying opportunity, but confirm with other indicators.")
        
        if 'MACD' in historical_data_full.columns and 'Signal' in historical_data_full.columns:
            macd = historical_data_full['MACD'].iloc[-1]
            signal = historical_data_full['Signal'].iloc[-1]
            macd_hist = historical_data_full['MACD_Hist'].iloc[-1]
            
            st.markdown(f"**MACD:** {macd:.2f}")
            st.markdown(f"**Signal:** {signal:.2f}")
            st.markdown(f"**Histogram:** {macd_hist:.2f}")
            
            if macd > signal and historical_data_full['MACD'].iloc[-2] <= historical_data_full['Signal'].iloc[-2]:
                st.success("🟢 Bullish MACD Crossover")
            elif macd < signal and historical_data_full['MACD'].iloc[-2] >= historical_data_full['Signal'].iloc[-2]:
                st.error("🔴 Bearish MACD Crossover")
    # 5. Add company information and additional details
    if stock_info:
        st.markdown("### ℹ️ Company Information")
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown(f"**Company:** {stock_info.get('longName', ticker_symbol)}")
            st.markdown(f"**Sector:** {stock_info.get('sector', 'N/A')}")
            st.markdown(f"**Industry:** {stock_info.get('industry', 'N/A')}")
            
        with info_col2:
            st.markdown(f"**Exchange:** {stock_info.get('exchange', 'N/A')}")
            st.markdown(f"**Currency:** {stock_info.get('currency', 'USD')}")
            if 'website' in stock_info:
                st.markdown(f"**Website:** [{stock_info['website']}]({stock_info['website']})")
    
    # 6. Add a link to more detailed analysis
    st.markdown("---")
    st.markdown("""
    ### 📊 Want More Analysis?
    - Generate a detailed PDF report using the sidebar
    - Try different timeframes using the range selector on the chart
    - Hover over data points for detailed information
    - Use the toolbar in the top-right corner of the chart to zoom, pan, or download the chart
    """)
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
    print(f"\n=== Starting Historical Analysis for {ticker_symbol} as of {analysis_date.strftime('%Y-%m-%d')} ===")
    
    # Convert analysis_date to pandas Timestamp if it's not already
    if not isinstance(analysis_date, pd.Timestamp):
        analysis_date = pd.to_datetime(analysis_date)
    
    # Calculate the start date (2 years before analysis date)
    start_date = (analysis_date - pd.DateOffset(years=2)).strftime('%Y-%m-%d')
    end_date = (analysis_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')  # Include analysis date
    
    print(f"Fetching data from {start_date} to {end_date}")
    
    # Fetch data with the calculated date range
    historical_data_all = report_generator.get_stock_data(
        ticker_symbol, 
        start=start_date,
        end=end_date,
        interval="1d"
    )
    
    if historical_data_all is None or historical_data_all.empty:
        error_msg = f"❌ Could not retrieve any historical data for {ticker_symbol}."
        print(error_msg)
        st.error(error_msg)
        return
        
    print(f"Retrieved {len(historical_data_all)} data points from {historical_data_all.index[0].date()} to {historical_data_all.index[-1].date()}")
    
    # Ensure we have a valid datetime index and handle timezones
    historical_data_all.index = pd.to_datetime(historical_data_all.index).tz_localize(None)
    
    # Filter data up to the selected analysis_date
    analysis_date_naive = pd.Timestamp(analysis_date).tz_localize(None)
    historical_data_filtered = historical_data_all[historical_data_all.index <= analysis_date_naive]
    
    if historical_data_filtered.empty:
        error_msg = f"❌ No data available for {ticker_symbol} on or before {analysis_date.strftime('%Y-%m-%d')}."
        print(error_msg)
        st.error(error_msg)
        return
        
    # Get the actual latest available date from the filtered data (could be before analysis_date if market was closed)
    actual_analysis_date = historical_data_filtered.index.max()
    print(f"Using closest market date: {actual_analysis_date.strftime('%Y-%m-%d')}")
    st.info(f"Displaying data as of the closest available market day: {actual_analysis_date.strftime('%Y-%m-%d')}")
    
    # Ensure we have enough data for calculations (at least 200 days for SMA200)
    if len(historical_data_filtered) < 200:
        st.warning(f"Limited historical data available ({len(historical_data_filtered)} days). Some indicators may be less reliable.")
        
    # Use the filtered data for analysis
    analysis_data = historical_data_filtered.copy()

    # 2. Calculate Technical Indicators based on data up to actual_analysis_date
    print("Calculating technical indicators...")
    
    # Make a copy to avoid SettingWithCopyWarning
    analysis_data = historical_data_filtered.copy()
    
    # Calculate indicators with error handling
    try:
        analysis_data['SMA_50'] = technical_indicators.calculate_sma(analysis_data, window=50)
        analysis_data['SMA_200'] = technical_indicators.calculate_sma(analysis_data, window=200)
        analysis_data['RSI_14'] = technical_indicators.calculate_rsi(analysis_data, window=14)
        
        macd_line, signal_line, hist = technical_indicators.calculate_macd(analysis_data)
        if macd_line is not None and signal_line is not None and hist is not None:
            analysis_data['MACD'] = macd_line
            analysis_data['Signal'] = signal_line
            analysis_data['MACD_Hist'] = hist
        else:
            print("Warning: MACD calculation returned None values")
            
    except Exception as e:
        print(f"Error calculating indicators: {str(e)}")
        st.error(f"Error calculating technical indicators: {str(e)}")
        return

    # Get the latest available values
    latest_data = analysis_data.iloc[-1] if not analysis_data.empty else None
    
    if latest_data is None:
        st.error("No data available for the selected date range.")
        return
        
    # 3. Display Metrics as of actual_analysis_date
    st.markdown(f"#### Metrics as of {actual_analysis_date.strftime('%Y-%m-%d')}")
    
    # Helper function to safely get values
    def get_indicator_value(col_name):
        if col_name not in analysis_data.columns or analysis_data[col_name].isna().all():
            return 'N/A'
        return analysis_data[col_name].iloc[-1] if not pd.isna(analysis_data[col_name].iloc[-1]) else 'N/A'
    
    latest_close = get_indicator_value('Close')
    sma50_val = get_indicator_value('SMA_50')
    sma200_val = get_indicator_value('SMA_200')
    rsi14_val = get_indicator_value('RSI_14')
    macd_val = get_indicator_value('MACD')
    signal_val = get_indicator_value('Signal')

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
st.set_page_config(
    layout="wide", 
    page_title="Stock Analysis Tool",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        padding: 0.5rem;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2c3e50;
    }
    .stMarkdown {
        color: #34495e;
    }
    .stAlert {
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main title with description
st.title("📈 Stock Analysis Dashboard")
st.markdown("""
    <div style='margin-bottom: 2rem; color: #7f8c8d;'>
        Analyze stocks with interactive charts, technical indicators, and fundamental metrics.
        Get insights to make informed investment decisions.
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔍 Stock Analysis")
    
    # Ticker input with example
    ticker_input = st.text_input(
        "Enter Stock Ticker",
        value="RELIANCE.NS",
        help="E.g., RELIANCE.NS, TATAMOTORS.NS, AAPL, MSFT"
    )
    
    # Add a sample tickers section
    st.markdown("### 📋 Sample Tickers")
    sample_col1, sample_col2 = st.columns(2)
    
    with sample_col1:
        if st.button("NIFTY 50"):
            ticker_input = "^NSEI"
        if st.button("RELIANCE"):
            ticker_input = "RELIANCE.NS"
        if st.button("TATA MOTORS"):
            ticker_input = "TATAMOTORS.NS"
            
    with sample_col2:
        if st.button("AAPL"):
            ticker_input = "AAPL"
        if st.button("MSFT"):
            ticker_input = "MSFT"
        if st.button("GOOGL"):
            ticker_input = "GOOGL"
    
    # Date input for historical analysis
    st.markdown("### ⏳ Historical View")
    yesterday = pd.Timestamp('today').normalize() - pd.Timedelta(days=1)
    historical_date_input = st.date_input(
        "Select Historical Date", 
        value=yesterday, 
        max_value=yesterday, 
        help="View indicators as of this date"
    )
    
    # Add some space
    st.markdown("---")
    
    # Add a section for report generation
    st.markdown("### 📄 Generate Report")
    if st.button("📊 Generate PDF Report"):
        with st.spinner("Generating report..."):
            try:
                report_path = report_generator.generate_report([ticker_input], "stock_report.pdf")
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=f,
                        file_name=f"{ticker_input}_report.pdf",
                        mime="application/pdf"
                    )
                st.success("Report generated successfully!")
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    # Add a link to the GitHub repo
    st.markdown("---")
    st.markdown("""
    ### 📚 Resources
    - [Documentation](#)
    - [GitHub Repository](#)
    - [Report an Issue](#)
    
    Made with ❤️ using [Streamlit](https://streamlit.io/)
    """)

# Initialize session state for tracking analysis
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# Main content area
tab1, tab2 = st.tabs(["📊 Current Analysis", "📅 Historical View"])

with tab1:
    if ticker_input:
        with st.spinner(f"Analyzing {ticker_input}..."):
            try:
                display_stock_analysis(ticker_input)
                st.session_state.analysis_done = True
            except Exception as e:
                st.error(f"Error analyzing {ticker_input}: {str(e)}")
                st.exception(e)  # Show full traceback for debugging
    else:
        st.info("👈 Enter a stock ticker in the sidebar to get started")

with tab2:
    if ticker_input:
        with st.spinner(f"Fetching historical data for {ticker_input} as of {historical_date_input}..."):
            try:
                display_historical_stock_analysis(ticker_input, historical_date_input)
            except Exception as e:
                st.error(f"Error fetching historical data: {str(e)}")
    else:
        st.info("👈 Enter a stock ticker and select a date to view historical analysis")

# Add full report button in the sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("📄 Generate Full Report (stocks_list.csv)"):
        st.session_state.generate_full_report = True

# Handle full report generation
if st.session_state.get('generate_full_report', False):
    with st.spinner("Generating full report..."):
        if os.path.exists('stocks_list.csv'):
            try:
                df = pd.read_csv('stocks_list.csv')
                tickers = df['Ticker'].dropna().tolist()
                if tickers:
                    report_path = report_generator.generate_report(tickers, 'stock_report.pdf')
                    
                    with open(report_path, "rb") as f:
                        st.sidebar.download_button(
                            label="📥 Download Full PDF Report",
                            data=f,
                            file_name="full_stock_report.pdf",
                            mime="application/pdf"
                        )
                    st.sidebar.success("Full report generated successfully!")
                else:
                    st.sidebar.error("No valid tickers found in stocks_list.csv")
            except Exception as e:
                st.sidebar.error(f"Error generating full report: {str(e)}")
        else:
            st.sidebar.error("stocks_list.csv not found. Please create this file with your list of tickers.")
    st.session_state.generate_full_report = False

    if historical_date_input and ticker_input:
        with st.spinner(f"Fetching and analyzing {ticker_input} for historical date {historical_date_input.strftime('%Y-%m-%d')}..."):
            try:
                display_historical_stock_analysis(ticker_input, historical_date_input)
                st.session_state.analysis_done = True
            except Exception as e:
                st.error(f"Error in historical analysis: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.markdown("Data sourced from Yahoo Finance. Not financial advice.")

# Placeholder for main content area if no analysis is run yet or to show general info
if not st.session_state.get('analysis_done', False):
    st.markdown("""
    # Welcome to the Stock Analysis Tool! 📈
    
    **How to use:**
    1. Enter a stock ticker in the sidebar (e.g., RELIANCE.NS, AAPL)
    2. View interactive charts with technical indicators
    3. Switch between current and historical views
    4. Generate PDF reports from the sidebar
    
    ### Sample Tickers:
    - Indian Stocks: RELIANCE.NS, TATAMOTORS.NS, INFY.NS
    - US Stocks: AAPL, MSFT, GOOGL
    - Indices: ^NSEI (Nifty 50), ^BSESN (Sensex), ^GSPC (S&P 500)
    """)
    #     st.markdown("Tickers in `stocks_list.csv` for full report:")
    #     st.json(default_tickers)

# To run this app: streamlit run app.py
