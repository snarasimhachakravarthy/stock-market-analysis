import os
import yaml
import logging
from datetime import datetime
from src.data_fetcher import DataFetcher
from src.technical_analysis import TechnicalAnalysis
from src.market_analyzer import MarketAnalyzer
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('market_analysis.log'),
            logging.StreamHandler()
        ]
    )

def load_config():
    """Load configuration from YAML file"""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = load_config()
        
        # Fetch data
        logger.info("Fetching market data...")
        fetcher = DataFetcher(
            symbol=config['market']['symbol'],
            days=config['market']['data_fetch_days']
        )
        df = fetcher.fetch_data()
        
        if df.empty:
            logger.error("Failed to fetch market data")
            return
            
        # Calculate technical indicators
        logger.info("Calculating technical indicators...")
        ta = TechnicalAnalysis(df)
        df_with_indicators = ta.add_all_indicators(config['indicators'])
        
        # Analyze market
        logger.info("Analyzing market conditions...")
        analyzer = MarketAnalyzer(df_with_indicators)
        analysis = analyzer.analyze_market()
        
        # Generate report
        logger.info("Generating report...")
        report_generator = ReportGenerator(config)
        report_path = report_generator.generate_report(analysis, df_with_indicators)
        
        logger.info(f"Report generated successfully at: {report_path}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main()
