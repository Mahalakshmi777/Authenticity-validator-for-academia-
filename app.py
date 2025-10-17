# app.py
import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import pytesseract
from rapidfuzz import fuzz

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# point to your tesseract exe if required

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


DB_PATH = 'students.db'

####################
# Utility functions
####################

def query_student_by_reg(reg_no):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, reg_no, department, degree FROM students WHERE reg_no = ?', (reg_no,))
    row = c.fetchone()
    conn.close()
    return row  # (name, reg_no, department, degree) or None

def insert_student(name, reg_no, department, degree=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO students (name, reg_no, department, degree) VALUES (?, ?, ?, ?)', (name, reg_no, department, degree))
        conn.commit()
        ok = True
    except Exception as e:
        print("DB insert error:", e)
        ok = False
    conn.close()
    return ok

def extract_fields_from_text(text):
    """
    Try to extract reg no, name, department from OCR text.
    - reg no: look for patterns with letters+digits (common for regs) e.g. KGISL2023001 or ABC2023123
    - name: heuristic: look for lines that appear like a name (Title case, or after 'This is to certify' etc.)
    - dept: look for known department keywords
    """
    t = text.replace('\r','\n')
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    joined = " ".join(lines)

    # 1) reg no pattern (letters + digits) - tweak as needed
    reg_pattern = re.compile(r'\b([A-Z]{2,6}\d{4,6}|[A-Z]{2,6}\d{3,7})\b', re.IGNORECASE)
    reg_match = reg_pattern.search(joined)
    reg_no = reg_match.group(1).upper() if reg_match else None

    # 2) department detection (common dept keywords)
    departments = ["CSE","ECE","EEE","MECH","CIVIL","IT","MBA","COMPUTER SCIENCE","COMPUTER SCIENCE AND ENGINEERING"]
    dept_found = None
    for dept in departments:
        if re.search(r'\b' + re.escape(dept) + r'\b', joined, re.IGNORECASE):
            dept_found = dept
            break

    # 3) name detection: try heuristics
    # - look for line containing 'awarded to' or 'This is to certify that' or 'Name:'
    name = None
    for ln in lines:
        low = ln.lower()
        if 'awarded to' in low or 'this is to certify that' in low or 'name:' in low:
            # extract probable name part
            # e.g. "This is to certify that Maha Lakshmi N has..."
            # remove prefixes
            candidate = re.sub(r'(?i)this is to certify that|awarded to|name:','', ln).strip(' :-')
            # if candidate has two words assume name
            if len(candidate.split()) >= 2:
                name = candidate.strip()
                break
    if not name:
        # fallback: check for lines with Title Case words (2+ words)
        for ln in lines[:8]:  # look at first 8 lines
            if len(ln.split()) >= 2 and ln == ln.title():
                name = ln.strip()
                break

    return {"reg_no": reg_no, "name": name, "department": dept_found}

def verify_against_db(extracted):
    """
    Logic:
    1. If reg_no found: lookup DB by reg_no (authoritative)
       - if not found -> Fake (reg not in DB)
       - if found -> compare name and department using fuzzy ratio
         - if name ratio >= 80 and dept matches -> Original
         - otherwise -> Fake (with reasons)
    2. If no reg_no found: try searching DB by name (less reliable)
    """
    reasons = []
    if not extracted:
        return {"status": "Fake", "reasons":["No text extracted"]}

    reg = extracted.get('reg_no')
    name_ex = extracted.get('name')
    dept_ex = extracted.get('department')

    if reg:
        student = query_student_by_reg(reg)
        if not student:
            return {"status":"Fake", "reasons":[f"Registration number {reg} not found in DB."]}
        db_name, db_reg, db_dept, db_degree = student
        # name fuzzy match
        name_score = 0
        if name_ex:
            name_score = fuzz.token_set_ratio(name_ex.lower(), db_name.lower())
        # dept match (exact word or fuzzy)
        dept_score = 0
        if dept_ex and db_dept:
            dept_score = fuzz.token_set_ratio(dept_ex.lower(), db_dept.lower())

        reasons.append(f"DB reg: {db_reg}; OCR reg: {reg}")
        reasons.append(f"Name match score: {name_score}")
        reasons.append(f"Department match score: {dept_score}")

        if name_score >= 80 and (dept_score >= 80 or db_dept.lower() in (dept_ex or '').lower()):
            return {"status":"Original", "reasons":reasons, "db_record": student}
        else:
            # partial mismatch
            mismatch_reasons = []
            if name_score < 80:
                mismatch_reasons.append(f"Name mismatch (score {name_score} vs expected '{db_name}').")
            if dept_score < 80 and db_dept.lower() not in (dept_ex or '').lower():
                mismatch_reasons.append(f"Department mismatch (found '{dept_ex}' vs expected '{db_dept}').")
            return {"status":"Fake", "reasons": reasons + mismatch_reasons, "db_record": student}

    else:
        # no reg_no: try best-effort search by name (not reliable)
        if not name_ex:
            return {"status":"Fake", "reasons":["Unable to detect registration number or name reliably."]}
        # try to find best name match in DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT name, reg_no, department, degree FROM students')
        rows = c.fetchall()
        conn.close()
        best = None
        best_score = 0
        for row in rows:
            db_name = row[0]
            score = fuzz.token_set_ratio(name_ex.lower(), db_name.lower())
            if score > best_score:
                best_score = score
                best = row
        if best and best_score >= 85:
            return {"status":"Original (by name match)", "reasons":[f"Name match score {best_score}"], "db_record": best}
        else:
            return {"status":"Fake", "reasons":[f"No strong name match (best score {best_score})."]}

####################
# Routes
####################

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        reg = request.form.get('reg_no')
        dept = request.form.get('department')
        degree = request.form.get('degree')
        ok = insert_student(name, reg, dept, degree)
        return render_template('admin.html', message = "Added" if ok else "Failed (maybe reg exists)")
    return render_template('admin.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    fp = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(fp)

    try:
        # Only image files in this simple example
        img = Image.open(fp)
        extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        return f"Error running OCR: {e}"

    extracted = extract_fields_from_text(extracted_text)
    result = verify_against_db(extracted)

    return render_template('result.html', text=extracted_text, extracted=extracted, result=result)

if __name__ == "__main__":
    app.run(debug=True)
