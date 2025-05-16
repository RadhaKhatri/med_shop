import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reports import Reports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,QGroupBox,
    QLabel, QComboBox, QDateEdit, QMessageBox,QCalendarWidget,QInputDialog, QLineEdit,QGridLayout,QListWidget, QListWidgetItem
)
from PyQt6.QtCore import QDate
from fpdf import FPDF    
import imaplib
import email
from email.header import decode_header
import webbrowser
from PyQt6.QtWidgets import QListWidgetItem
from db import connect_db
from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QLineEdit, QCompleter, QMessageBox, QListWidgetItem
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtCore import QTimer
import smtplib
from email.message import EmailMessage
import mimetypes



class ReportUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Shop Reports")
        self.setGeometry(100, 100, 1000, 600)
        self.entries = {}

        
        self.conn = connect_db()  
        if not self.conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to MySQL! Exiting...")
            sys.exit(1)  # ❌ Exit app if DB connection fails
        self.cursor = self.conn.cursor()
        print("✅ Connected to MySQL!")
        
        # Fetch vendor emails from DB
        emails = self.get_vendor_emails()
        
        # Setup autocomplete using QCompleter
        email_completer = QCompleter()
        email_completer.setModel(QStringListModel(emails))
        email_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        email_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Match from anywhere
        email_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
      
        self.setStyleSheet("""
    QWidget {
        background-color: #f5f7fa;
        font-family: Segoe UI, sans-serif;
        font-size: 14px;
    }

    QGroupBox {
        border: 2px solid #444;
        border-radius: 10px;
        margin-top: 10px;
        padding: 15px;
        
        
    }

    QGroupBox:title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 3px;
        font-weight: bold;
        color: #333;
    }

    QLabel {
        font-weight: 600;
        color: #222;
    }

    QPushButton {
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
    }

    QPushButton:hover {
        background-color: #0056b3;
    }

    QPushButton:pressed {
        background-color: #3e8e41;
    }

    QComboBox, QLineEdit, QDateEdit {
        border: 2px solid #999;
        border-radius: 10px;
        padding: 6px;
        background-color: white;
    }

    QTableWidget {
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #fff;
        gridline-color: #aaa;
    }

    QHeaderView::section {
        font-weight: bold;
        padding: 4px;
        border: none;
    }

    QTableWidget QTableCornerButton::section {
        background-color: ;
    }

    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 2px solid;
    }
""")


        self.report_manager = Reports()

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        
         # === Top Control Section ===
        top_group = QGroupBox("Report Options")
        top_layout = QGridLayout()
        
        top_group.setFixedHeight(200)  # Adjust as needed      QVBoxLayout, setLayout

        
        self.pdf_list_widget = QListWidget()
        top_layout.addWidget(self.pdf_list_widget)
        self.pdf_list_widget.itemDoubleClicked.connect(self.open_pdf)

        self.report_type = QComboBox()
        self.report_type.addItems([
            "Daily Sales Report", "Monthly Sales Report", "Yearly Sales Report",
            "Product-wise Sales Report",
            "GST Summary Report", "GST Detailed Report", "GST Liability Report",
            "Profit Summary Report",
            "Expired Products Report", "Near Expiry Report",
            "Current Stock Report", "Low Stock Report", "Out of Stock Report",
            "Purchase Report"
        ])
        top_layout.addWidget(QLabel("                            Report Type:"),0,0)
        top_layout.addWidget(self.report_type,0,1)

        # Create the date input
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        # Create a calendar widget with clear navigation
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setNavigationBarVisible(True)

        # Apply stylesheet to ensure month/year are visible in black
        calendar.setStyleSheet("""
            QCalendarWidget QToolButton {
                color: black;
                font-weight: bold;
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;  /* Optional: hide dropdown arrow if too light */
            }
            QCalendarWidget QWidget {
                color: black;
            }
        """)

        # Set calendar to the date edit
        self.date_input.setCalendarWidget(calendar)

        # Add to layout
        top_layout.addWidget(QLabel("              Date:"), 0, 2)
        top_layout.addWidget(self.date_input, 0, 3)

        self.view_btn = QPushButton("View Report")
        self.view_btn.clicked.connect(self.view_report)
        top_layout.addWidget(self.view_btn,0,4)
        
        self.vendor_email_input = QLineEdit(self)
        self.vendor_email_input.setPlaceholderText("Enter vendor email to fetch bills")
        top_layout.addWidget(self.vendor_email_input,0,5)
        #self.populate_vendor_emails()
        self.vendor_email_input.setFocus()
        QTimer.singleShot(100, self.vendor_email_input.setFocus)
        
        # Apply to the email input field
        self.vendor_email_input.setCompleter(email_completer)
        
        self.fetch_bills_btn = QPushButton("Fetch Vendor Bills")
        self.fetch_bills_btn.clicked.connect(self.fetch_vendor_bills)
        top_layout.addWidget(self.fetch_bills_btn,0,6)

    #Fetched emails from DB:    
        
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.current_report_data = []
        self.current_report_name = ""
        
        
        bottom_group = QGroupBox()
        bottom_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.clicked.connect(self.export_excel)
        bottom_layout.addWidget(self.export_btn)
        
        self.export_pdf_btn = QPushButton("Export to PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        bottom_layout.addWidget(self.export_pdf_btn)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email to send report")
        bottom_layout.addWidget(self.email_input)

        self.send_email_btn = QPushButton("Send Email")
        self.send_email_btn.clicked.connect(self.send_email)
        bottom_layout.addWidget(self.send_email_btn)

        #self.gst_graph_btn = QPushButton("Show Monthly GST Graph")
        #self.gst_graph_btn.clicked.connect(self.plot_monthly_gst)
        #bottom_layout.addWidget(self.gst_graph_btn)

        layout.addLayout(bottom_layout)
        
        bottom_group.setLayout(bottom_layout)
        layout.addWidget(bottom_group)

        self.setLayout(layout)

        self.current_report_data = []
        self.current_report_name = ""

    def view_report(self):
        report_name = self.report_type.currentText()
        date = self.date_input.date().toString("yyyy-MM-dd")
        self.current_report_name = report_name.replace(" ", "_")
        try:
            data = []
            match report_name:
                case "Daily Sales Report":
                    data = self.report_manager.daily_sales_report(date)
                case "Monthly Sales Report":
                    year, month = date.split("-")[0], date.split("-")[1]
                    data = self.report_manager.monthly_sales_report(year, month)
                case "Yearly Sales Report":
                    year = date.split("-")[0]
                    data = self.report_manager.yearly_sales_report(year)
                case "Product-wise Sales Report":
                    data = self.report_manager.product_wise_sales_report()
                case "Vendor-wise Sales Report":
                    data = self.report_manager.vendor_wise_sales_report()
                case "GST Summary Report":
                    data = self.report_manager.gst_summary_report()
                case "GST Detailed Report":
                    # Use last 30 days
                    today = QDate.currentDate()
                    start = today.addDays(-30).toString("yyyy-MM-dd")
                    end = today.toString("yyyy-MM-dd")
                    data = self.report_manager.gst_detailed_report_filtered(start, end)
                case "GST Liability Report":
                    start = end = date
                    data = self.report_manager.gst_liability_report(start, end)
                case "Profit Summary Report":
                    data = self.report_manager.profit_summary_report()
                case "Loss Report":
                    data = self.report_manager.loss_report()
                case "High-Profit Products Report":
                    data = self.report_manager.high_profit_products_report()
                case "Expired Products Report":
                    data = self.report_manager.expired_products_report()
                case "Near Expiry Report":
                    data = self.report_manager.near_expiry_report()
                case "Current Stock Report":
                    data = self.report_manager.current_stock_report()
                case "Low Stock Report":
                    data = self.report_manager.low_stock_report()
                case "Out of Stock Report":
                    data = self.report_manager.out_of_stock_report()
                case "Purchase Report":
                    data = self.report_manager.purchase_report()
            self.current_report_data = data
            self.show_table(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_table(self, data):
        self.table.clear()
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        headers = list(data[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, header in enumerate(headers):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[header])))

        # Option 1: Auto-resize to fit contents
        self.table.resizeColumnsToContents()
    
    def export_excel(self):
        if not self.current_report_data:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return
        try:
            self.report_manager.export_to_excel(self.current_report_data, self.current_report_name, format='excel')
            QMessageBox.information(self, "Success", f"Exported to reports/{self.current_report_name}.xlsx")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

            

    def send_email(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Missing Email", "Please enter an email address.")
            return
        try:
            file_path = f'reports/{self.current_report_name}.xlsx'
            if not os.path.exists(file_path):
                self.export_excel()
            subject = f"Medical Shop Report - {self.current_report_name}"
            body = f"Attached is the report: {self.current_report_name}"
            self.report_manager.send_email_with_report(email, subject, body, file_path)
            QMessageBox.information(self, "Success", f"Email sent to {email}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def export_pdf(self):
        if not self.current_report_data:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return

        try:
            # PDF creation
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Siddhanath Medical, Ramanandnagar", ln=True, align="C")

            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, "Owner: Aniket Ankush Gejage", ln=True, align="C")
            pdf.cell(0, 10, "Address: Shop No 6, Bhagatsingh Chowk, Kirloskarwadi, Ramanandnagar, Tal- Palus (Sangli)", ln=True, align="C")
            pdf.cell(0, 10, "Email: aniketgejage12345@gmail.com | Contact: 9766019199", ln=True, align="C")
            pdf.cell(0, 10, "Registration Numbers: MH-SAN-458563 / MH-SAN-458564", ln=True, align="C")

            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Report: {self.current_report_name}", ln=True)

            pdf.ln(5)
            headers = self.current_report_data[0].keys()
            col_width = 190 // len(headers)

            pdf.set_font("Arial", "B", 12)
            for header in headers:
                pdf.cell(col_width, 10, str(header), 1)
            pdf.ln()

            pdf.set_font("Arial", "", 12)
            for row in self.current_report_data:
                for value in row.values():
                    pdf.cell(col_width, 10, str(value), 1)
                pdf.ln()

            # Save PDF
            reports_folder = r"reports"
            if not os.path.exists(reports_folder):
                os.makedirs(reports_folder)

            filename = f"{self.current_report_name}.pdf"
            save_path = os.path.join(reports_folder, filename)
            pdf.output(save_path)

            # Message Box UI
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("✅ PDF Exported")
            msg_box.setText("Report exported successfully!")
            msg_box.setInformativeText(f"Saved at:\n{save_path}")
            msg_box.setIcon(QMessageBox.Icon.Information)

            open_button = msg_box.addButton("📂 Open File", QMessageBox.ButtonRole.ActionRole)
            share_button = msg_box.addButton("📤 Share File", QMessageBox.ButtonRole.ActionRole)
            ok_button = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

            msg_box.exec()

            clicked = msg_box.clickedButton()
            if clicked == open_button:
                if os.path.exists(save_path):
                    os.startfile(save_path)
                else:
                    QMessageBox.critical(self, "Error", f"❌ File not found:\n{save_path}")

            elif clicked == share_button:
                if os.path.exists(save_path):
                    receiver_email, ok = QInputDialog.getText(self, "Recipient Email", "Enter recipient's email:", QLineEdit.EchoMode.Normal)
                    if ok and receiver_email.strip():
                        try:
                            sender_email = "beactive1474@gmail.com"
                            app_password = "zrtr smiw bfvd droc"  # Gmail App Password

                            msg = EmailMessage()
                            msg['Subject'] = f'Report: {self.current_report_name}'
                            msg['From'] = sender_email
                            msg['To'] = receiver_email.strip()
                            msg.set_content(f"Dear user,\n\nPlease find the attached report.\n\nRegards,\nSiddhanath Medical")

                            with open(save_path, 'rb') as f:
                                file_data = f.read()
                                file_type, _ = mimetypes.guess_type(save_path)
                                main_type, sub_type = file_type.split('/', 1)
                                msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(save_path))

                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                smtp.login(sender_email, app_password)
                                smtp.send_message(msg)

                            QMessageBox.information(self, "Email Sent", "📤 Report shared successfully via email!")

                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"❌ Failed to send email:\n{str(e)}")
                    else:
                        QMessageBox.warning(self, "Cancelled", "📧 Email sending cancelled or invalid email entered.")
                else:
                    QMessageBox.critical(self, "Error", f"❌ File not found:\n{save_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

            
    

    #def plot_monthly_gst(self):
        #try:
            #data = self.report_manager.gst_liability_report()
            #if not data:
                #QMessageBox.warning(self, "No Data", "No GST data available to plot.")
                #return
            #months = [f"{row['month']}/{row['year']}" for row in data]
            #gst = [row['total_gst_collected'] for row in data]

            #plt.bar(months, gst, color='green')
            #plt.xlabel("Month")
            #plt.ylabel("Total GST Collected")
            #plt.title("Monthly GST Liability")
            #plt.xticks(rotation=45)
            #plt.tight_layout()
            #plt.show()
        #except Exception as e:
            #QMessageBox.critical(self, "Error", str(e))

    def fetch_vendor_bills(self):
        vendor_email = self.vendor_email_input.text().strip()
        if not vendor_email:
            QMessageBox.warning(self, "Input Error", "Please enter a vendor email.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Store the vendor email if it doesn't already exist
            cursor.execute("SELECT vendor_id FROM vendors WHERE email = %s", (vendor_email,))
            result = cursor.fetchone()   

            if not result:
                cursor.execute("INSERT INTO vendors (name, email) VALUES (%s, %s)", ("Unknown Vendor", vendor_email))
                conn.commit()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error accessing database: {str(e)}")
            return
        finally:
            if conn:
                cursor.close()
                conn.close()

        # Start fetching vendor bills from Gmail
        self.fetch_emails_from_gmail(vendor_email)

    def fetch_emails_from_gmail(self, vendor_email):
        imap_server = "imap.gmail.com"
        email_user = "beactive1474@gmail.com"
        email_pass = "zrtr smiw bfvd droc"  # App Password

        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("inbox")

            result, data = mail.search(None, f'(FROM "{vendor_email}")')
            email_ids = data[0].split()
            os.makedirs("vendor_bills", exist_ok=True)

            for num in email_ids:
                result, msg_data = mail.fetch(num, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = part.get_filename()
                    if filename and filename.endswith(".pdf"):
                        filepath = os.path.join("vendor_bills", filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))

            QMessageBox.information(self, "Done", "Vendor bills fetched successfully!")
            self.show_fetched_pdfs("vendor_bills")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch vendor bills: {str(e)}")
            
    def open_pdf(self, item):
        import webbrowser
        filepath = os.path.join("vendor_bills", item.text())
        if os.path.exists(filepath):
            webbrowser.open(filepath)
        else:
            QMessageBox.warning(self, "File not found", "Could not find the selected file.")


    def show_fetched_pdfs(self, folder_path="vendor_bills"):
        if not os.path.exists(folder_path):
            QMessageBox.information(self, "No Files", "No PDF files were fetched.")
            return

        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        if not pdf_files:
            QMessageBox.information(self, "No Files", "No PDF files found in the folder.")
            return

        self.pdf_list_widget.clear()
        for pdf in pdf_files:
            item = QListWidgetItem(pdf)
            self.pdf_list_widget.addItem(item)

    def get_vendor_emails(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email FROM vendors")
        return [row[0] for row in cursor.fetchall()]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ReportUI()
    window.show()
    sys.exit(app.exec())




#Actions
#  def populate_vendor_emails(self):
