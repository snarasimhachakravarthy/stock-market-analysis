import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EmailSender:
    def __init__(self, config: dict):
        self.config = config
        self.smtp_server = config['email']['smtp_server']
        self.smtp_port = config['email']['smtp_port']
        self.sender_email = config['email']['sender_email']
        self.sender_password = config['email']['sender_password']
        self.recipient_email = config['email']['recipient_email']
        
    def send_report(self, report_path: str) -> bool:
        """
        Send market analysis report via email
        
        Args:
            report_path (str): Path to the HTML report file
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"SENSEX Market Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Attach HTML content
            with open(report_path, 'r') as f:
                html_content = f.read()
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Attach report as attachment
            with open(report_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename=report.html')
                msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
