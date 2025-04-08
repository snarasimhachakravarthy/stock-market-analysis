import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict
import json

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
    
    def _create_price_chart(self, df: pd.DataFrame) -> str:
        """
        Create a candlestick chart with moving averages
        """
        # Create figure with subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, 
                           row_heights=[0.7, 0.3])
        
        # Add candlestick
        fig.add_trace(
            go.Candlestick(x=df.index,
                         open=df['Open'],
                         high=df['High'],
                         low=df['Low'],
                         close=df['Close'],
                         name='Price'),
            row=1, col=1
        )
        
        # Add moving averages if available
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['SMA_50'],
                          line=dict(color='blue', width=1.5),
                          name='50-day MA'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df.index, y=df['SMA_200'],
                          line=dict(color='orange', width=1.5),
                          name='200-day MA'),
                row=1, col=1
            )
        
        # Add volume
        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'],
                  marker=dict(color='gray'),
                  name='Volume'),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='SENSEX Price Analysis',
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            height=800,
            width=1200,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig.to_html(full_html=False)
    
    def _create_rsi_chart(self, df: pd.DataFrame) -> str:
        """
        Create RSI chart with overbought/oversold levels
        """
        if 'RSI' not in df.columns:
            return """
            <div class="status-card neutral">
                <h3>RSI Analysis Not Available</h3>
                <p>Insufficient data for RSI calculation</p>
            </div>
            """
        
        fig = go.Figure()
        
        # Add RSI line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'],
                      line=dict(color='blue', width=1.5),
                      name='RSI')
        )
        
        # Add overbought/oversold levels
        fig.add_hline(y=70, line=dict(color='red', width=1, dash='dash'),
                     annotation_text="Overbought", annotation_position="top left")
        fig.add_hline(y=30, line=dict(color='green', width=1, dash='dash'),
                     annotation_text="Oversold", annotation_position="bottom left")
        
        # Update layout
        fig.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_title='RSI Value',
            template='plotly_white',
            height=400,
            width=1200,
            showlegend=False,
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False)
    
    def _create_macd_chart(self, df: pd.DataFrame) -> str:
        """
        Create MACD chart with signal line and histogram
        """
        if 'MACD' not in df.columns or 'MACD_Signal' not in df.columns:
            return """
            <div class="status-card neutral">
                <h3>MACD Analysis Not Available</h3>
                <p>Insufficient data for MACD calculation</p>
            </div>
            """
        
        fig = go.Figure()
        
        # Add MACD line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'],
                      line=dict(color='blue', width=1.5),
                      name='MACD')
        )
        
        # Add Signal line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'],
                      line=dict(color='orange', width=1.5),
                      name='Signal')
        )
        
        # Add MACD Histogram
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            macd_hist = df['MACD'] - df['MACD_Signal']
            colors = ['green' if v > 0 else 'red' for v in macd_hist]
            fig.add_trace(
                go.Bar(x=df.index, y=macd_hist,
                      marker=dict(color=colors),
                      name='Histogram')
            )
        
        # Update layout
        fig.update_layout(
            title='MACD Analysis',
            yaxis_title='Value',
            template='plotly_white',
            height=400,
            width=1200,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False)
    
    def _create_bollinger_bands_chart(self, df: pd.DataFrame) -> str:
        """
        Create Bollinger Bands chart
        """
        if 'BB_Upper' not in df.columns or 'BB_Lower' not in df.columns:
            return """
            <div class="status-card neutral">
                <h3>Bollinger Bands Analysis Not Available</h3>
                <p>Insufficient data for Bollinger Bands calculation</p>
            </div>
            """
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Close'],
                      line=dict(color='black', width=1.5),
                      name='Price')
        )
        
        # Add Bollinger Bands
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Upper'],
                      line=dict(color='gray', width=1, dash='dash'),
                      name='Upper Band')
        )
        
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Lower'],
                      line=dict(color='gray', width=1, dash='dash'),
                      name='Lower Band')
        )
        
        # Update layout
        fig.update_layout(
            title='Bollinger Bands Analysis',
            yaxis_title='Price',
            template='plotly_white',
            height=400,
            width=1200,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False)
    
    def _generate_status_card(self, status: str) -> str:
        """Generate a status card with appropriate styling"""
        status_class = {
            'Bullish': 'bullish',
            'Bearish': 'bearish',
            'Sideways': 'neutral',
            'Mixed': 'neutral'
        }.get(status.split()[0], 'neutral')  # Get first word of status
        
        return f"""
        <div class="status-card {status_class}">
            <h2>Market Status</h2>
            <div class="status-value">
                <span class="icon">{self._get_status_icon(status)}</span>
                <span class="text">{status}</span>
            </div>
        </div>
        """
    
    def _get_status_icon(self, status: str) -> str:
        """Get appropriate icon for status"""
        if "Bullish" in status or "Up" in status:
            return '📈'
        elif "Bearish" in status or "Down" in status:
            return '📉'
        elif "Sideways" in status or "Mixed" in status:
            return '➡️'
        else:
            return 'ℹ️'
    
    def _generate_stat_grid(self, df: pd.DataFrame, analysis: Dict[str, str]) -> str:
        """Generate a grid of market statistics"""
        latest_data = df.iloc[-1]
        
        # Get latest SMA values if available
        sma_50 = float(latest_data['SMA_50']) if 'SMA_50' in df.columns else None
        sma_200 = float(latest_data['SMA_200']) if 'SMA_200' in df.columns else None
        
        return f"""
        <div class="stat-grid">
            <div class="stat-card">
                <h3>Close Price</h3>
                <div class="value">₹{float(latest_data['Close']):,.2f}</div>
                <div class="label">Current Market Price</div>
            </div>
            
            <div class="stat-card">
                <h3>RSI</h3>
                <div class="value">{float(latest_data['RSI']):.2f}</div>
                <div class="label">Relative Strength Index</div>
            </div>
            
            <div class="stat-card">
                <h3>Volume</h3>
                <div class="value">{int(latest_data['Volume']):,}</div>
                <div class="label">Trading Volume</div>
            </div>
            
            <div class="stat-card">
                <h3>SMAs</h3>
                <div class="value">
                    50D: {sma_50:.2f}{' (N/A)' if sma_50 is None else ''}<br>
                    200D: {sma_200:.2f}{' (N/A)' if sma_200 is None else ''}
                </div>
                <div class="label">Moving Averages</div>
            </div>
        </div>
        """
    
    def _generate_indicator_analysis(self, analysis: Dict[str, str], df: pd.DataFrame) -> str:
        """Generate analysis cards for technical indicators"""
        latest_data = df.iloc[-1]
        
        indicators = {
            'SMA': {
                'status': analysis.get('SMA', 'Insufficient data'),
                'value': f"50D: {float(df['SMA_50'].iloc[-1]):.2f}<br>200D: {float(df['SMA_200'].iloc[-1]):.2f}" if 'SMA_50' in df.columns and 'SMA_200' in df.columns else 'N/A',
                'explanation': "Moving averages indicate trend direction. When 50D crosses above 200D, it's a bullish signal (Golden Cross)."
            },
            'RSI': {
                'status': analysis.get('RSI', 'Insufficient data'),
                'value': f"{float(latest_data['RSI']):.2f}" if 'RSI' in df.columns else 'N/A',
                'explanation': "RSI measures overbought/oversold conditions. Values above 70 indicate overbought conditions, while below 30 indicate oversold conditions."
            },
            'MACD': {
                'status': analysis.get('MACD', 'Insufficient data'),
                'value': f"MACD: {float(latest_data['MACD']):.2f}<br>Signal: {float(latest_data['MACD_Signal']):.2f}" if 'MACD' in df.columns and 'MACD_Signal' in df.columns else 'N/A',
                'explanation': "MACD shows momentum. When MACD line crosses above signal line, it's a bullish signal."
            },
            'Bollinger Bands': {
                'status': analysis.get('Bollinger Bands', 'Insufficient data'),
                'value': f"Price: {float(latest_data['Close']):.2f}<br>BB: {float(df['BB_Upper'].iloc[-1]):.2f}/{float(df['BB_Lower'].iloc[-1]):.2f}" if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns else 'N/A',
                'explanation': "Bollinger Bands measure volatility. When price touches upper band, it's overbought. When price touches lower band, it's oversold."
            }
        }
        
        analysis_cards = []
        for indicator, data in indicators.items():
            status_class = {
                'Bullish': 'bullish',
                'Bearish': 'bearish',
                'Neutral': 'neutral',
                'Insufficient': 'neutral'
            }.get(data['status'].split()[0], 'neutral')  # Get first word of status
            
            analysis_cards.append(f"""
            <div class="indicator-card">
                <div class="status {status_class}">{data['status']}</div>
                <h3>{indicator}</h3>
                <div class="value">{data['value']}</div>
                <p class="explanation">{data['explanation']}</p>
            </div>
            """)
        
        return f"<div class='indicator-analysis'>{''.join(analysis_cards)}</div>"
    
    def _generate_reference_glossary(self) -> str:
        """Generate reference glossary section"""
        glossary_items = [
            {
                'title': 'RSI Levels',
                'content': 'Oversold < 30<br>Overbought > 70<br>Neutral: 30-70'
            },
            {
                'title': 'MACD Signals',
                'content': 'Bullish: MACD crosses above Signal<br>Bearish: MACD crosses below Signal<br>Neutral: Lines are close'
            },
            {
                'title': 'SMA Crosses',
                'content': 'Golden Cross: 50D crosses above 200D<br>Death Cross: 50D crosses below 200D<br>Neutral: Lines are close'
            },
            {
                'title': 'Bollinger Bands',
                'content': 'Overbought: Price touches Upper Band<br>Oversold: Price touches Lower Band<br>Neutral: Price within Bands'
            }
        ]
        
        glossary_items_html = []
        for item in glossary_items:
            glossary_items_html.append(f"""
            <div class="glossary-item">
                <h4>{item['title']}</h4>
                <p>{item['content']}</p>
            </div>
            """)
        
        return f"""
        <div class="glossary">
            <h3>Reference Glossary</h3>
            {''.join(glossary_items_html)}
        </div>
        """
    
    def generate_report(self, analysis: Dict[str, str], df: pd.DataFrame) -> str:
        """
        Generate HTML report with enhanced structure and visuals
        """
        # Create report directory if it doesn't exist
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Generate charts
        price_chart = self._create_price_chart(df)
        rsi_chart = self._create_rsi_chart(df)
        macd_chart = self._create_macd_chart(df)
        bollinger_chart = self._create_bollinger_bands_chart(df)
        
        # Create HTML report
        report = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SENSEX Market Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                {open('src/styles/report.css', 'r').read()}
            </style>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 SENSEX Market Analysis</h1>
                    <div class="timestamp">Generated on: {datetime.now().strftime('%d %B %Y at %I:%M %p IST')}</div>
                </div>
                
                {self._generate_status_card(analysis['Overall Status'])}
                
                {self._generate_stat_grid(df, analysis)}
                
                <div class="chart-container">
                    <div class="chart-card">
                        <h4>Price Action & Moving Averages</h4>
                        {price_chart}
                    </div>
                    
                    <div class="chart-card">
                        <h4>Relative Strength Index (RSI)</h4>
                        {rsi_chart}
                    </div>
                    
                    <div class="chart-card">
                        <h4>MACD Analysis</h4>
                        {macd_chart}
                    </div>
                    
                    <div class="chart-card">
                        <h4>Bollinger Bands</h4>
                        {bollinger_chart}
                    </div>
                </div>
                
                {self._generate_indicator_analysis(analysis, df)}
                
                <!-- Only show sector analysis if available -->
                {'<div class="status-card neutral">' if 'sector_rotation' in analysis else ''}
                    <h2>Sector Performance</h2>
                    <div class="sector-metric">
                        <h3>Top Performing Sector (1-Week): {analysis.get('sector_rotation', {}).get('top_performer_week', 'N/A')}</h3>
                    </div>
                    <div class="sector-metric">
                        <h3>Bottom Performing Sector (1-Week): {analysis.get('sector_rotation', {}).get('bottom_performer_week', 'N/A')}</h3>
                    </div>
                    <div class="sector-metric">
                        <h3>Sector Trend: {analysis.get('sector_rotation', {}).get('trend', 'N/A')}</h3>
                    </div>
                </div>
                
                {self._generate_reference_glossary()}
            </div>
        </body>
        </html>
        """
        
        # Save report
        report_path = os.path.join(self.report_dir, self.report_filename)
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report_path
