from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                            QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

class AttendanceDialog(QDialog):
    def __init__(self, database, face_recognition, headless=False):
        super().__init__()
        self.database = database
        self.face_recognition = face_recognition
        self.headless = headless

        self.setWindowTitle("Mark Attendance")
        self.setModal(True)
        self.setMinimumSize(640, 480)

        # Create layout
        layout = QVBoxLayout(self)

        # Camera preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)

        # Status label
        self.status_label = QLabel("Looking for face...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)

        # Initialize camera if not in headless mode
        if not self.headless:
            self.camera = cv2.VideoCapture(0)
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_preview)
            self.timer.start(100)  # 10 FPS
        else:
            self.camera = None
            self.timer = None
            self.preview_label.setText("Camera preview not available in headless mode")
            self.status_label.setText("Attendance marking not available in headless mode")

        # Cooldown timer to prevent multiple recognitions
        self.cooldown_timer = QTimer()
        self.cooldown_timer.timeout.connect(self.reset_cooldown)
        self.in_cooldown = False

    def update_preview(self):
        if self.headless:
            return

        ret, frame = self.camera.read()
        if ret:
            # Try to recognize face if not in cooldown
            if not self.in_cooldown:
                user_id, confidence, rect = self.face_recognition.recognize_face(frame)

                if user_id is not None and confidence < 100:  # Adjust confidence threshold as needed
                    # Draw rectangle around face
                    (x, y, w, h) = rect
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # Get student name
                    student_name = self.database.get_student_name(user_id)

                    if student_name:
                        # Mark attendance
                        self.database.mark_attendance(user_id)

                        # Update status
                        self.status_label.setText(
                            f"Attendance marked for {student_name} (ID: {user_id})")

                        # Start cooldown
                        self.in_cooldown = True
                        self.cooldown_timer.start(3000)  # 3 second cooldown
                else:
                    self.status_label.setText("Looking for face...")

            # Convert frame to QImage
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Display the image
            self.preview_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def reset_cooldown(self):
        self.in_cooldown = False
        self.cooldown_timer.stop()

    def closeEvent(self, event):
        if self.timer:
            self.timer.stop()
        if self.cooldown_timer:
            self.cooldown_timer.stop()
        if self.camera:
            self.camera.release()
        super().closeEvent(event)