# Stock Market Analysis Report Generator

This repository contains a Python script to generate a daily HTML report for Indian stock market analysis, covering both index stocks and custom user-provided stocks. The report aims to provide insights into whether stocks are at a good valuation for investment based on common technical and fundamental metrics.

## Features

*   Fetches latest stock data from Yahoo Finance.
*   Calculates common technical indicators:
    *   Simple Moving Averages (SMA - 50 & 200 day)
    *   Relative Strength Index (RSI - 14 day)
    *   Moving Average Convergence Divergence (MACD - 12, 26, 9 day)
    *   Bollinger Bands (20 day)
*   Extracts key fundamental ratios:
    *   Price-to-Earnings (P/E) Ratio
    *   Earnings Per Share (EPS)
    *   Price-to-Book (P/B) Ratio
    *   Debt-to-Equity (D/E) Ratio (Note: Currently 'N/A' as it requires deeper balance sheet parsing not yet implemented)
    *   Dividend Yield
    *   Price/Earnings to Growth (PEG) Ratio
*   Generates basic textual inferences based on RSI and Price vs SMA50.
*   **Generates Buy/Sell/Hold signals** with reasoning based on a combination of SMA, RSI, and MACD indicators.
*   Produces a **PDF report** (downloadable via UI) with:
    *   Key metrics tables for each stock/index.
    *   Signal and reasoning for each stock.
    *   Concise set of charts in PDF: Price chart (with SMAs & Bollinger Bands) and RSI chart.
*   **Interactive Local UI (Streamlit):**
    *   Analyze individual tickers (Indian or US) on demand.
    *   View current metrics, all charts (Price, Volume, RSI, MACD), inferences, and signals.
    *   **Historical View:** Select a past date to see key technical indicators (Close, SMA50, SMA200, RSI, MACD) as of that date.
    *   Trigger full PDF report generation for stocks in `stocks_list.csv`.
*   Modern and clean visual styling for both UI and PDF report.
*   Customizable list of stocks/indices via `stocks_list.csv` for the PDF report. The tool supports both Indian (e.g., `.NS`, `.BO` suffixes) and US (no suffix) stock tickers.
*   Includes a `setup.sh` script for easy environment setup.

## Prerequisites

*   Python 3.6+
*   pip (Python package installer)
*   `venv` module for Python (usually included with Python 3)

## Setup and Usage

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Run the Setup Script:**
    This script will create a virtual environment and install the necessary dependencies.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    The script will guide you. After it runs, you **must** activate the virtual environment in your current terminal session:
    ```bash
    source .venv/bin/activate
    ```
    *Note for Windows users:* You might need to use a Git Bash terminal or WSL to run the `.sh` script, or manually create the virtual environment (`python -m venv .venv`) and activate it (`.venv\Scripts\activate`), then install dependencies (`pip install -r requirements.txt`).

3.  **Running the Application (Local UI):**
    Once the setup is complete and the virtual environment is activated, you can run the local Streamlit UI:
    ```bash
    streamlit run app.py
    ```
    This will typically open the application in your default web browser.

    **Using the Local UI:**
    *   **Single Ticker Analysis:** Enter a stock ticker in the sidebar (e.g., `RELIANCE.NS` for an Indian stock, or `AAPL` for a US stock) and click "Analyze Ticker". The analysis for that ticker will appear in the main window.
    *   **Full PDF Report Generation:** Click the "Generate Full Report" button in the sidebar. This will process all tickers listed in `stocks_list.csv` and generate `stock_report.pdf`. A download button for the PDF will appear in the sidebar.

4.  **Customize Stock List for Full PDF Report (Optional):**
    Edit the `stocks_list.csv` file to include the stock tickers (e.g., `RELIANCE.NS`, `INFY.NS`, `AAPL`, `MSFT`) or index tickers (e.g., `^NSEI` for NIFTY 50, `^BSESN` for SENSEX) you want to include in the full PDF report. Each ticker should be on a new line under the "Ticker" header.

5.  **Direct PDF Report Generation (Alternative to UI):**
    If you only want to generate the PDF report without using the UI, ensure your virtual environment is activated, then run:
    ```bash
    python report_generator.py
    ```
    This will create `stock_report.pdf` in the project root.

## Supported Markets

