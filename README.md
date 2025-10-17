🎓 Authenticity Validator for Academia

Authenticity Validator for Academia is a web-based application designed to verify the authenticity of academic certificates using Optical Character Recognition (OCR) and database validation.
It extracts text details (like Name, Register Number, Department, and Degree) from uploaded certificates and compares them with trusted data stored in a SQLite database.
If all the details match, the certificate is marked ✅ Authentic — otherwise, it is flagged ❌ Fake.


⚙️ Tech Stack
Category	Technologies Used
Frontend	HTML, CSS
Backend	Python (Flask)
OCR Engine	Tesseract OCR (pytesseract)
Database	SQLite3
Libraries	Flask, pytesseract, Pillow, pdf2image


🗂️ Project Structure
AuthenticityValidator/
│
├── app.py                 # Main Flask application
├── add_students.py        # Adds original certificate records to DB
├── database.db            # SQLite database (auto-created)
│
├── templates/             # HTML templates
│   ├── index.html         # Upload & verification page
│   └── result.html        # Result display page
│
├── static/
│   └── styles.css         # Styling for web pages
│
├── uploads/               # Temporary storage for uploaded files
│
└── .gitignore             # Ignored files & folders (venv, uploads, etc.)


🚀 Setup & Installation
1️⃣ Clone the repository
git clone https://github.com/<your-username>/AuthenticityValidator.git
cd AuthenticityValidator

2️⃣ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate     

3️⃣ Install dependencies
pip install flask pytesseract pillow pdf2image

4️⃣ Install Tesseract OCR

Download and install from:
🔗 https://github.com/tesseract-ocr/tesseract

After installing, note the path (example:
C:\Program Files\Tesseract-OCR\tesseract.exe)

Then add this line in your app.py:

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

5️⃣ Add sample student records

Run: python add_students.py

This creates the database and inserts original student data.

6️⃣ Run the Flask app
python app.py


Then open your browser and visit:

http://127.0.0.1:5000

🧠 How It Works

Upload a certificate (Image).

The app extracts text from it using Tesseract OCR.

Extracted data is compared with trusted records in the database.

Displays:

✅ Authentic Certificate → if all fields match

❌ Fake Certificate → if mismatch found

💾 Example Database Records
Name	         Reg No  	Department	Degree
Mahalakshmi N	21CSE0456  	CSE	       BE
Priyanka S	  21ECE0345	  CSE        BE


💡 Future Enhancements

1.AI Integration: Use AI to automatically detect fake or tampered certificates through pattern and signature analysis.

2.Blockchain Support: Store verified certificate data on a secure blockchain for transparency and tamper-proof validation.

3.Institution Portal: Allow colleges to upload verified data directly for instant authenticity checks.

4.Enhanced OCR: Support more languages and file formats for wider usability.



Team Members: Brindha M
              Dharshini M
              Indhumadhi P
              Mahalakshmi N
              Priyanka S


🏁 Conclusion

The Authenticity Validator for Academia simplifies the verification of academic certificates by integrating OCR and database validation, providing an efficient, automated way to detect fake or tampered certificates in educational institutions.



