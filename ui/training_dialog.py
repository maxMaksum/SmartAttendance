from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox

class TrainingDialog(QDialog):
    def __init__(self, face_recognition, parent=None):
        super().__init__(parent)
        self.face_recognition = face_recognition
        self.setWindowTitle("Train Model")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Train Model using collected training images."))
        self.train_button = QPushButton("Train")
        self.train_button.clicked.connect(self.train_model)
        layout.addWidget(self.train_button)

    def train_model(self):
        try:
            count = self.face_recognition.train_model()
            QMessageBox.information(self, "Training Completed", f"Model trained with {count} images.")
        except Exception as e:
            QMessageBox.critical(self, "Training Error", str(e))
