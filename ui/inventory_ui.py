import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db  

from inventory_manager import InventoryManager  # ✅ Importing from the parent folder

from PyQt6.QtWidgets import QApplication,QCheckBox, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView
from datetime import date, datetime
from PyQt6.QtGui import QColor
import mysql.connector
from fpdf import FPDF
from PyQt6.QtWidgets import QDialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from email.message import EmailMessage
import mimetypes
from PyQt6.QtWidgets import QInputDialog




class InventoryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Shop Inventory Management")
        self.setGeometry(100, 100, 900, 500)
        
        self.conn = connect_db()  
        if not self.conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to MySQL! Exiting...")
            sys.exit(1)  # ❌ Exit app if DB connection fails
        self.cursor = self.conn.cursor()
        print("✅ Connected to MySQL!")

        self.inventory = InventoryManager()
        
        self.initUI()

    def initUI(self):
        # Main Layout  
        main_layout = QVBoxLayout()
        
        # Heading Label
        self.heading = QLabel("Inventory Management")
        self.heading.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Form Layout
        self.entries = {}
        fields = ["Name", "Category", "Manufacturer", "Batch No", "Expiry Date (YYYY-MM-DD)","purchase_price", "Price", "Stock Quantity", "GST %","SCH %"]
        form_layout = QVBoxLayout()
        
        for field in fields:
            label = QLabel(field)
            label.setFont(QFont("Arial", 14))
            label.setFixedWidth(280)
            entry = QLineEdit()
            entry.setFont(QFont("Arial", 14))
            entry.setStyleSheet("border-radius: 8px; padding: 5px; max-width: 200px;")     
            self.entries[field] = entry
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            row_layout.addWidget(label)
            row_layout.addWidget(entry)
            form_layout.addLayout(row_layout)
        
        main_layout.addLayout(form_layout)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        button_style = "font-size: 15px; padding: 6px 12px; max-width: 200px;"
        
        self.add_btn = QPushButton("Add Medicine")
        self.add_btn.setStyleSheet(f"background-color: green; color: white; {button_style}")
        self.add_btn.clicked.connect(self.add_medicine)

        self.update_btn = QPushButton("Update Medicine")
        self.update_btn.setStyleSheet(f"background-color: blue; color: white; {button_style}")
        self.update_btn.clicked.connect(self.update_medicine)

        self.delete_btn = QPushButton("Delete Medicine")
        self.delete_btn.setStyleSheet(f"background-color: red; color: white; {button_style}")
        self.delete_btn.clicked.connect(self.delete_medicine)

        self.clear_btn = QPushButton("Clear Fields")
        self.clear_btn.setStyleSheet(f"background-color: gray; color: white; {button_style}")
        self.clear_btn.clicked.connect(self.clear_fields)
        
        # Add Generate Bill button
        #self.bill_btn = QPushButton("Generate Bill")
        #self.bill_btn.setStyleSheet(f"background-color: purple; color: white; {button_style}")
        #self.bill_btn.clicked.connect(self.prepare_bill)
        #btn_layout.addWidget(self.bill_btn)

        # Add a text field for Customer Name (Initially Hidden)
        self.customer_name_entry = QLineEdit()
        self.customer_name_entry.setPlaceholderText("Enter Customer Name...")
        self.customer_name_entry.setFont(QFont("Arial", 14))
        self.customer_name_entry.hide()
        main_layout.addWidget(self.customer_name_entry)

        # Add a confirm button (Initially Hidden)
        self.confirm_bill_btn = QPushButton("Confirm Generate Bill")
        self.confirm_bill_btn.setStyleSheet(f"background-color: darkorange; color: white; {button_style}")
        self.confirm_bill_btn.clicked.connect(self.generate_bill)
        self.confirm_bill_btn.hide()
        main_layout.addWidget(self.confirm_bill_btn)


        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.billing_mode = False  # Add this line to track billing mode
        self.is_preparing_bill = False

        
        # Table Layout
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry","Purchase_price", "Price", "Stock", "GST","SCH","NET RATE"])
        self.table.cellClicked.connect(self.select_medicine)
        self.table.setStyleSheet("width: 100%;")
        
        # Make columns expand to take full width
        self.table.horizontalHeader().setStretchLastSection(True)  # Stretch last column
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch all columns

        # Remove unnecessary width restriction
        self.table.setStyleSheet("border: none;") 
        
                # Enable arrow key navigation between fields
        for entry in self.entries.values():
            entry.installEventFilter(self)

        
        main_layout.addWidget(self.table)
        self.load_medicines()
        
        # Main Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def add_medicine(self):
        #data = self.get_form_data()
        fields = ["Name", "Category", "Manufacturer", "Batch No", "Expiry Date (YYYY-MM-DD)", "purchase_price", "Price", "Stock Quantity", "GST %", "SCH %"]

        data = [self.entries[field].text() for field in fields]
        if data:
            self.inventory.add_medicine(*data)
            self.load_medicines()
            self.clear_fields()
    
    def update_medicine(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a medicine to update")
            return
        
        medicine_id = int(self.table.item(selected_row, 0).text())
        data = self.get_form_data()
        if data:
            self.inventory.update_medicine(medicine_id, *data)
            self.load_medicines()
            self.clear_fields()
    
    def delete_medicine(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a medicine to delete")
            return
        
        medicine_id = int(self.table.item(selected_row, 0).text())
        self.inventory.delete_medicine(medicine_id)
        self.load_medicines()
        self.clear_fields()
    
    
    def select_medicine(self, row, _):
        for i, field in enumerate(list(self.entries.keys())):
            self.entries[field].setText(self.table.item(row, i+1).text())
    
    def get_form_data(self):
        try:
            name = self.entries["Name"].text().strip()
            category = self.entries["Category"].text().strip()
            manufacturer = self.entries["Manufacturer"].text().strip()
            batch_no = self.entries["Batch No"].text().strip()
            expiry_date = self.entries["Expiry Date (YYYY-MM-DD)"].text().strip()
            purchase_price = float(self.entries["purchase_price"].text().strip())
            price = float(self.entries["Price"].text().strip())
            stock_quantity = int(self.entries["Stock Quantity"].text().strip())
            gst_percentage = float(self.entries["GST %"].text().strip())
            sch_percentage = float(self.entries["SCH %"].text().strip())
            
            if not all([name, category, manufacturer, batch_no, expiry_date]):
                raise ValueError("All fields must be filled!")
            
            return name, category, manufacturer, batch_no, expiry_date,purchase_price, price, stock_quantity, gst_percentage,sch_percentage
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            return None
    
    def clear_fields(self):
        for entry in self.entries.values():
            entry.clear()
            
    def eventFilter(self, source, event):
        if event.type() == event.Type.KeyPress:
            entries_list = list(self.entries.values())
            if source in entries_list:
                index = entries_list.index(source)
                if event.key() == Qt.Key.Key_Down and index < len(entries_list) - 1:
                    entries_list[index + 1].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up and index > 0:
                    entries_list[index - 1].setFocus()
                    return True
        return super().eventFilter(source, event) 
    
    def prepare_bill(self):
        if not self.is_preparing_bill:
            # Start Bill Preparation
            self.customer_name_entry.show()
            self.confirm_bill_btn.show()

            self.table.setColumnCount(11)
            self.table.setHorizontalHeaderLabels(
                ["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry", "Price", "Stock", "GST","SCH","NET RATE"]
            )
            self.load_medicines(with_checkbox=True)

            self.is_preparing_bill = True  # Now bill preparation mode is active

            # (Optional) Change button text
            self.bill_btn.setText("Cancel Bill")
        
        else:
            # Cancel Bill Preparation
            self.customer_name_entry.hide()
            self.confirm_bill_btn.hide()

            self.table.setColumnCount(11)
            self.table.setHorizontalHeaderLabels(
                ["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry", "Price", "Stock", "GST","SCH","NET RATE"]
            )
            self.load_medicines(with_checkbox=False)

            self.is_preparing_bill = False  # Exit bill preparation mode

            # (Optional) Change button text back
            self.bill_btn.setText("Generate Bill")


    def load_medicines(self, with_checkbox=False):
        self.table.setRowCount(0)
        medicines = self.inventory.fetch_all_medicines()
        today = date.today()

        query = """
            SELECT name, batch_no FROM medicines 
            WHERE expiry_date <= DATE_ADD(%s, INTERVAL 30 DAY)
        """
        self.cursor.execute(query, (today,))
        expiring_data = self.cursor.fetchall()
        expiring_set = set((name, batch_no) for name, batch_no in expiring_data)

        try:
            if with_checkbox:
                self.table.setColumnCount(12)
                self.table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry","purchase_price", "Price", "Stock", "GST","SCH","NET RATE"]
                )
            else:
                self.table.setColumnCount(12)
                self.table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry","purchase_price", "Price", "Stock", "GST","SCH","NET RATE"]
                )

            for medicine in medicines:
                row = self.table.rowCount()
                self.table.insertRow(row)

                if with_checkbox:
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    checkbox = QCheckBox()
                    label = QLabel(str(medicine[0]))
                    layout.addWidget(checkbox)
                    layout.addWidget(label)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(5)
                    self.table.setCellWidget(row, 0, widget)
                else:
                    item = QTableWidgetItem(str(medicine[0]))
                    self.table.setItem(row, 0, item)

                name = medicine[1]
                batch_no = medicine[4]
                is_expiring = (name, batch_no) in expiring_set
