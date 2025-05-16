import sys
import os
import subprocess
import mysql.connector
import traceback  
from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from datetime import datetime, date
from PyQt6.QtGui import QPixmap  

# ✅ Import database connection function
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db  
#from stock_alert import StockAlert
from ui.stock_alert import StockAlert

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        # ✅ Establish MySQL connection
        self.conn = connect_db()  
        if not self.conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to MySQL! Exiting...")
            sys.exit(1)  # ❌ Exit app if DB connection fails
        self.cursor = self.conn.cursor()
        print("✅ Connected to MySQL!")
        
        self.entries = {}

        # ✅ Set up the window
        self.setWindowTitle("Medical Shop Inventory Management")
        self.setGeometry(100, 100, 1000, 600)
        
        # ✅ Set absolute icon path
        #icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/icon.ico"))
        #if os.path.exists(icon_path):
            #self.setWindowIcon(QIcon(icon_path))
        #else:
            #print("⚠ Warning: Icon not found at", icon_path)

        #self.setStyleSheet("background-color: #f8f9fa;")

        # ✅ Main Widget and Layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        

        # ✅ Title Label
        title = QLabel("Medical Shop Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #343a40; padding: 10px;")
        main_layout.addWidget(title)

        # ✅ Navigation Buttons
        button_layout = QHBoxLayout()

        self.dashboard_btn = QPushButton("Dashboard")
        self.inventory_btn = QPushButton("Inventory Management")
        self.billing_btn = QPushButton("Billing & Sales")
        self.reports_btn = QPushButton("Reports & Analysis")
        self.pdf_btn = QPushButton("Storage Reports")

        for btn in [self.dashboard_btn, self.inventory_btn, self.billing_btn, self.reports_btn,self.pdf_btn]:
            btn.setFixedSize(250, 50)
            btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007BFF; 
                    color: white; 
                    border-radius: 8px;
                    border: none; 
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)

        # ✅ Expiry Alert Section
        alert_label = QLabel("\n⚠ Expiry Date Alerts:")
        alert_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        alert_label.setStyleSheet("color: red;")
        main_layout.addWidget(alert_label)
        
        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(3)
        self.expiry_table.setHorizontalHeaderLabels(["Medicine Name", "Batch No", "Expiry Date"])
        self.expiry_table.setStyleSheet("font-size: 14px; background-color: white; border-radius: 5px;")
        
        # ✅ Set column width and styling
        self.expiry_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.expiry_table.horizontalHeader().setStyleSheet("font-size: 16px; font-weight: bold; color: #212529; background-color: #e9ecef;")
        self.expiry_table.verticalHeader().setDefaultSectionSize(30)
        
        self.load_expiry_alerts()
        main_layout.addWidget(self.expiry_table)

        # ✅ Connect buttons to open respective windows
        self.inventory_btn.clicked.connect(self.open_inventory)
        self.billing_btn.clicked.connect(self.open_billing)
        self.reports_btn.clicked.connect(self.open_report)
        self.pdf_btn.clicked.connect(self.open_pdf)

    def open_inventory(self):
        """Opens the Inventory Management UI."""
        try:
            from ui.inventory_ui import InventoryUI  
            self.inventory_window = InventoryUI()
            self.inventory_window.showMaximized()
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Inventory UI file not found!\n{str(e)}")
            traceback.print_exc()
            
    def open_billing(self):
        """Opens the Billing & Sales UI."""
        try:
            from ui.billing_ui import BillingUI  
            self.billing_window = BillingUI()
            self.billing_window.showMaximized()
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Billing UI file not found!\n{str(e)}")
            traceback.print_exc()
            
    
    def open_report(self):
        """Opens the Billing & Sales UI."""
        try:
            from ui.report_ui import ReportUI  
            self.report_window = ReportUI()
            self.report_window.showMaximized()
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"report UI file not found!\n{str(e)}")
            traceback.print_exc()
    
    def open_pdf(self):
        """Opens the Billing & Sales UI."""
        try:
            from pdf import  FileViewer
            self.report_window = FileViewer()
            self.report_window.showMaximized()
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"report UI file not found!\n{str(e)}")
            traceback.print_exc()
    
    def load_expiry_alerts(self):
        """Loads Expiry Alerts from MySQL Database"""
        if not self.cursor:
            print("❌ Cannot load expiry alerts: No database connection.")
            return
        
        try:
            today = date.today()
            query = """
            SELECT name, batch_no, expiry_date FROM medicines 
            WHERE expiry_date <= DATE_ADD(%s, INTERVAL 30 DAY) 
            ORDER BY expiry_date ASC
            """
            self.cursor.execute(query, (today,))
            expiry_data = self.cursor.fetchall()

            self.expiry_table.setRowCount(len(expiry_data))  
            for row, (name, batch, expiry_date) in enumerate(expiry_data):
                self.expiry_table.setItem(row, 0, QTableWidgetItem(name))
                self.expiry_table.setItem(row, 1, QTableWidgetItem(batch))
                self.expiry_table.setItem(row, 2, QTableWidgetItem(str(expiry_date)))

            expired_medicines = [f"{name} (Batch: {batch}, Expiry: {expiry_date})" for name, batch, expiry_date in expiry_data if expiry_date < today]
            if expired_medicines:
                self.show_expiry_alert(expired_medicines)

        except mysql.connector.Error as e:
            print(f"❌ Error fetching expiry alerts: {e}")

    def show_expiry_alert(self, expired_medicines):
        """Show an alert for expired medicines"""
        alert_message = "The following medicines are expired:\n\n" + "\n".join(expired_medicines)
        QMessageBox.warning(self, "Expiry Alert", alert_message)

    def closeEvent(self, event):
        """Close DB connection when window is closed"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.showMaximized()
    sys.exit(app.exec())

