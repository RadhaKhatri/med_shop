# 🏥 Automated Medical Billing System

The **Automated Medical Billing System** is a desktop application built using **Python** and **PyQt6**, designed to streamline medical shop operations such as inventory management, billing, report generation, and vendor tracking. It also integrates with email to automatically fetch purchase invoices in PDF format. This project is ideal for standalone medical stores looking to digitize their day-to-day operations.

---

## 📁 Project Structure


medical_shop/
│── main.py   # Entry point of the application( This file will start the application and open the dashboard.) 

│── auth.py      

│── db.py                  # Database connection file	

│── inventory_manager.py           # Inventory Management (CRUD)

│── billing.py             # Billing & Sales Management

│── reports.py             # Sales & GST Reports

│── email_fetch.py         # Fetch PDFs from Email

│── ui/	

│   │── dashboard.py       # Dashboard UI (This file will contain the main window of the app. )

│   │── inventory_ui.py    # Inventory UI

│   │── billing_ui.py      # Billing UI

│   │── reports_ui.py      # Reports UI

│── assets/

│   │── icon.ico           # App icon

│   │── logo.png           # App logo

│── requirements.txt       # List of required libraries

└── README.md              # Project documentation




---

## 🛠️ Features

- 📦 Inventory management with expiry alerts
- 🧾 Billing & sales with GST calculation
- 📊 Sales, GST, and stock reports
- 📨 Automatic PDF fetch from email (invoice attachments)
- 🧾 Vendor and purchase tracking
- 🔐 User authentication system
- 📤 One-click deployment to `.exe`
- 🧑‍💻 MySQL-based secure backend

---

## 🧭 Development Roadmap

### ✅ Phase 1: Database Setup
- MySQL DB creation (`db.py`)
- Connection established using `mysql-connector-python`

### ✅ Phase 2: UI with PyQt6
- Main window with navigation (`dashboard.py`)

### ✅ Phase 3: Inventory Management
- CRUD operations for medicines (`inventory_manager.py`)
- UI: Add, update, and delete medicines (`inventory_ui.py`)

### ✅ Phase 4: Billing System
- Invoice generation with tax logic (`billing.py`)
- User-friendly billing UI (`billing_ui.py`)

### ✅ Phase 5: Reporting
- Sales and GST reports (`reports.py`)
- Integrated into reporting UI (`reports_ui.py`)

### ✅ Phase 6: Email Integration
- Fetch PDF attachments from inbox (`email_fetch.py`)

### ✅ Phase 7: Testing & Deployment
- Final testing
- Create `.exe` for Windows deployment
- MySQL installation guide for client-side

---

## 🗄️ Database Schema

Make sure to run the following SQL queries to set up your MySQL database:

```sql
CREATE DATABASE medical_shop;
USE medical_shop;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    batch_no VARCHAR(50),
    expiry_date DATE,
    price DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    gst_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    gst_no VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT,
    medicine_id INT,
    purchase_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    quantity INT NOT NULL,
    purchase_price DECIMAL(10,2) NOT NULL,
    invoice_pdf_path VARCHAR(255),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INT,
    total_price DECIMAL(10,2),
    gst_amount DECIMAL(10,2),
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

CREATE TABLE expiry_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT,
    expiry_date DATE,
    status ENUM('pending', 'resolved') DEFAULT 'pending',
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT,
    notification_type ENUM('stock', 'expiry', 'payment', 'other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('unread', 'read') DEFAULT 'unread'
);

CREATE TABLE settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(50) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL
);

___________________________________________________________________________________________________________________________________

## 🚀 Getting Started

_____________________________________________________________________
## Prerequisites
Python 3.10+

MySQL Server

Recommended: Virtual Environment

______________________________________________________________________
## Run the App

python main.py

_______________________________________________________________________

## 🙋‍♂️ Author
Developed by #Radha Khatri
🚀 Co-Lead, Cloud & Open Source @ GDGC ADCET
📫 Contact: beactive1474@gmail.com





