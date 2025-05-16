import pdfkit
import mysql.connector
from datetime import datetime
from db import connect_db  # Ensure db.py contains connect_db()
import re  # Add this at the top of your file
from PyQt6.QtWidgets import QMessageBox
import os

# Configure wkhtmltopdf path
# Get the current folder where the script is running
base_path = os.path.dirname(os.path.abspath(__file__))

# Build the relative path to wkhtmltopdf.exe
wkhtmltopdf_path = os.path.join(base_path, 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

# Pass it to pdfkit
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Define options to prevent rendering issues
options = {
    'enable-local-file-access': '',  # Required for loading local resources
    'disable-smart-shrinking': '',   # Fix scaling issues
    'no-stop-slow-scripts': '',      # Prevents timeouts on JavaScript
    'load-error-handling': 'ignore', # Ignores errors
    'load-media-error-handling': 'ignore'  # Ignores media loading issues
}

def calculate_item_totals(price, quantity, scheme_discount, gst):
    gross = price * quantity
    discount_amount = gross * (scheme_discount / 100)
    net_after_discount = gross - discount_amount
    gst_amount = net_after_discount * (gst / 100)
    subtotal = net_after_discount + gst_amount
    net_rate = net_after_discount / quantity if quantity != 0 else 0
    return round(gross, 2), round(discount_amount, 2), round(net_after_discount, 2), round(gst_amount, 2), round(subtotal, 2), round(net_rate, 2)

class BillingSystem:   
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def fetch_medicine(self, medicine_id=None, name=None):
        cursor = self.conn.cursor()
        if medicine_id is not None:
            cursor.execute(
                "SELECT medicine_id, name, price, net_rate, gst_percentage FROM medicines WHERE medicine_id = %s",
                (medicine_id,)
            )
        elif name is not None:
            cursor.execute(
                "SELECT medicine_id, name, price, net_rate, gst_percentage FROM medicines WHERE name = %s",
                (name,)
            )
        else:
            raise ValueError("Either medicine_id or name must be provided.")
        
        return cursor.fetchone()

    
    def get_medicine_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT medicine_id, name FROM medicines")  # Ensure both columns are selected
        return cursor.fetchall()   

    