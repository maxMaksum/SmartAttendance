from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class AttendanceDialog(QDialog):
    def __init__(self, database, face_recognition, headless=False):
        super().__init__()
        self.database = database
        self.face_recognition = face_recognition
        self.headless = headless
        self.setWindowTitle("Mark Attendance")
        self.cap = cv2.VideoCapture(0)  # Open default camera

        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
            self.close()
            return

        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.video_label = QLabel("Camera feed")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)

        self.face_count_label = QLabel("Detected faces: 0")
        self.face_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.face_count_label)

        self.capture_button = QPushButton("Capture & Mark Attendance")
        self.capture_button.clicked.connect(self.capture_frame)
        layout.addWidget(self.capture_button)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            print("Frame captured")
            # Detect faces in the frame
            faces = self.face_recognition.detect_faces(frame)
            print(f"Faces detected: {faces}")
            self.face_count_label.setText(f"Detected faces: {len(faces)}")
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.video_label.setPixmap(pixmap)  # Ensure the QLabel's pixmap is set
        else:
            print("Failed to capture frame")

    def capture_frame(self):
        ret, frame = self.cap.read()
        if ret:
            user_id, confidence, rect = self.face_recognition.recognize_face(frame)
            if user_id is not None:
                self.database.mark_attendance(user_id)
                QMessageBox.information(self, "Attendance Marked", f"Attendance marked for Student ID: {user_id}")
                self.print_match_message(user_id)
                self.accept()
            else:
                QMessageBox.warning(self, "Not Recognized", "No face recognized. Please try again.")
                # Show the frame with detected faces
                self.update_frame()

    def print_match_message(self, user_id):
        print(f"Data from webcam matches with data in the database for Student ID: {user_id}")

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        event.accept()
