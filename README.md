# ShareIt - Secure File Sharing System 🔐

A Django-based secure file sharing platform with encryption and token-based access control.

---

## 🚀 Features

- File upload with encryption (Fernet)
- Temporary share links using UUID tokens
- Email verification system
- Token-based file download validation
- Download logging system

---

## 🛠 Tech Stack

- Python
- Django
- Cryptography (Fernet)
- SQLite
- HTML/CSS

---

## 🔐 Security Highlights

- Encrypted file storage
- Unique share tokens
- Environment-based secret management (.env)
- No hardcoded credentials

---

## ⚙️ Setup Instructions

1. Clone the repository
2. Create virtual environment:
   python -m venv venv
3. Activate environment:
   venv\Scripts\activate
4. Install dependencies:
   pip install -r requirements.txt
5. Create .env file with email credentials
6. Run server:
   python manage.py runserver

---

## 📌 Future Improvements

- Token expiry system
- Password hashing improvement
- Production deployment
- AWS S3 storage integration

---

## 👨‍💻 Author

Yash Verma