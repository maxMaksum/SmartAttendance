import sys
import os
from PyQt6.QtWidgets import QApplication
from database import Database
from recognition import FaceRecognition
from ui.main_window import MainWindow

def main():
    # Set environment variables for headless operation
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-runner"
    os.environ["DISPLAY"] = ":99"

    # Create application
    app = QApplication(sys.argv)

    # Initialize components
    database = Database()
    face_recognition = FaceRecognition()

    # Create and show main window
    window = MainWindow(database, face_recognition)
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()