#stock = int(med[7]) if len(med) > 7 and med[7] else 1

                for col_num, value in enumerate(medicine[1:], start=1):
                    item = QTableWidgetItem(str(value))
                    if is_expiring:
                        item.setBackground(QColor("#FFCCCC"))
                    self.table.setItem(row, col_num, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load medicines: {str(e)}")

    
    def generate_bill(self):
        selected_medicines = []

        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)  # Get the widget in column 0 (ID + checkbox)
            if widget:
                checkbox = widget.findChild(QCheckBox)  # Find the checkbox
                label = widget.findChild(QLabel)  # Find the label (ID)

                if checkbox and checkbox.isChecked():
                    medicine_data = [label.text()]
                    for col in range(1, self.table.columnCount()):
                        item = self.table.item(row, col)
                        medicine_data.append(item.text() if item else "")
                    selected_medicines.append(medicine_data)

        if not selected_medicines:
            QMessageBox.warning(self, "No Selection", "Please select at least one medicine to generate bill!")
            return

        customer_name = self.customer_name_entry.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "Input Error", "Please enter the customer name!")
            return

        self.show_bill(customer_name, selected_medicines)

        # After bill generation, reset billing mode
        self.cancel_billing_mode()


    def show_bill(self, customer_name, medicines):
        bill_window = QDialog(self)
        bill_window.setWindowTitle(f"Bill for {customer_name}")
        bill_window.resize(900, 600)
  
        layout = QVBoxLayout()

        title = QLabel(f"Bill for {customer_name}")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        medicines_table = QTableWidget()
        medicines_table.setColumnCount(6)  # Adjust to 9 columns, as per the provided headers
        medicines_table.setHorizontalHeaderLabels([ "Name", "Category", "Expiry", "Price", "Stock", "GST"])
        medicines_table.horizontalHeader().setStretchLastSection(True)

        total_price = 0.0

        for row_num, med in enumerate(medicines):
            medicines_table.insertRow(row_num)

            # Check and handle missing values safely
            #stock = int(med[7]) if len(med) > 7 and med[7] else 1
            stock = int(float(med[7])) if len(med) > 7 and med[7] else 1# Stock corresponds to column 7
            price = float(med[6]) if len(med) > 6 and med[6] else 0.0
            gst = float(med[8]) if len(med) > 8 and med[8] else 0.0

            #medicines_table.setItem(row_num, 0, QTableWidgetItem(str(med[0])))  # ID
            medicines_table.setItem(row_num, 0, QTableWidgetItem(med[1]))  # Name
            medicines_table.setItem(row_num, 1, QTableWidgetItem(med[2]))  # Category
            #medicines_table.setItem(row_num, 3, QTableWidgetItem(med[3]))  # Manufacturer
            #medicines_table.setItem(row_num, 4, QTableWidgetItem(med[4]))  # Batch
            medicines_table.setItem(row_num, 2, QTableWidgetItem(med[5]))  # Expiry
            medicines_table.setItem(row_num, 3, QTableWidgetItem(f"{price:.2f}"))  # Price
            medicines_table.setItem(row_num, 4, QTableWidgetItem(str(stock)))  # Stock (Quantity)
            medicines_table.setItem(row_num, 5, QTableWidgetItem(f"{gst:.2f}"))  # GST

            # Calculate total
            total_price += (price + (price * gst / 100)) * stock

        layout.addWidget(medicines_table)

        total_label = QLabel(f"Total Amount: ₹{total_price:.2f}")
        total_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(total_label)

        # Add a button to export the bill to a PDF
        export_button = QPushButton("Export Bill as PDF")
        export_button.clicked.connect(lambda: self.export_bill_as_pdf(customer_name, medicines, total_price))
        layout.addWidget(export_button)

        bill_window.setLayout(layout)
        bill_window.exec()

    def export_bill_as_pdf(self, customer_name, medicines, total_amount):

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
        pdf.cell(0, 10, f"Customer: {customer_name}", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 10, "Name", 1)
        pdf.cell(30, 10, "Category", 1)
        pdf.cell(20, 10, "Expiry", 1)
        pdf.cell(20, 10, "Price", 1)
        pdf.cell(20, 10, "Stock", 1)
        pdf.cell(20, 10, "GST%", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 12)
        for med in medicines:
            pdf.cell(30, 10, med[1], 1)
            pdf.cell(30, 10, med[2], 1)    
            pdf.cell(20, 10, med[5], 1)
            pdf.cell(20, 10, f"{float(med[6]):.2f}", 1)
            pdf.cell(20, 10, str(med[7]), 1)
            pdf.cell(20, 10, f"{float(med[8]):.2f}", 1)
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Total Amount: Rs. {total_amount:.2f}", ln=True)

        # Save PDF
        base_path = os.path.dirname(os.path.abspath(__file__))
        bills_folder = os.path.join(base_path, 'b2b bill')
        if not os.path.exists(bills_folder):
            os.makedirs(bills_folder)

        filename = f"Bill_{customer_name.replace(' ', '_')}.pdf"
        save_path = os.path.join(bills_folder, filename)
        pdf.output(save_path)

        # Show enhanced QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("✅ Bill Exported")
        msg_box.setText("Bill exported successfully!")
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
                        app_password = "zrtr smiw bfvd droc"  # Use Gmail App Password

                        msg = EmailMessage()
                        msg['Subject'] = f'Bill for {customer_name}'
                        msg['From'] = sender_email
                        msg['To'] = receiver_email.strip()
                        msg.set_content(f"Dear {customer_name},\n\nPlease find the attached bill.\n\nRegards,\nSiddhanath Medical")

                        with open(save_path, 'rb') as f:
                            file_data = f.read()
                            file_type, _ = mimetypes.guess_type(save_path)
                            main_type, sub_type = file_type.split('/', 1)
                            msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(save_path))

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender_email, app_password)
                            smtp.send_message(msg)

                        QMessageBox.information(self, "Email Sent", "📤 Bill shared successfully via email!")

                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"❌ Failed to send email:\n{str(e)}")
                else:
                    QMessageBox.warning(self, "Cancelled", "📧 Email sending cancelled or invalid email entered.")
            else:
                QMessageBox.critical(self, "Error", f"❌ File not found:\n{save_path}")

    
    def cancel_billing_mode(self):
        self.billing_mode = False
        self.customer_name_entry.hide()
        self.confirm_bill_btn.hide()
        self.load_medicines(with_checkbox=False)  # Reload medicines normally without checkboxes



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryUI()
    window.show()
    sys.exit(app.exec())



# pdf.cell(0, 10, f"Total Amount: Rs. {total_amount}", ln=True)  select





