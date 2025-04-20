# SENSEX Market Analysis System

An automated system for analyzing SENSEX market data using technical indicators and generating daily reports.

## Features

- Fetches historical SENSEX data from Yahoo Finance
- Calculates multiple technical indicators:
  - Simple Moving Averages (50-day and 200-day)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Bollinger Bands
- Generates daily market analysis reports with:
  - Current market status
  - Latest market data
  - Technical indicators analysis
  - Interactive price charts
- Organizes reports in a structured directory based on date and time
- Configurable via YAML configuration file

## Requirements

- Python 3.8+
- Required Python packages (see requirements.txt):
  - pandas
  - yfinance
  - plotly
  - ta

## Installation

1. Clone the repository:
```bash
git clone https://github.com/snarasimhachakravarthy/stock-market-analysis.git
cd stock-market-analysis
```

2. Create and activate a virtual environment (or use the provided one):
```bash
# If you want to create a new environment:
python -m venv stock_market_env
source stock_market_env/bin/activate  # On Windows: stock_market_env\Scripts\activate
```

**To activate the project-specific virtual environment created with pyenv:**
```bash
source ~/.pyenv/versions/3.11.8/envs/stock_market_env/bin/activate
```

- Make sure to activate this environment before running any scripts or installing requirements.


3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The system is configured through `config/config.yaml`. You can customize:
- Market parameters (symbol, data fetch days)
- Technical indicators settings
- Report generation settings
- Email settings (if email functionality is enabled)

## Usage

1. Run the main script:
```bash
python main.py
```

2. The script will:
   - Fetch latest market data
   - Calculate technical indicators
   - Analyze market conditions
   - Generate a report in the `reports/daily_reports/` directory

3. Reports are organized in the following structure:
```
reports/
└── daily_reports/
    └── YYYY-MM-DD/
        └── HH-MM-SS/
            └── daily_market_report.html
```

## Report Structure

Each report contains:
1. Overall Market Status
2. Latest Market Data (Close Price, Volume, RSI)
3. Technical Indicators Analysis
4. Interactive Candlestick Chart with:
   - Price data
   - 50-day and 200-day SMAs
   - Volume bars

## Technical Indicators Used

1. **Simple Moving Averages (SMA)**
   - 50-day SMA (short-term trend)
   - 200-day SMA (long-term trend)
   - Used to identify trend direction and potential crossovers

2. **Relative Strength Index (RSI)**
   - 14-day period
   - Used to identify overbought (>70) and oversold (<30) conditions

3. **Moving Average Convergence Divergence (MACD)**
   - Fast period: 12 days
   - Slow period: 26 days
   - Signal period: 9 days
   - Used to identify momentum and potential trend changes

4. **Bollinger Bands**
   - 20-day period
   - 2 standard deviations
   - Used to identify volatility and potential overbought/oversold conditions

## Directory Structure

```
stock-market-analysis/
├── config/
│   └── config.yaml
├── reports/
│   └── daily_reports/
├── src/
│   ├── data_fetcher.py
│   ├── technical_analysis.py
│   ├── market_analyzer.py
│   ├── report_generator.py
│   └── email_sender.py
├── requirements.txt
└── main.py
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
