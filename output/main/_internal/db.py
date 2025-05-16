import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Radha@1474",
            database="medical_shop"
        )
        if conn.is_connected():
            print("✅ Connected to MySQL Database!")
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        return None

# Test Connection
if __name__ == "__main__":
    db_connection = connect_db()
    if db_connection:
        db_connection.close()

