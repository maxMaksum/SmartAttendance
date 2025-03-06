import sys
import os
from PyQt6.QtWidgets import QApplication
from database import Database
from recognition import FaceRecognition
from ui.main_window import MainWindow

def main():
    # Remove headless environment variables if running locally
    print("Setting environment variables...")  # This can be removed in local testing
    # os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Comment this out for local development
    # os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-runner"  # Comment this out
    # os.environ["DISPLAY"] = ":99"  # Comment this out
    
    # Create application
    print("Creating application...")
    app = QApplication(sys.argv)

    # Initialize components
    print("Initializing database...")
    database = Database()
    print("Database initialized.")
    print("Initializing face recognition...")
    face_recognition = FaceRecognition()
    print("Face recognition initialized.")

    # Create and show main window
    print("Creating and showing main window...")
    window = MainWindow(database, face_recognition)
    window.show()
    print("Main window shown.")

    # Start event loop
    print("Starting event loop...")
    sys.exit(app.exec())
    print("Event loop started.")  # This line will not be executed

if __name__ == "__main__":
    main()
