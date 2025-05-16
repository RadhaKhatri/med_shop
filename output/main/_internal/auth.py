from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame
)
from ui.dashboard import Dashboard
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize
import sys
import subprocess
import os
from PyQt6.QtGui import QKeySequence, QShortcut
from utils import resource_path 


# ✅ Credentials
CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "password123"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Siddhanath Medical")
        self.resize(1024, 768)
        

        # ✅ Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # ✅ Create Background First
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        # ✅ Card-like Login Frame
        login_frame = QFrame(self)
        login_frame.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            padding: 30px;
            border: 1px solid #ccc;
        """)
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(15)
        login_frame.setLayout(frame_layout)

        # ✅ Shop Name
        shop_label = QLabel("Siddhanath Medical")
        shop_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        shop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shop_label.setStyleSheet("color: #222;")
        frame_layout.addWidget(shop_label)

        # ✅ Owner Name
        owner_label = QLabel("Owner: Aniket")
        owner_label.setFont(QFont("Arial", 12))
        owner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        owner_label.setStyleSheet("color: #666;")
        frame_layout.addWidget(owner_label)

        # ✅ Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFont(QFont("Arial", 12))
        self.username_input.setStyleSheet(self.input_style())
        frame_layout.addWidget(self.username_input)

        # ✅ Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setStyleSheet(self.input_style())
        frame_layout.addWidget(self.password_input)

        # ✅ Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.login_button.setStyleSheet(self.button_style())
        self.login_button.clicked.connect(self.validate_login)
        
        # ✅ Add shortcut for Enter key to trigger login
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut.activated.connect(self.validate_login)


        frame_layout.addWidget(self.login_button)
        
        # ✅ Install event filters to capture Up/Down keys
        self.username_input.installEventFilter(self)
        self.password_input.installEventFilter(self)


        # ✅ Add Login Frame to Main Layout
        main_layout.addWidget(login_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # ✅ Apply Background
        self.set_background()

    def set_background(self):
        """ Set a full-screen background image using QLabel. """
        background_image = QPixmap(resource_path("login.webp"))  # Load background image

        if not background_image.isNull():
            self.background_label.setPixmap(background_image.scaled(
                self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
            self.background_label.setGeometry(0, 0, self.width(), self.height())  # Fill screen

        # ✅ Ensure UI elements stay in front of the background
        self.background_label.lower()

    def resizeEvent(self, event):
        """ Ensure background resizes dynamically when window is resized. """
        self.set_background()
        super().resizeEvent(event)

    def input_style(self):
        return """
            QLineEdit {
                border: 2px solid #007BFF;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #007BFF; color: white;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

    def validate_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            self.open_dashboard()
        else:
            QMessageBox.warning(self, "Error", "Invalid Username or Password!")

    def open_dashboard(self):
        self.close()

        dashboard_path = resource_path(os.path.join( "dashboard.py"))
        print("Looking for:", dashboard_path)

        if os.path.exists(dashboard_path):
            print("Dashboard exists. Launching...")
            subprocess.Popen([sys.executable, dashboard_path])
        else:
            QMessageBox.critical(self, "Error", "Dashboard file not found!")
            
    def eventFilter(self, source, event):
        if event.type() == event.Type.KeyPress:
            if source == self.username_input and event.key() == Qt.Key.Key_Down:
                self.password_input.setFocus()
                return True
            elif source == self.password_input and event.key() == Qt.Key.Key_Up:
                self.username_input.setFocus()
                return True
        return super().eventFilter(source, event)
       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.showMaximized()
    sys.exit(app.exec())
