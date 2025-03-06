from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar,
                            QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class TrainingWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, face_recognition):
        super().__init__()
        self.face_recognition = face_recognition
    
    def run(self):
        try:
            num_images = self.face_recognition.train_model()
            self.finished.emit(num_images)
        except Exception as e:
            self.error.emit(str(e))

class TrainingDialog(QDialog):
    def __init__(self, face_recognition):
        super().__init__()
        self.face_recognition = face_recognition
        
        self.setWindowTitle("Train Model")
        self.setModal(True)
        self.setMinimumSize(400, 200)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Ready to train model")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Train button
        self.train_btn = QPushButton("Start Training")
        self.train_btn.clicked.connect(self.start_training)
        layout.addWidget(self.train_btn)
        
        # Initialize worker
        self.worker = None

    def start_training(self):
        self.train_btn.setEnabled(False)
        self.status_label.setText("Training in progress...")
        
        # Create and start worker thread
        self.worker = TrainingWorker(self.face_recognition)
        self.worker.finished.connect(self.training_finished)
        self.worker.error.connect(self.training_error)
        self.worker.start()

    def training_finished(self, num_images):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.status_label.setText("Training complete!")
        
        QMessageBox.information(self, "Success", 
                              f"Model trained successfully with {num_images} images!")
        self.accept()

    def training_error(self, error_msg):
        QMessageBox.warning(self, "Error", f"Training failed: {error_msg}")
        self.train_btn.setEnabled(True)
        self.status_label.setText("Training failed")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
