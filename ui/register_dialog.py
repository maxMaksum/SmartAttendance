import os
import cv2
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, 
    QPushButton, QMessageBox, QLabel
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from .face_capture_dialog import FaceCaptureDialog

class RegisterDialog(QDialog):
    DUPLICATE_THRESHOLD = 50

    def __init__(self, database, face_recognition, parent=None):
        super().__init__(parent)
        self.database = database
        self.face_recognition = face_recognition
        self.setWindowTitle("Student Registration")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Student ID Input
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter Student ID")
        layout.addWidget(self.id_input)

        # Video Label
        self.video_label = QLabel()
        layout.addWidget(self.video_label)

        # Capture Button
        self.capture_btn = QPushButton("Capture Face Data")
        self.capture_btn.clicked.connect(self.capture_face_data)
        layout.addWidget(self.capture_btn)

        # Register Button
        self.register_btn = QPushButton("Complete Registration")
        self.register_btn.clicked.connect(self.finalize_registration)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def capture_face_data(self):
        student_id = self.id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Error", "Please enter Student ID first")
            return

        # Initial camera check
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.warning(self, "Error", "Camera not available")
            return

        face_detected = False
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame for better visibility
            frame = cv2.resize(frame, (640, 480))

            # Face detection
            faces, _ = self.face_recognition.detect_face(frame)
            if faces is not None and len(faces) > 0:
                for face in faces:
                    (x, y, w, h) = face[:4]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_detected = True

            # Convert frame to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))

            # Process events to update the UI
            QApplication.processEvents()

            # Add a delay to slow down the video feed
            time.sleep(0.1)

            if face_detected:
                break

        cap.release()

        if face_detected:
            # Save the captured frame for inspection
            capture_frame_path = os.path.join("capture_frames", f"{student_id}_captured_frame.jpg")
            os.makedirs("capture_frames", exist_ok=True)
            cv2.imwrite(capture_frame_path, frame)
            print(f"Captured frame saved as '{capture_frame_path}'")  # Debug message

            # Duplicate check
            if os.path.exists(self.face_recognition.model_file):
                faces, _ = self.face_recognition.detect_face(frame)
                if faces is None or len(faces) == 0:
                    QMessageBox.warning(self, "Error", "No face detected")
                    print("No face detected in the captured frame.")  # Debug message
                    return

                user_id, confidence, _ = self.face_recognition.recognize_face(frame)
                if user_id and confidence < self.DUPLICATE_THRESHOLD:
                    QMessageBox.warning(self, "Duplicate", "Face already registered")
                    return

            # Start face capture
            capture_dialog = FaceCaptureDialog(self.face_recognition, self)
            if capture_dialog.exec() == QDialog.DialogCode.Accepted:
                self.save_face_data(student_id, capture_dialog.captured_images)
        else:
            QMessageBox.warning(self, "Error", "No face detected")

    def save_face_data(self, student_id, images):
        save_dir = os.path.join("training_data", student_id)
        os.makedirs(save_dir, exist_ok=True)
        
        for idx, img in enumerate(images):
            cv2.imwrite(os.path.join(save_dir, f"{idx}.jpg"), img)
        
        QMessageBox.information(
            self, 
            "Success", 
            f"Saved {len(images)} face images for student {student_id}"
        )

    def finalize_registration(self):
        student_id = self.id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Error", "Student ID required")
            return

        if not os.path.exists(os.path.join("training_data", student_id)):
            QMessageBox.warning(self, "Error", "Capture face data first")
            return

        # Add to database
        self.database.add_student(student_id, "Unknown")  # Add actual name if available
        QMessageBox.information(self, "Success", "Registration complete")
        self.accept()