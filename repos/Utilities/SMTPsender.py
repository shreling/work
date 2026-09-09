
import sys 
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

## Read in text from DB 

folders = ['Dash', 'Utilities']
for folder in folders:
    path_to_folders = os.path.join('C:\\Users\\' + os.getlogin() + '\\Source\\Repos\\Investments-Quant\\' + folder)
    if path_to_folders not in sys.path:
        sys.path.append(path_to_folders)
import matplotlib.pyplot as plt
from Utility_functions import *
# Initialising the connection to the databases
connection_dict, params_dict_dict = initialize_env_and_db_connections()

class SMTPsender:
    """

    A class for sending emails using the SendGrid API. Designed to send email from an email address on SMTP server. 
    Avoids use of traditional Outlook library. 

    Attributes:
        connection_dict (dict): A dictionary containing the SendGrid client.
        from_email (str): The sender's email address.
        to_emails (str or list): The recipient's email address(es).
        subject (str): The subject of the email.
        html_content (str): The HTML content of the email.
    

    Usage:
        
        1.) smtp_sender = SMTPsender(
            connection_dict,
            from_email="Quantreports@mediolanum.ie",
            to_emails="Quantreports@mediolanum.ie",
            subject='Test',
            html_content='<strong>This is a test email from Sendgrid - SMTP Server...</strong>'
             )
            response = smtp_sender.send_email()
        
        2.) smtp_sender.set_fancy_theme(theme_color="#0033A0", text_color="#000000") ## dark blue theme
            smtp_sender.add_table(html_table, intro_text="This is a test table") ## can add multiple tables
            smtp_sender.generate_fancy_html() ## this generates the html content for the email body
            response = smtp_sender.send_email()
    """
    def __init__(self, connection_dict, from_email, to_emails, subject, html_content = ""):
        self.from_email = from_email
        self.to_emails = to_emails
        self.subject = subject
        self.sendgrid_client = connection_dict['sendgrid_client']
        self.tables = []
        self.intro_texts = []
        self.html_content = html_content

    def send_email(self):
        ## generic email sender method
        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_emails,
            subject=self.subject,
            html_content=self.html_content)
        try:
            response = self.sendgrid_client.send(message)
            return response
        except Exception as e:
            print(e)

    def set_fancy_theme(self, theme_color, text_color="#000000"):
        ## set the theme color for the email template - this is used in the generate_fancy_html method
        ## usually dark blue or green in ESG emails. 
        self.theme_color = theme_color
        self.text_color = text_color

    def add_table(self, html_table, intro_text=""):
        ## this gets used in the generate_fancy_html method to loop through and add multiple tables
        self.tables.append(html_table)
        self.intro_texts.append(intro_text)

    def generate_fancy_html(self):
        ## tidy table style
        table_style = f"""
        <style>
        table.dataframe {{
            border-collapse: collapse; 
            width: 100%; 
            border: 1px solid black;
        }} 
        table.dataframe th, table.dataframe td {{
            border: 1px solid black; 
            text-align: left; 
            padding: 5px; 
            white-space: nowrap; 
            font-size: 10px; 
            overflow: visible; 
            text-overflow: ellipsis; 
            word-wrap: break-word;
        }} 
        table.dataframe th {{
            background-color: {self.theme_color}; 
            color: white;
        }} 
        table.dataframe td {{
            background-color: #ffffff; 
            color: {self.text_color};
        }}
        </style>
        """
        ## Rather than create html for each potential table we just Auto loop through the tables and intro_texts lists with zip and then it will auto concat these html snippets together
        tables_html = ""
        for intro_text, html_table in zip(self.intro_texts, self.tables): ## Zip through two lists at once...
            tables_html += f"""
                        <tr>
                            <td colspan="2" style="text-align: center; color: {self.text_color}; font-family: Arial, sans-serif; font-size: 11px; line-height: 24px; padding: 20px 0 30px 0;">
                                <p style="margin: 0;">{intro_text}</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="vertical-align: top; padding-bottom: 15px; font-family: Arial, sans-serif; font-size: 12px;text-align: center;">
                                <div style="text-align: center;">
                                   {html_table}
                                </div>
                            </td>
                        </tr>
                        """
            
        ## In reality this is a template for the email - we can add multiple tables and intro texts to the email by using the add_table method
        ## if we didnt have the above zip method we end up with a really long ugly html string with lots of repeated code, depdnant on how many tables we want to add.
        ## {tables_html} below is the dynamic part of the email body 

        self.html_content = f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Data Report Template</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            {table_style}
        </head>
        <body style="margin: 0; padding: 0;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td style="padding: 20px 0 30px 0;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; border: 1px solid #cccccc; width: 100%;">
                            <tr>
                                <td align="center" bgcolor="{self.theme_color}" style="padding: 40px 0 30px 0;">
                                    <h2 style="font-size: 16px; margin: 0; color: white;">{self.subject}</h2>
                                </td>
                            </tr>
                            <tr>
                                <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                                        {tables_html} 
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """


