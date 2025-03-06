import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = "attendance.db"
        self.initialize()

    def initialize(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        # Create students table.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                registration_date TEXT NOT NULL
            )
        ''')
        # Create attendance table with checkin and checkout columns.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                checkin_time TEXT NOT NULL,
                checkout_time TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        conn.commit()
        conn.close()

    def register_student(self, student_id, name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (id, name, registration_date) VALUES (?, ?, ?)",
                (student_id, name, datetime.now().strftime("%Y-%m-%d"))
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def insert_attendance(self, student_id, checkin_time, checkout_time=None):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO attendance (student_id, checkin_time, checkout_time) VALUES (?, ?, ?)",
                (student_id, checkin_time, checkout_time)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print("Error inserting attendance:", e)
            return False
        finally:
            conn.close()

    def get_student_name(self, student_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE id=?", (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown"
