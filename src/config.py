import yaml
from typing import Dict

def load_config() -> Dict:
    """
    Load configuration from config.yaml
    
    Returns:
        Dict: Configuration dictionary
    """
    config_path = 'config/config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {
            'report': {
                'report_directory': 'reports/daily_reports/{date}/{timestamp}',
                'report_filename': 'daily_market_report.html'
            }
        }
