import sqlite3

# Connect to your database (make sure this is the correct path)
conn = sqlite3.connect("students.db")
c = conn.cursor()

# List of dummy students to add
students = [
    ("Maha Lakshmi N", "KGISL2023001", "CSE", "B.E"),
    ("John Doe", "KGISL2023002", "CSE", "B.E"),
    ("Jane Smith", "KGISL2023003", "ECE", "B.E"),
    ("Alex Johnson", "KGISL2023004", "MECH", "B.E")
]

# Insert students, skip if reg_no already exists
for s in students:
    c.execute("""
        INSERT OR IGNORE INTO students (name, reg_no, department, degree)
        VALUES (?, ?, ?, ?)
    """, s)

# Commit changes
conn.commit()

# Display current records in DB
c.execute("SELECT * FROM students")
rows = c.fetchall()
print("Current students in DB:")
for row in rows:
    print(row)

# Close connection
conn.close()
