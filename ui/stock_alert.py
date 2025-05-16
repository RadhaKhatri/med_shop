from PyQt6.QtWidgets import QMessageBox
import mysql.connector

class StockAlert:
    def __init__(self, conn):
        """Initialize with database connection"""
        self.conn = conn
        self.cursor = conn.cursor() if conn else None

    def check_low_stock(self):
        """Check medicines with low stock and show alert"""
        if not self.cursor:
            print("❌ Cannot check stock alerts: No database connection.")
            return

        try:
            # ✅ Query to get medicines where stock is ≤ 10
            query = "SELECT name, batch_no, stock FROM medicines WHERE stock <= 10 ORDER BY stock ASC"
            self.cursor.execute(query)
            low_stock_items = self.cursor.fetchall()

            if not low_stock_items:
                QMessageBox.information(None, "Stock Alert", "✅ All stock levels are sufficient.")
                return

            # ✅ Create alert message
            #alert_message = "⚠ The following medicines are low in stock:\n\n"
            #for name, batch, stock in low_stock_items:
            #    alert_message += f"{name} (Batch: {batch}) - Stock: {stock}\n"

            #QMessageBox.warning(None, "⚠ Low Stock Alert", alert_message)

        except mysql.connector.Error as e:
            print(f"❌ Error fetching stock alerts: {e}")
