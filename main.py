import sys
from PyQt6.QtWidgets import QApplication
from database import Database
from recognition import FaceRecognition
from ui.main_window import MainWindow
from attendance_manager import AttendanceManager

def main():
    app = QApplication(sys.argv)
    print("Initializing database...")
    database = Database()
    print("Initializing face recognition...")
    face_recognition = FaceRecognition()
    print("Initializing session-based attendance manager...")
    attendance_manager = AttendanceManager()
    print("Creating and showing main window...")
    window = MainWindow(database, face_recognition, attendance_manager)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
