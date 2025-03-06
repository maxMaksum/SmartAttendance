from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

class RegisterDialog(QDialog):
    def __init__(self, database, face_recognition, headless=False):
        super().__init__()
        self.database = database
        self.face_recognition = face_recognition
        self.headless = headless

        self.setWindowTitle("Register New Student")
        self.setModal(True)
        self.setMinimumSize(640, 480)

        # Create layout
        layout = QVBoxLayout(self)

        # Create form layout
        form_layout = QHBoxLayout()

        # Student ID input
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Student ID")
        form_layout.addWidget(self.id_input)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Student Name")
        form_layout.addWidget(self.name_input)

        layout.addLayout(form_layout)

        # Camera preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)

        # Status label
        self.status_label = QLabel("Please position your face in the camera")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.capture_btn = QPushButton("Start Capture")
        self.capture_btn.clicked.connect(self.toggle_capture)
        button_layout.addWidget(self.capture_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_student)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # Initialize camera if not in headless mode
        if not self.headless:
            self.camera = cv2.VideoCapture(0)
            self.capture_timer = QTimer()
            self.capture_timer.timeout.connect(self.update_preview)
        else:
            self.camera = None
            self.capture_timer = None
            self.preview_label.setText("Camera preview not available in headless mode")

        # Initialize capture variables
        self.is_capturing = False
        self.captured_frames = []

    def toggle_capture(self):
        if self.headless:
            QMessageBox.warning(self, "Error", "Camera capture not available in headless mode")
            return

        if not self.is_capturing:
            if not self.id_input.text() or not self.name_input.text():
                QMessageBox.warning(self, "Error", "Please enter both ID and Name")
                return

            self.capture_btn.setText("Stop Capture")
            self.is_capturing = True
            self.captured_frames = []
            self.capture_timer.start(100)  # 10 FPS
        else:
            self.capture_btn.setText("Start Capture")
            self.is_capturing = False
            self.capture_timer.stop()

            if len(self.captured_frames) >= 30:
                self.save_btn.setEnabled(True)
                self.status_label.setText("Capture complete! Click Save to register.")
            else:
                self.status_label.setText("Not enough frames captured. Try again.")

    def update_preview(self):
        if self.headless:
            return

        ret, frame = self.camera.read()
        if ret:
            # Detect face
            face, rect = self.face_recognition.detect_face(frame)

            if face is not None:
                # Draw rectangle around face
                (x, y, w, h) = rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                if self.is_capturing:
                    self.captured_frames.append(frame)
                    self.status_label.setText(f"Capturing... {len(self.captured_frames)}/30")

                    if len(self.captured_frames) >= 30:
                        self.toggle_capture()

            # Convert frame to QImage
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Display the image
            self.preview_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def save_student(self):
        student_id = int(self.id_input.text())
        name = self.name_input.text()

        # Register in database
        if not self.database.register_student(student_id, name):
            QMessageBox.warning(self, "Error", "Student ID already exists!")
            return

        # In headless mode, simulate captured frames
        if self.headless:
            QMessageBox.information(self, "Success", 
                                  f"Student registered successfully in headless mode!")
            self.accept()
            return

        # Save training images
        saved_count = self.face_recognition.save_training_images(student_id, self.captured_frames)

        if saved_count > 0:
            QMessageBox.information(self, "Success", 
                                  f"Student registered successfully!\n{saved_count} training images saved.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to save training images!")

    def closeEvent(self, event):
        if self.capture_timer:
            self.capture_timer.stop()
        if self.camera:
            self.camera.release()
        super().closeEvent(event)