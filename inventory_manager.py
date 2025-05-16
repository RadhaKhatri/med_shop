import mysql.connector
from mysql.connector import Error
from datetime import datetime
from db import connect_db  # ✅ Import the correct function

class InventoryManager:
    def __init__(self):
        self.conn = connect_db()  # ✅ Use connect_db() to establish a connection
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None
            print("❌ Database connection failed.")

    def add_medicine(self, name, category, manufacturer, batch_no, expiry_date,purchase_price , price, stock_quantity, gst_percentage, scheme_discount):
        if not self.cursor:
            print("❌ Cannot add medicine: No database connection.")
            return  
        
        query = """
        INSERT INTO medicines (name, category, manufacturer, batch_no, expiry_date,purchase_price, price, stock_quantity, gst_percentage,scheme_discount )
        VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s,%s)
        """
        values = (name, category, manufacturer, batch_no, expiry_date,purchase_price, price, stock_quantity, gst_percentage,scheme_discount )
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print("✅ Medicine added successfully.")
        except Error as e:
            print(f"❌ Error adding medicine: {e}")

    def fetch_all_medicines(self):
        if not self.cursor:
            print("❌ Cannot fetch medicines: No database connection.")
            return []
        
        query = """SELECT medicine_id, name, category, manufacturer, batch_no, expiry_date, 
               purchase_price, price, stock_quantity, gst_percentage, 
               scheme_discount, net_rate 
            FROM medicines"""
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ Error fetching medicines: {e}")
            return []

    def update_medicine(self, medicine_id, name, category, manufacturer, batch_no, expiry_date,purchase_price, price, stock_quantity, gst_percentage,scheme_discount):
        if not self.cursor:
            print("❌ Cannot update medicine: No database connection.")
            return

        query = """
        UPDATE medicines
        SET name=%s, category=%s, manufacturer=%s, batch_no=%s, expiry_date=%s,purchase_price=%s, price=%s, stock_quantity=%s, gst_percentage=%s, scheme_discount=%s
        WHERE medicine_id=%s
        """
        values = (name, category, manufacturer, batch_no, expiry_date,purchase_price, price, stock_quantity, gst_percentage,scheme_discount, medicine_id)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print("✅ Medicine updated successfully.")
        except Error as e:
            print(f"❌ Error updating medicine: {e}")

    def delete_medicine(self, medicine_id):
        if not self.cursor:
            print("❌ Cannot delete medicine: No database connection.")
            return
        
        try:
            # Step 1: Delete sales related to this medicine
            delete_sales_query = "DELETE FROM sales WHERE medicine_id = %s"
            self.cursor.execute(delete_sales_query, (medicine_id,))

            # Step 2: Delete the medicine   
            delete_medicine_query = "DELETE FROM medicines WHERE medicine_id = %s"
            self.cursor.execute(delete_medicine_query, (medicine_id,))

            self.conn.commit()
            print("✅ Medicine and related sales deleted successfully.")

        except Error as e:
            print(f"❌ Error deleting medicine: {e}")


    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed.")

# Example usage
if __name__ == "__main__":
    inventory = InventoryManager()
    
    # Adding a test medicine
    inventory.add_medicine("Paracetamol", "Painkiller", "ABC Pharma", "B123", "2025-12-31", 50.00, 100, 5.00, 10.00)
    
    # Fetch and print medicines
    medicines = inventory.fetch_all_medicines()
    for medicine in medicines:
        print(medicine)
    
    # Update a medicine
    inventory.update_medicine(1, "Paracetamol", "Painkiller", "XYZ Pharma", "B123", "2026-01-01", 55.00, 90, 5.00, 10.00)
    
    # Delete a medicine
    inventory.delete_medicine(1)
    
    # Close connection properly
    inventory.close()
