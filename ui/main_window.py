from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import os

from .register_dialog import RegisterDialog
from .attendance_dialog import AttendanceDialog
from .training_dialog import TrainingDialog

class MainWindow(QMainWindow):
    def __init__(self, database, face_recognition):
        super().__init__()
        self.database = database
        self.face_recognition = face_recognition

        # Check if we're running in headless mode
        self.headless = os.environ.get("QT_QPA_PLATFORM") == "offscreen"

        self.setWindowTitle("Facial Recognition Attendance System")
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create buttons layout
        button_layout = QHBoxLayout()

        # Create action buttons
        self.register_btn = QPushButton("Register New Student")
        self.register_btn.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(self.register_btn)

        self.attendance_btn = QPushButton("Mark Attendance")
        self.attendance_btn.clicked.connect(self.show_attendance_dialog)
        button_layout.addWidget(self.attendance_btn)

        self.train_btn = QPushButton("Train Model")
        self.train_btn.clicked.connect(self.show_training_dialog)
        button_layout.addWidget(self.train_btn)

        layout.addLayout(button_layout)

        # Create table for showing attendance records
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Student ID", "Name", "Timestamp"])
        layout.addWidget(self.table)

        # Load and apply stylesheet
        self.load_stylesheet()

        # Initialize table data
        self.refresh_attendance_data()

        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_attendance_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def load_stylesheet(self):
        try:
            with open("assets/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass  # Use default style if stylesheet is not available

    def refresh_attendance_data(self):
        """Refresh the attendance records table"""
        records = self.database.get_attendance_records()
        self.table.setRowCount(len(records))

        for row, (student_id, name, timestamp) in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(str(student_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(timestamp))

        self.table.resizeColumnsToContents()

    def show_register_dialog(self):
        """Show the student registration dialog"""
        dialog = RegisterDialog(self.database, self.face_recognition, headless=self.headless)
        if dialog.exec():
            self.refresh_attendance_data()

    def show_attendance_dialog(self):
        """Show the attendance marking dialog"""
        dialog = AttendanceDialog(self.database, self.face_recognition, headless=self.headless)
        if dialog.exec():
            self.refresh_attendance_data()

    def show_training_dialog(self):
        """Show the model training dialog"""
        dialog = TrainingDialog(self.face_recognition)
        dialog.exec()