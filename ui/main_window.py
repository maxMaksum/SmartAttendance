import os
import cv2
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class MainWindow(QMainWindow):
    def __init__(self, database, face_recognition, attendance_manager):
        super().__init__()
        self.database = database
        self.face_recognition = face_recognition
        self.attendance_manager = attendance_manager
        self.headless = os.environ.get("QT_QPA_PLATFORM") == "offscreen"

        self.setWindowTitle("Facial Recognition Attendance System")
        self.setMinimumSize(800, 600)
        
        # Initialize UI
        self.init_ui()
        self.load_stylesheet()
        self.refresh_attendance_data()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_attendance_data)
        self.refresh_timer.start(30000)  # 30 seconds

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Button Layout
        button_layout = QHBoxLayout()
        self.register_btn = QPushButton("Register New Student")
        self.register_btn.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(self.register_btn)

        self.mark_attendance_btn = QPushButton("Mark Attendance")
        self.mark_attendance_btn.clicked.connect(self.handle_mark_attendance)
        button_layout.addWidget(self.mark_attendance_btn)

        self.train_btn = QPushButton("Train Model")
        self.train_btn.clicked.connect(self.show_training_dialog)
        button_layout.addWidget(self.train_btn)

        layout.addLayout(button_layout)

        # Attendance Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Student ID", "Name", "Timestamp", "Status"])
        layout.addWidget(self.table)

        # Face Preview
        self.face_preview = QLabel("Face Preview")
        self.face_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.face_preview)

    def load_stylesheet(self):
        try:
            with open("assets/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Error loading stylesheet:", e)

    def refresh_attendance_data(self):
        records = self.attendance_manager.get_session_records()
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(str(record["student_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(record.get("name", "Unknown")))
            self.table.setItem(row, 2, QTableWidgetItem(self.format_timestamp(record)))
            self.table.setItem(row, 3, QTableWidgetItem(record["state"].title().replace("_", " ")))
        self.table.resizeColumnsToContents()

    def format_timestamp(self, record):
        if record["state"] == "checked_in":
            return record["checkin_time"].strftime("%Y-%m-%d %H:%M:%S")
        return record.get("checkout_time", record["checkin_time"]).strftime("%Y-%m-%d %H:%M:%S")

    def show_register_dialog(self):
        # Local import to avoid circular dependency
        from .register_dialog import RegisterDialog
        dialog = RegisterDialog(
            database=self.database,
            face_recognition=self.face_recognition,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_attendance_data()

    def show_training_dialog(self):
        from .training_dialog import TrainingDialog  # Local import
        dialog = TrainingDialog(self.face_recognition, parent=self)
        dialog.exec()

    def handle_mark_attendance(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            QMessageBox.warning(self, "Error", "Could not access camera")
            return

        user_id, confidence, rect = self.face_recognition.recognize_face(frame)
        if user_id:
            self.update_face_preview(frame, rect)
            student_name = self.database.get_student_name(user_id)
            result = self.attendance_manager.check_in(user_id, student_name)
            QMessageBox.information(self, "Attendance", result["message"])
            self.refresh_attendance_data()
        else:
            QMessageBox.warning(self, "Not Recognized", "No matching face found")

    def update_face_preview(self, frame, rect):
        if rect:
            x, y, w, h = rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.face_preview.setPixmap(QPixmap.fromImage(q_img).scaled(
            200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.attendance_manager.save_records(self.database)
        event.accept()