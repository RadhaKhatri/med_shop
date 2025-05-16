import mysql.connector
from db import connect_db
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
from fpdf import FPDF

# PyQt5 message box for alerts
from PyQt6.QtWidgets import QMessageBox

# For handling emails and attachments
import imaplib
import email
from email.header import decode_header

# For file system operations
import os



class Reports:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor(dictionary=True)

    def daily_sales_report(self, date):
        try:
            query = """
                SELECT s.sale_id, m.name AS medicine_name, s.quantity, s.total_price, s.gst_amount, s.sale_date
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.medicine_id
                WHERE DATE(s.sale_date) = %s
            """
            self.cursor.execute(query, (date,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def monthly_sales_report(self, year, month):
        try:
            query = """
                SELECT m.name AS medicine_name, SUM(s.quantity) AS total_quantity, SUM(s.total_price) AS total_price
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.medicine_id
                WHERE YEAR(s.sale_date) = %s AND MONTH(s.sale_date) = %s
                GROUP BY m.name
            """
            self.cursor.execute(query, (year, month))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def yearly_sales_report(self, year):
        try:
            query = """
                SELECT m.name AS medicine_name, SUM(s.quantity) AS total_quantity, SUM(s.total_price) AS total_price
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.medicine_id
                WHERE YEAR(s.sale_date) = %s
                GROUP BY m.name
            """
            self.cursor.execute(query, (year,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def gst_summary_report(self):
        try:
            query = """
                SELECT m.gst_percentage, SUM(s.total_price) AS total_sales, SUM(s.gst_amount) AS total_gst
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.medicine_id
                GROUP BY m.gst_percentage
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def expired_products_report(self):
        try:
            query = """
                SELECT name, batch_no, expiry_date
                FROM medicines
                WHERE expiry_date < CURDATE()    
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def near_expiry_report(self):
        try:
            query = """
                SELECT name, batch_no, expiry_date
                FROM medicines
                WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def low_stock_report(self):
        try:
            query = """
                SELECT name, stock_quantity
                FROM medicines
                WHERE stock_quantity <= 10
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def current_stock_report(self):
        try:
            query = "SELECT name, stock_quantity FROM medicines"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []

    def purchase_report(self):
        try:
            query = """
                SELECT p.purchase_id, v.name AS vendor_name, m.name AS medicine_name,
                       p.quantity, p.purchase_price, p.purchase_date
                FROM purchases p
                JOIN vendors v ON p.vendor_id = v.vendor_id
                JOIN medicines m ON p.medicine_id = m.medicine_id
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return []
    #########################################################################  
    def out_of_stock_report(self):
        query = """
        SELECT name, category, manufacturer, batch_no, expiry_date
        FROM medicines
        WHERE stock_quantity = 0
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def high_profit_products_report(self):
        query = """
        SELECT 
            m.name,
            m.price AS selling_price,
            m.purchase_price,
            (m.price - m.purchase_price) AS profit_per_unit
        FROM medicines m
        WHERE (m.price - m.purchase_price) > 10  -- Adjust threshold as needed
        ORDER BY profit_per_unit DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def product_wise_sales_report(self):
        query = """
        SELECT 
            m.name,
            SUM(s.quantity) AS total_quantity_sold,
            SUM(s.total_price) AS total_sales_amount
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        GROUP BY m.medicine_id
        ORDER BY total_sales_amount DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def vendor_wise_sales_report(self):
        query = """
        SELECT 
            v.name AS vendor_name,
            SUM(s.total_price) AS total_sales
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        JOIN vendors v ON m.vendor_id = v.vendor_id
        GROUP BY v.vendor_id
        ORDER BY total_sales DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def gst_detailed_report(self):
        query = """
        SELECT 
            s.sale_id,
            m.name AS medicine_name,
            s.sale_date,
            s.total_price,
            m.gst_percentage,
            ROUND(s.total_price * (m.gst_percentage / (100 + m.gst_percentage)), 2) AS gst_amount
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        ORDER BY s.sale_date DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def gst_liability_report(self, start_date=None, end_date=None):
        base_query = """
            SELECT 
                MONTH(s.sale_date) AS month,
                YEAR(s.sale_date) AS year,
                SUM(ROUND(s.total_price * (m.gst_percentage / (100 + m.gst_percentage)), 2)) AS total_gst_collected
            FROM sales s
            JOIN medicines m ON s.medicine_id = m.medicine_id
        """

        params = []
        if start_date and end_date:
            base_query += " WHERE s.sale_date BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        base_query += """
            GROUP BY YEAR(s.sale_date), MONTH(s.sale_date)
            ORDER BY year DESC, month DESC
        """

        self.cursor.execute(base_query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def profit_summary_report(self):
        query = """
        SELECT 
            m.name AS medicine_name,
            SUM(s.quantity) AS total_quantity_sold,
            AVG(m.price) AS selling_price,
            AVG(m.purchase_price) AS purchase_price,
            (AVG(m.price) - AVG(m.purchase_price)) * SUM(s.quantity) AS total_profit
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        GROUP BY m.medicine_id
        ORDER BY total_profit DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]


    def loss_report(self):
        query = """
        SELECT 
            m.name AS medicine_name,
            SUM(s.quantity) AS total_quantity_sold,
            AVG(m.price) AS selling_price,
            AVG(m.purchase_price) AS purchase_price,
            (AVG(m.price) - AVG(m.purchase_price)) * SUM(s.quantity) AS total_loss
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        GROUP BY m.medicine_id
        HAVING total_loss < 0
        ORDER BY total_loss ASC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]


    def export_to_excel(self, data, report_name, format='excel'):
        if not data:
            print("⚠️ No data to export.")
            return

        df = pd.DataFrame(data)
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)

        if format == 'excel':
            file_path = os.path.join(reports_dir, f"{report_name}.xlsx")
            df.to_excel(file_path, index=False)
            print(f"✅ Excel report exported to {file_path}")

        elif format == 'pdf':
            file_path = os.path.join(reports_dir, f"{report_name}.pdf")
            self._export_to_pdf(df, file_path)
            print(f"✅ PDF report exported to {file_path}")

        else:
            print("❌ Unsupported format. Choose 'excel' or 'pdf'.")
            return

        return file_path

    def _export_to_pdf(self, df, file_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        col_width = pdf.w / (len(df.columns) + 1)

        # Header
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), border=1)
        pdf.ln()

        # Rows
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1)
            pdf.ln()

        pdf.output(file_path)

    def send_email_with_report(self, to_email, subject, body, attachment_path):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'beactive1474@gmail.com'
        msg['To'] = to_email
        msg.set_content(body)

        # Attach file
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Send using Gmail SMTP (you must enable 'less secure apps' or use App Password)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('beactive1474@gmail.com', 'zrtr smiw bfvd droc')  # Use an App Password!
            smtp.send_message(msg)

        print(f"📧 Email sent to {to_email}")

    def gst_detailed_report_filtered(self, start_date, end_date):
        query = """
        SELECT 
            s.sale_id,
            m.name AS medicine_name,
            s.sale_date,
            s.total_price,
            m.gst_percentage,
            ROUND(s.total_price * (m.gst_percentage / (100 + m.gst_percentage)), 2) AS gst_amount
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        WHERE s.sale_date BETWEEN %s AND %s
        ORDER BY s.sale_date DESC
        """
        self.cursor.execute(query, (start_date, end_date))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def close_connection(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
