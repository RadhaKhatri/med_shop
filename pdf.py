import os
import sys
import mimetypes
import smtplib
from email.message import EmailMessage
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox,
    QLineEdit, QInputDialog, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFileDialog
import platform
import subprocess
from PyQt6.QtWidgets import QMessageBox



class FileViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📁 Exported Files Manager")
        self.setGeometry(100, 100, 850, 600)

        self.folder_base_path = os.path.dirname(os.path.abspath(__file__))
        self.sections = {
            "Invoices": "invoices",
            "Reports": "reports",
            "Vendor Bill": "vendor_bills",
            "Photo Bill": "photo_bill"
        }

        self.current_label = None
        self.current_folder_path = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("📁 Exported Files Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #343a40; padding: 10px;")
        self.layout.addWidget(title)

        button_layout = QHBoxLayout()
        for label, folder in self.sections.items():
            button = QPushButton(f"📁 View {label}")
            button.setFixedSize(180, 40)
            button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007BFF; 
                    color: white; 
                    border-radius: 8px;
                    border: none; 
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _, f=folder, l=label: self.show_files(f, l))
            button_layout.addWidget(button)
        self.layout.addLayout(button_layout)

        # Upload Button
        self.upload_button = QPushButton("⬆️ Upload File")
        self.upload_button.setFixedSize(150, 35)
        self.upload_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.upload_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search files...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.filter_files)
        self.search_bar.setFixedHeight(30)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.search_bar)

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Last Modified", "Actions"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.file_table)

    def show_files(self, folder_name, label):
        folder_path = os.path.join(self.folder_base_path, folder_name)
        self.current_folder_path = folder_path
        self.current_label = label

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.load_files(folder_path, label)

    def filter_files(self, text):
        if self.current_folder_path:
            self.load_files(self.current_folder_path, self.current_label, filter_text=text)

    def load_files(self, folder_path, label, filter_text=""):
        self.file_table.setRowCount(0)
        all_files = os.listdir(folder_path)
        files = [f for f in all_files if filter_text.lower() in f.lower()]

        self.file_table.setRowCount(len(files))
        for row, file_name in enumerate(files):
            file_path = os.path.join(folder_path, file_name)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")

            self.file_table.setItem(row, 0, QTableWidgetItem(file_name))
            self.file_table.setItem(row, 1, QTableWidgetItem(modified_time))

            action_layout = QHBoxLayout()
            container = QWidget()

            open_btn = QPushButton("Open")
            share_btn = QPushButton("Share")
            delete_btn = QPushButton("Delete")

            for btn in (open_btn, share_btn, delete_btn):
                btn.setFixedHeight(30)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6c757d; 
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #5a6268;
                    }
                """)

            open_btn.clicked.connect(lambda _, p=file_path: self.open_file(p))
            share_btn.clicked.connect(lambda _, p=file_path, n=file_name: self.share_file(p, n))
            delete_btn.clicked.connect(lambda _, p=file_path: self.delete_file(p))

            action_layout.addWidget(open_btn)
            action_layout.addWidget(share_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            container.setLayout(action_layout)
            self.file_table.setCellWidget(row, 2, container)

    def upload_file(self):
        if not self.current_folder_path:
            QMessageBox.warning(self, "No Folder Selected", "❌ Please click a section (Invoices, Reports, etc.) before uploading.")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All Files (*)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                original_path = selected_files[0]
                original_name = os.path.basename(original_path)

                new_name, ok = QInputDialog.getText(self, "Rename File", "Enter new name for file (with extension):", QLineEdit.EchoMode.Normal, original_name)
                if ok and new_name.strip():
                    new_path = os.path.join(self.current_folder_path, new_name.strip())

                    try:
                        with open(original_path, 'rb') as src, open(new_path, 'wb') as dst:
                            dst.write(src.read())

                        QMessageBox.information(self, "Success", f"✅ File saved as '{new_name}' in {self.current_label}.")
                        self.search_bar.setText("")
                        self.load_files(self.current_folder_path, self.current_label)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"❌ Failed to save file:\n{str(e)}")
                else:
                    QMessageBox.warning(self, "Cancelled", "❌ File rename cancelled.")

    def open_file(self, file_path):
        try:
            if platform.system() == "Windows":
                # Use rundll32 to open with default associated program (e.g. Photos for images)
                subprocess.run(["rundll32", "shell32.dll,ShellExec_RunDLL", file_path], shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Could not open file:\n{str(e)}")


    def share_file(self, path, file_name):
        if not os.path.exists(path):
            QMessageBox.critical(self, "Error", f"❌ File not found:\n{path}")
            return

        receiver_email, ok = QInputDialog.getText(self, "Recipient Email", "Enter recipient's email:", QLineEdit.EchoMode.Normal)
        if ok and receiver_email.strip():
            try:
                sender_email = "beactive1474@gmail.com"
                app_password = "zrtr smiw bfvd droc"  # App password

                msg = EmailMessage()
                msg['Subject'] = f"File: {file_name}"
                msg['From'] = sender_email
                msg['To'] = receiver_email.strip()
                msg.set_content(f"Hello,\n\nPlease find the attached file: {file_name}.\n\nRegards,\nSiddhanath Medical")

                with open(path, 'rb') as f:
                    file_data = f.read()
                    file_type, _ = mimetypes.guess_type(path)
                    if file_type:
                        main_type, sub_type = file_type.split('/', 1)
                    else:
                        main_type, sub_type = 'application', 'octet-stream'

                    msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=file_name)

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, app_password)
                    smtp.send_message(msg)

                QMessageBox.information(self, "Success", "📤 Email sent successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to send email:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Cancelled", "Email sending cancelled or invalid email entered.")

    def delete_file(self, path):
        if os.path.exists(path):
            reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete:\n{os.path.basename(path)}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(path)
                    QMessageBox.information(self, "Deleted", "🗑️ File deleted successfully.")
                    self.search_bar.setText("")  # Clear search to reload
                    self.show_files(os.path.basename(self.current_folder_path), "Refreshed")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"❌ Failed to delete file:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Not Found", "❌ File not found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = FileViewer()
    viewer.show()
    sys.exit(app.exec())
