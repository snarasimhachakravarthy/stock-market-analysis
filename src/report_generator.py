import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from typing import Dict

class ReportGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.report_dir = self._format_directory_path(config['report']['report_directory'])
        self.report_filename = config['report']['report_filename']
        
    def _format_directory_path(self, path: str) -> str:
        """Format the directory path with date and timestamp"""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        timestamp_str = now.strftime('%H-%M-%S')
        
        # Replace placeholders in the path
        path = path.replace('{date}', date_str)
        path = path.replace('{timestamp}', timestamp_str)
        return path
    
    def generate_report(self, analysis: Dict[str, str], df: pd.DataFrame) -> str:
        """
        Generate HTML report with market analysis
        
        Args:
            analysis (Dict[str, str]): Market analysis results
            df (pd.DataFrame): DataFrame containing market data
            
        Returns:
            str: Path to generated report file
        """
        # Create report directory if it doesn't exist
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Get latest data
        latest_data = df.iloc[-1]
        
        # Create HTML report
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SENSEX Market Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .indicator {{ margin-bottom: 20px; }}
                .status-box {{
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .undervalued {{ background-color: #d4edda; color: #155724; }}
                .fairly-valued {{ background-color: #fff3cd; color: #856404; }}
                .overvalued {{ background-color: #f8d7da; color: #721c24; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SENSEX Market Analysis Report</h1>
                    <h3>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h3>
                </div>
                
                <div class="status-box {self._get_status_class(analysis['Overall Status'])}">
                    <h2>Overall Market Status: {analysis['Overall Status']}</h2>
                </div>
                
                <div class="indicator">
                    <h2>Latest Market Data</h2>
                    <ul>
                        <li>Close Price: {float(latest_data['Close']):.2f}</li>
                        <li>Volume: {int(latest_data['Volume']):,}</li>
                        <li>RSI: {float(latest_data['RSI']):.2f}</li>
                    </ul>
                </div>
                
                <div class="indicator">
                    <h2>Technical Indicators Analysis</h2>
                    <ul>
                        {''.join([f'<li>{indicator}: {status}</li>' for indicator, status in analysis.items()])}
                    </ul>
                </div>
                
                <div class="chart">
                    {self._generate_price_chart(df)}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save report
        report_path = os.path.join(self.report_dir, self.report_filename)
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report_path
    
    def _get_status_class(self, status: str) -> str:
        """Get CSS class based on market status"""
        if "Undervalued" in status:
            return "undervalued"
        elif "Overvalued" in status:
            return "overvalued"
        return "fairly-valued"
    
    def _generate_price_chart(self, df: pd.DataFrame) -> str:
        """Generate price chart using Plotly"""
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(x=df.index,
                                   open=df['Open'],
                                   high=df['High'],
                                   low=df['Low'],
                                   close=df['Close'],
                                   name='Price'))
        
        # Add SMAs
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'],
                               name='SMA 50',
                               line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'],
                               name='SMA 200',
                               line=dict(color='red', width=1)))
        
        fig.update_layout(
            title='SENSEX Price Chart with SMAs',
            yaxis_title='Price',
            xaxis_title='Date',
            template='plotly_white'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
