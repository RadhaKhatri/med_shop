import subprocess
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFormLayout, QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox,QCheckBox, QCompleter
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt


import pdfkit
from PyQt6.QtWidgets import QComboBox

#sys.path.append(r"D:\TY\miniproject\medical_shop\venv\Lib\site-packages")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # = .../medical_shop/ui
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

wkhtmltopdf_path = os.path.join(ROOT_DIR, "ui", "wkhtmltopdf", "bin", "wkhtmltopdf.exe")
pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
from billing import BillingSystem

import smtplib
from email.message import EmailMessage
import mimetypes

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db 
from billing import calculate_item_totals 

class BillingUI(QMainWindow):
    def __init__(self):
        super().__init__()   
        self.entries = {}
        
        self.conn = connect_db()  
        if not self.conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to MySQL! Exiting...")
            sys.exit(1)  # ❌ Exit app if DB connection fails
        self.cursor = self.conn.cursor()
        print("✅ Connected to MySQL!")

        self.setWindowTitle("Billing & Sales")
        self.setGeometry(200, 100, 800, 500)
        self.billing_system = BillingSystem()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.heading = QLabel("Generate Bill")
        self.heading.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.main_layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form_layout = QVBoxLayout()

        # Sale Type Label
        label_type = QLabel("Sale Type")
        label_type.setFont(QFont("Arial", 14))
        label_type.setFixedWidth(120)

        # Pack checkbox and input
        self.pack_checkbox = QCheckBox("Pack")
        self.pack_checkbox.setFont(QFont("Arial", 14))

        pack_entry = QLineEdit()
        pack_entry.setFont(QFont("Arial", 14))
        pack_entry.setPlaceholderText("Enter Pack (optional)")
        pack_entry.setFixedWidth(180)
        pack_entry.setStyleSheet("border-radius: 8px; padding: 5px;")

        # Strip checkbox and input
        self.strip_checkbox = QCheckBox("Strip")
        self.strip_checkbox.setFont(QFont("Arial", 14))

        strip_entry = QLineEdit()
        strip_entry.setFont(QFont("Arial", 14))
        strip_entry.setPlaceholderText("Enter Strip (optional)")
        strip_entry.setFixedWidth(180)
        strip_entry.setStyleSheet("border-radius: 8px; padding: 5px;")

        # Store in entries
        self.entries["Pack"] = pack_entry
        self.entries["Strip"] = strip_entry

        # Horizontal layout for Pack row
        pack_row = QHBoxLayout()
        pack_row.addSpacing(10)
        pack_row.addWidget(self.pack_checkbox)
        pack_row.addSpacing(10)
        pack_row.addWidget(pack_entry)
        pack_row.addStretch()

        # Horizontal layout for Strip row
        strip_row = QHBoxLayout()
        strip_row.addSpacing(10)
        strip_row.addWidget(self.strip_checkbox)
        strip_row.addSpacing(10)
        strip_row.addWidget(strip_entry)
        strip_row.addStretch()

        # Vertical layout combining Pack and Strip rows
        sale_type_fields_layout = QVBoxLayout()
        sale_type_fields_layout.setSpacing(10)
        sale_type_fields_layout.addLayout(pack_row)
        sale_type_fields_layout.addLayout(strip_row)

        # Wrap it in a widget for alignment control
        sale_type_fields_widget = QWidget()
        sale_type_fields_widget.setLayout(sale_type_fields_layout)

        # Final layout with label and fields
        sale_type_layout = QHBoxLayout()
        sale_type_layout.addWidget(label_type, alignment=Qt.AlignmentFlag.AlignTop)
        sale_type_layout.addWidget(sale_type_fields_widget)

        # Add to form layout
        form_layout.addLayout(sale_type_layout)

         # Fields
        customer_fields = ["Customer Name", "Medicine ID", "Medicine Name","Packet Size"]
        

        for field in customer_fields:
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
            
        # Discount %
        label_discount = QLabel("Discount %")
        label_discount.setFont(QFont("Arial", 14))
        label_discount.setFixedWidth(280)

        discount_entry = QLineEdit()
        discount_entry.setFont(QFont("Arial", 14))
        discount_entry.setStyleSheet("border-radius: 8px; padding: 5px; max-width: 200px;")
        discount_entry.setPlaceholderText("Enter Discount (optional)")
        self.entries["Discount"] = discount_entry

        discount_layout = QHBoxLayout()
        discount_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        discount_layout.addWidget(label_discount)
        discount_layout.addWidget(discount_entry)
        form_layout.addLayout(discount_layout)
        
        # Doctor info on the right side
        doctor_layout = QVBoxLayout()
        doctor_fields = ["Doctor Name", "Mobile No.", "Address"]
        for field in doctor_fields:
            label = QLabel(field)
            label.setFont(QFont("Arial", 14))
            label.setFixedWidth(150)
            entry = QLineEdit()
            entry.setFont(QFont("Arial", 14))
            entry.setStyleSheet("border-radius: 8px; padding: 5px; max-width: 250px;")
            if field == "Address":
                entry.setPlaceholderText("Enter full address")
                entry.setMinimumHeight(40)
            self.entries[field] = entry
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignmentFlag.AlignLeft)
            row.addWidget(label)
            row.addWidget(entry)
            doctor_layout.addLayout(row)

        # Combine form and doctor layouts horizontally
        form_container_layout = QHBoxLayout()
        form_container_layout.addLayout(form_layout)
        form_container_layout.addSpacing(20)
        form_container_layout.addLayout(doctor_layout)

        # Add combined layout to main
        self.main_layout.addLayout(form_container_layout)


        # Autocomplete setup for medicine name with ID
        raw_medicines = self.billing_system.get_medicine_names()
        display_medicines = [f"{med_id} - {med_name}" for med_id, med_name in raw_medicines]

        completer = QCompleter()
        completer.setModel(QStringListModel(display_medicines))
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)  # ✅ Match anywhere in string
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)  # ✅ Show dropdown while typing

        self.entries["Medicine Name"].setCompleter(completer)

        self.main_layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        button_style = "font-size: 15px; padding: 6px 12px; max-width: 200px;"

        self.add_btn = QPushButton("Add Item")
        self.add_btn.setStyleSheet(f"background-color: green; color: white; {button_style}")
        self.add_btn.clicked.connect(self.add_item)
        btn_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(btn_layout)
  
        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Medicine", "Quantity", "Price", "GST%", "Discount%", "Net Rate", "Subtotal", "Delete",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.main_layout.addWidget(self.table)

       # Button Style (you can customize this as needed)
        button_style = "font-size: 15px; padding: 6px 12px; max-width: 200px;"

        # Finalize Bill Button
        self.final_bill_button = QPushButton("Finalize Bill")
        self.final_bill_button.setStyleSheet(f"background-color: blue; color: white; {button_style}")
        self.final_bill_button.clicked.connect(self.finalize_bill)

        # Generate Invoice Button
        self.generate_invoice_button = QPushButton("Generate Invoice")
        self.generate_invoice_button.setStyleSheet(f"background-color: blue; color: white; {button_style}")
        self.generate_invoice_button.clicked.connect(self.generate_invoice)

        # Button Layout (horizontal)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.final_bill_button)
        button_layout.addWidget(self.generate_invoice_button)

        # Add to main layout
        self.main_layout.addLayout(button_layout)


        # GST and Total Labels     
        self.gst_label = QLabel("Total GST: ₹0.00")
        self.total_label = QLabel("Total: ₹0.00")
        self.gst_label.setFont(QFont("Arial", 14))
        self.total_label.setFont(QFont("Arial", 14))
        self.main_layout.addWidget(self.gst_label)
        self.main_layout.addWidget(self.total_label)

        self.central_widget.setLayout(self.main_layout)
        self.items = []

        for entry in self.entries.values():
            entry.installEventFilter(self)

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

    def add_item(self):
        customer_name = self.entries["Customer Name"].text().strip()
        doctor_name = self.entries["Doctor Name"].text().strip()
        mobile_no = self.entries["Mobile No."].text().strip()
        address = self.entries["Address"].text().strip()

        medicine_id = self.entries["Medicine ID"].text().strip()
        medicine_name = self.entries["Medicine Name"].text().strip()
        pack_text = self.entries["Pack"].text().strip()
        strip_text = self.entries["Strip"].text().strip()

        # Validate at least pack or strip
        pack_qty = int(pack_text) if pack_text.isdigit() else 0
        strip_qty = int(strip_text) if strip_text.isdigit() else 0
        if pack_qty == 0 and strip_qty == 0:
            QMessageBox.critical(self, "Error", "Enter at least Pack or Strip quantity.")
            return

        # Validate packet size
        packet_size_text = self.entries["Packet Size"].text().strip()
        if not packet_size_text.isdigit() or int(packet_size_text) == 0:
            QMessageBox.critical(self, "Error", "Packet Size must be a non-zero number.")
            return
        packet_size = int(packet_size_text)

        quantity = (pack_qty * packet_size) + strip_qty

        # Fetch medicine
        medicine = None
        if medicine_id:
            medicine = self.billing_system.fetch_medicine(medicine_id)
        elif medicine_name and " - " in medicine_name:
            med_id = medicine_name.split(" - ", 1)[0].strip()
            medicine = self.billing_system.fetch_medicine(med_id)
        else:
            QMessageBox.critical(self, "Error", "Provide valid Medicine ID or Name.")
            return

        if not medicine:
            QMessageBox.critical(self, "Error", "Medicine not found.")
            return

        med_id, name, price, net_rate_db, gst = medicine
        price = float(price)
        gst = float(gst)

        # Discount
        discount_text = self.entries["Discount"].text().strip()
        discount = float(discount_text) if discount_text and discount_text.replace('.', '', 1).isdigit() else 0.0

        # Determine sale type
        sale_type = ""
        if self.pack_checkbox.isChecked() and self.strip_checkbox.isChecked():
            sale_type = "Both"
        elif self.pack_checkbox.isChecked():
            sale_type = "Pack"
        elif self.strip_checkbox.isChecked():
            sale_type = "Strip"

        if sale_type == "Strip":
            price = price / packet_size  # Adjust price per strip

        # Calculate billing
        gross, discount_amount, net_after_discount, gst_amount, subtotal, net_rate = calculate_item_totals(
            price, quantity, discount, gst
        )

        # Insert row into table
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(name))
        self.table.setItem(row_count, 1, QTableWidgetItem(str(quantity)))
        self.table.setItem(row_count, 2, QTableWidgetItem(f"{price:.2f}"))
        self.table.setItem(row_count, 3, QTableWidgetItem(f"{gst:.2f}%"))
        self.table.setItem(row_count, 4, QTableWidgetItem(f"{discount:.2f}%"))
        self.table.setItem(row_count, 5, QTableWidgetItem(f"{net_rate:.2f}"))
        self.table.setItem(row_count, 6, QTableWidgetItem(f"{subtotal:.2f}"))

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: red; color: white; font-size: 12px;")
        delete_button.clicked.connect(lambda checked, row=row_count: self.delete_item(row))
        self.table.setCellWidget(row_count, 7, delete_button)

        # Store item
        self.items.append({
            "customer_name": customer_name,
            "doctor_name": doctor_name,
            "mobile_no": mobile_no,
            "address": address,
            "medicine_id": med_id,
            "name": name,
            "quantity": quantity,
            "strip_qty": strip_qty,
            "pack_qty": pack_qty,
            "rate": price,
            "discount": discount,
            "gst": gst,
            "subtotal": subtotal,
            "sale_type": sale_type
        })

        self.recalculate_totals()

    def recalculate_totals(self):
        total_gst = 0.0
        total_price = 0.0

        for row in range(self.table.rowCount()):
            quantity_item = self.table.item(row, 1)
            price_item = self.table.item(row, 2)
            gst_item = self.table.item(row, 3)
            discount_item = self.table.item(row, 4)

            quantity = int(quantity_item.text()) if quantity_item else 0
            price = float(price_item.text()) if price_item else 0.0
            gst = float(gst_item.text().replace('%', '')) if gst_item else 0.0
            discount = float(discount_item.text().replace('%', '')) if discount_item else 0.0

            _, _, net_after_discount, gst_amount, _, _ = calculate_item_totals(price, quantity, discount, gst)

            total_gst += gst_amount
            total_price += net_after_discount + gst_amount

        self.total_gst = round(total_gst, 2)
        self.total_price = round(total_price, 2)

        self.gst_label.setText(f"Total GST: ₹{self.total_gst:.2f}")
        self.total_label.setText(f"Total: ₹{self.total_price:.2f}")
 
    def delete_item(self, row):  
        self.table.removeRow(row)
        self.items.pop(row)
        self.recalculate_totals()
        
    def finalize_bill(self):
        if not self.items:
            QMessageBox.critical(self, "Error", "No items to finalize!")
            return

        try:
            for item in self.items:
                name = item['name']
                rate = item['rate']
                gst = item['gst']
                discount = item['discount']
                subtotal = item['subtotal']
                quantity = item.get('quantity', 0)

                # Recalculate values needed for DB update
                net_without_gst = subtotal / (1 + gst / 100)
                gst_amount = subtotal - net_without_gst

                item['total_price'] = subtotal
                item['gst_amount'] = gst_amount
                item['total_qty'] = quantity

                medicine_id = item['medicine_id']
                sold_quantity = item['total_qty']
                total_price = item['total_price']
                gst_amount = item['gst_amount']

                # Update stock
                self.cursor.execute("SELECT stock_quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
                result = self.cursor.fetchone()
                if result:
                    current_stock = result[0]
                    new_stock = current_stock - sold_quantity

                    self.cursor.execute(
                        "UPDATE medicines SET stock_quantity = %s WHERE medicine_id = %s",
                        (new_stock, medicine_id)
                    )

                    # Insert sales record
                    self.cursor.execute(
                        "INSERT INTO sales (medicine_id, quantity, total_price, gst_amount) VALUES (%s, %s, %s, %s)",
                        (medicine_id, sold_quantity, total_price, gst_amount)
                    )

            self.conn.commit()
            QMessageBox.information(self, "✅ Finalized", "Bill finalized and stock updated successfully!")
            self.reset_form()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def generate_invoice(self):
        customer_name = self.entries["Customer Name"].text().strip()
        doctor_name = self.entries["Doctor Name"].text().strip()
        mobile_no = self.entries["Mobile No."].text().strip()
        address = self.entries["Address"].text().strip()

        if not customer_name or not self.items:
            QMessageBox.critical(self, "Error", "Customer name and at least one item are required!")
            return

        try:
            #pdfkit_config = pdfkit.configuration(wkhtmltopdf="D:/Mydownlod/wkhtmltopdf/bin/wkhtmltopdf.exe")
            
            items_html = ""
            total_gst = 0.0
            total_without_gst = 0.0
            grand_total = 0.0

            for item in self.items:
                name = item['name']
                rate = item['rate']
                gst = item['gst']
                discount = item['discount']
                subtotal = item['subtotal']
                pack_qty = item.get('pack_qty', 0)
                strip_qty = item.get('strip_qty', 0)
                quantity = item.get('quantity', 0)

                # Calculate net without GST and GST amount
                net_without_gst = subtotal / (1 + gst / 100)
                gst_amount = subtotal - net_without_gst

                # Update the item dictionary to be used later in finalize_bill
                item['total_qty'] = quantity
                item['gst_amount'] = gst_amount
                item['total_price'] = subtotal

                items_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{strip_qty}</td>
                    <td>{pack_qty}</td>
                    <td>{rate:.2f}</td>
                    <td>{discount:.2f}%</td>
                    <td>{gst:.2f}%</td>
                    <td>{net_without_gst:.2f}</td>
                    <td>{subtotal:.2f}</td>
                </tr>
                """

                total_gst += gst_amount
                total_without_gst += net_without_gst
                grand_total += subtotal

            from datetime import datetime
            current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

            html = f"""<html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
                    h1, h2, h3 {{ text-align: center; }}
                    .totals-table {{
                        margin-top: 30px;
                        margin-left: auto;
                        font-family: Arial, sans-serif;
                        border-collapse: collapse;
                        border: none;
                        width: auto;
                        font-size: 16px;
                    }}
                    .totals-table td {{
                        padding: 4px 8px;
                        text-align: right;
                        border: none;
                        font-size: 16px;
                    }}
                    .totals-table td.label {{
                        text-align: left;
                        font-weight: bold;
                        white-space: nowrap;
                    }}
                    .footer-signature {{
                        margin-top: 60px;
                        display: flex;
                        justify-content: space-between;
                        font-size: 14px;
                        padding: 0 20px;
                    }}
                    .footer-signature div {{
                        text-align: center;
                        width: 40%;
                    }}
                    .details {{
                        font-size: 14px;
                        line-height: 1.6;
                    }}
                </style>
            </head>
            <body>
                <h1>Siddhanath Medical Ramanandnagar</h1>
                <h3>
                    shop no 6, Ground floor, Property no 89, Bhagatsingh Chowk, kirloskarwadi, Ramanandnagar.<br>
                    Tal- Palus (sangli) | Pin: 416308<br>
                    Email: aniketgejage12345@gmail.com | Contact: 9766019199<br>
                    Reg No: MH-SAN-458563 / MH-SAN-458564
                </h3>
                <h2>Invoice</h2>
                <div class="details">
                    <p><strong>Patient  Name:</strong> {customer_name}</p>
                    <p><strong>Doctor Name:</strong> {doctor_name}</p>
                    <p><strong>Mobile No:</strong> {mobile_no}</p>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Date & Time:</strong> {current_time}</p>
                </div>

                <table>
                    <tr>
                        <th>Medicine</th>
                        <th>Strip</th>
                        <th>Pack</th>
                        <th>Rate</th>
                        <th>Discount</th>
                        <th>GST</th>
                        <th>Price w/o GST</th>
                        <th>Total</th>
                    </tr>
                    {items_html}
                </table>

                <table class="totals-table">
                    <tr>
                        <td class="label">Total w/o GST:</td>
                        <td>Rs. {total_without_gst:.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Total GST:</td>
                        <td>Rs. {total_gst:.2f}</td>
                    </tr>
                    <tr>
                        <td class="label"><strong>Final Total:</strong></td>
                        <td><strong>Rs. {grand_total:.2f}</strong></td>
                    </tr>
                </table>

                <div class="footer-signature">
                    <div>
                        <br><br>______________________<br>
                        Signature
                    </div>
                </div>
            </body>
            </html>
            """
            # Save PDF
            #invoice_path = r"D:\TY\miniproject\medical_shop\invoices"
            invoice_path = os.path.join(BASE_DIR, "invoices")

            os.makedirs(invoice_path, exist_ok=True)
            filename = f"Bill_{customer_name.replace(' ', '_')}.pdf"
            save_path = os.path.join(invoice_path, filename)
            pdfkit.from_string(html, save_path, configuration=pdfkit_config)

            # Show custom QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("✅ Invoice Generated")
            msg_box.setText("Invoice generated successfully!")
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
                            app_password = "zrtr smiw bfvd droc"

                            msg = EmailMessage()
                            msg['Subject'] = f'Invoice for {customer_name}'
                            msg['From'] = sender_email
                            msg['To'] = receiver_email.strip()
                            msg.set_content(f"Dear {customer_name},\n\nPlease find the attached invoice.\n\nRegards,\nMedical Shop")

                            with open(save_path, 'rb') as f:
                                file_data = f.read()
                                file_type, _ = mimetypes.guess_type(save_path)
                                main_type, sub_type = file_type.split('/', 1)
                                msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(save_path))

                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                smtp.login(sender_email, app_password)
                                smtp.send_message(msg)

                            QMessageBox.information(self, "Email Sent", "📤 Invoice shared successfully via email!")
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"❌ Failed to send email:\n{str(e)}")
                    else:
                        QMessageBox.warning(self, "Cancelled", "📧 Email sending cancelled or invalid email entered.")
                else:
                    QMessageBox.critical(self, "Error", f"❌ File not found:\n{save_path}")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Unexpected error:\n{str(e)}")

    
    def reset_form(self):
        """Reset the form to its initial state after invoice generation."""

        # Clear all input fields
        for field in self.entries.values():
            field.clear()
            field.setEnabled(True)

        # Re-enable input controls and buttons
        self.add_btn.setEnabled(True)

        # Clear the invoice table
        self.table.clearContents()
        self.table.setRowCount(0)

        # Clear the item list
        self.items.clear()

        # Optionally reset focus to Customer Name or another logical first field
        self.entries["Customer Name"].setFocus()


