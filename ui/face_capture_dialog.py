from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class FaceCaptureDialog(QDialog):
    def __init__(self, face_recognition, parent=None):
        super().__init__(parent)
        self.face_recognition = face_recognition
        self.captured_images = []  # List to store captured face images
        self.setWindowTitle("Capture Face Data")
        self.setModal(True)
        self.setup_ui()

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open camera.")
            self.reject()

        # Timer for updating the video feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms

    def setup_ui(self):
        layout = QVBoxLayout()

        # Label to display the video feed
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)

        # Button to capture face images
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_face)
        layout.addWidget(self.capture_button)

        # Button to finish capturing
        self.finish_button = QPushButton("Finish", self)
        self.finish_button.clicked.connect(self.accept)
        layout.addWidget(self.finish_button)

        self.setLayout(layout)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Detect faces in the frame
            face, rect = self.face_recognition.detect_face(frame)
            if face is not None:
                # Draw a rectangle around the detected face
                x, y, w, h = rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convert the frame to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Display the QImage in the QLabel
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def capture_face(self):
        ret, frame = self.cap.read()
        if ret:
            face, rect = self.face_recognition.detect_face(frame)
            if face is not None:
                self.captured_images.append(face)
                QMessageBox.information(self, "Success", "Face captured successfully!")
            else:
                QMessageBox.warning(self, "Error", "No face detected in the frame.")

    def closeEvent(self, event):
        # Release the camera when the dialog is closed
        self.cap.release()
        event.accept()