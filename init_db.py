# init_db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_no TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            degree TEXT
        )
    ''')
    # sample entries
    students = [
        ("Maha Lakshmi N", "KGISL2023001", "CSE", "B.E Computer Science and Engineering"),
        ("John Doe", "ABC2023123", "EEE", "B.Tech Electrical Engineering")
    ]
    for name, reg, dept, degree in students:
        try:
            c.execute('INSERT INTO students (name, reg_no, department, degree) VALUES (?, ?, ?, ?)', (name, reg, dept, degree))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    print("students.db created/updated.")

if __name__ == "__main__":
    init_db()
