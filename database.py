import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = "attendance.db"
        self.initialize()

    def initialize(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                registration_date TEXT NOT NULL
            )
        ''')

        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        conn.commit()
        conn.close()

    def register_student(self, student_id, name):
        """Register a new student"""
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

    def mark_attendance(self, student_id):
        """Mark attendance for a student"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (student_id, timestamp) VALUES (?, ?)",
            (student_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()

    def get_student_name(self, student_id):
        """Get student name by ID"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE id=?", (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_all_students(self):
        """Get all registered students"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, registration_date FROM students")
        students = cursor.fetchall()
        conn.close()
        return students

    def get_attendance_records(self, date=None):
        """Get attendance records, optionally filtered by date"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT s.id, s.name, a.timestamp 
                FROM attendance a 
                JOIN students s ON a.student_id = s.id 
                WHERE date(a.timestamp) = ?
                ORDER BY a.timestamp DESC
            """, (date,))
        else:
            cursor.execute("""
                SELECT s.id, s.name, a.timestamp 
                FROM attendance a 
                JOIN students s ON a.student_id = s.id 
                ORDER BY a.timestamp DESC
            """)
            
        records = cursor.fetchall()
        conn.close()
        return records