*   **Indian Stocks:** Use standard Yahoo Finance tickers (e.g., `RELIANCE.NS`, `INFY.BO`).
*   **US Stocks:** Use standard Yahoo Finance tickers (e.g., `AAPL`, `MSFT`).
*   **Major Indices:** (e.g., `^NSEI`, `^BSESN`, `^GSPC`).

## Metrics Used

### Technical Indicators

*   **Simple Moving Average (SMA):**
    *   Periods: 50-day and 200-day.
    *   Purpose: Shows the average price over a specified period, helping to identify medium-term and long-term trends. Crossovers (e.g., 50-day crossing above 200-day - "Golden Cross") can signal momentum shifts.
*   **Relative Strength Index (RSI):**
    *   Period: 14-day.
    *   Purpose: A momentum oscillator measuring the speed and change of price movements.
    *   Interpretation: Values > 70 typically indicate overbought conditions; < 30 indicate oversold conditions.
*   **Moving Average Convergence Divergence (MACD):**
    *   Periods: Short EMA (12-day), Long EMA (26-day), Signal Line (9-day EMA of MACD).
    *   Purpose: A trend-following momentum indicator showing the relationship between two moving averages.
    *   Interpretation: MACD line crossing above signal line is often a bullish signal; crossing below is bearish.
*   **Bollinger Bands®:**
    *   Period: 20-day SMA for the middle band.
    *   Standard Deviations: 2 for upper and lower bands.
    *   Purpose: Measure market volatility. Prices are considered overbought near the upper band and oversold near the lower band.

### Fundamental Ratios

*(Primarily extracted from Yahoo Finance's summary data)*

*   **Price-to-Earnings (P/E) Ratio:** Market price per share / Earnings per share (EPS). Indicates investor expectations.
*   **Earnings Per Share (EPS):** Company's profit allocated to each share. Growth in EPS is generally positive.
*   **Price-to-Book (P/B) Ratio:** Market price per share / Book value per share. Compares market valuation to company's net asset value.
*   **Debt-to-Equity (D/E) Ratio:** Total liabilities / Shareholder equity. Measures financial leverage. *(Currently N/A in report; requires specific balance sheet parsing).*
*   **Dividend Yield:** Annual dividend per share / Stock's current price. Shows return from dividends.
*   **Price/Earnings to Growth (PEG) Ratio:** P/E ratio / Annual EPS growth rate. Balances P/E with growth expectations. *(Often N/A if growth data isn't readily available in summary).*

### Actionable Signals & Insights

*   **Buy/Sell/Hold Signal:** A signal (Buy, Sell, Hold, or nuanced Hold like "Hold (Buy Cautiously)") is generated for individual stocks based on a weighted scoring of technical indicators:
    *   SMA50 vs SMA200 (Golden/Death Cross)
    *   Current Price vs SMA50
    *   RSI Level (Oversold, Overbought, Neutral)
    *   MACD Line vs Signal Line
    *   MACD Histogram
*   **Reasoning Pointers:** Key technical observations that contributed to the signal are listed as bullet points.
*   **Availability:** This feature is available in the Streamlit UI for single-ticker analysis and in the generated PDF report.
*   **Historical View (UI):** The Streamlit UI allows selecting a historical date to view technical indicators (Close, SMA50, SMA200, RSI, MACD) as of that date. The Buy/Sell/Hold signal is based on the *latest* data, not historical.

## Future Enhancements (Potential)

*   **Interactive Charts:** Replacing current static charts in the UI with interactive ones (e.g., using Plotly).
*   More sophisticated inference engine and signal generation logic.

*   **Buy/Sell/Hold:** A signal is generated based on a combination of SMA positions, RSI levels, and MACD crossovers.
*   **Reasoning:** Key technical observations that contributed to the signal are listed as bullet points. This is available in both the UI and the PDF report for individual stocks.

## Future Enhancements (Potential)

*   **Interactive Charts:** Replacing current static charts in the UI with interactive ones (e.g., using Plotly).
*   More sophisticated inference engine and signal generation logic.
*   Interactive charts (e.g., using Plotly or Bokeh).
*   Allowing users to customize indicator parameters.
*   Detailed industry/sector comparison for P/E ratios.
*   Calculation of D/E ratio from balance sheet data.
*   Portfolio analysis features.

## Disclaimer

This tool is for informational and educational purposes only. The data is sourced from Yahoo Finance and may have inaccuracies or delays. The generated report does **not** constitute financial advice. Always do your own research or consult with a qualified financial advisor before making investment decisions.
