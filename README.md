# Secure Share - End-to-End Encrypted File Sharing �

A Django-based secure file sharing platform with AES-256 encryption, temporary share links, and user account management.

---

## 🚀 Features

- **End-to-End Encryption**: Files encrypted with AES-256 before storage
- **Secure Share Links**: Generate temporary shareable links with UUID tokens
- **Email Verification**: Account verification via email links
- **User Authentication**: Secure login/signup with status-based approval
- **Admin Dashboard**: Manage users, activate/deactivate accounts
- **File Management**: Upload, view, download, and delete encrypted files
- **Storage Quota**: Track storage usage per user
- **Expiring Links**: Auto-expiring share links with time-based access control
- **Download History**: Track file downloads and sharing activity
- **Responsive Design**: Mobile-friendly UI with consistent styling

---

## 🛠 Tech Stack

- **Backend**: Django 6.0.2
- **Language**: Python 3.13
- **Database**: SQLite3
- **Encryption**: Cryptography (Fernet AES-256)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Email**: SMTP-based verification system

---

## 🔐 Security Highlights

- AES-256 encryption for all uploaded files
- Unique UUID tokens for share links
- Email-based account verification
- Admin approval workflow (status = 0/1)
- Session-based authentication
- Secure file download with access validation
- No plaintext password storage
- CSRF protection on forms

---

## 📋 Core Features

### User Management
- User signup with email verification
- Admin approval before account activation
- Change password functionality
- Session-based authentication
- Logout with session flush

### File Operations
- Upload files with automatic encryption
- AES-256 encryption key generation per file
- Store original filename for download
- View uploaded files with metadata
- Download with automatic decryption
- Delete files and encrypted data
- Track upload time and file details

### Sharing
- Generate temporary shareable links
- UUID-based unique tokens
- Public file access via share token
- Share status tracking
- Link copied to clipboard functionality

### Admin Features
- User management dashboard
- Activate/deactivate user accounts
- Delete user accounts
- View all registered users
- Change admin password

---

## ⚙️ Setup Instructions

1. **Clone Repository**
   ```bash
   git clone <repo-url>
   cd Minor_Project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   - Create `.env` file with email credentials
   - Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run Server**
   ```bash
   python manage.py runserver
   ```

7. **Access Application**
   - User: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

---

## � Project Structure

```
Minor_Project/
├── config/                 # Django settings
├── core/                   # Main app
│   ├── migrations/        # Database migrations
│   ├── static/
│   │   └── core/css/      # Stylesheets
│   ├── templates/core/    # HTML templates
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   └── utils.py           # Helper functions
├── manage.py              # Django CLI
└── db.sqlite3             # Database
```

---

## 📊 Database Models

### Signup Model
- regid (Primary Key)
- name, email, password, mobile
- status (0=inactive, 1=active)
- role (user/admin)
- info (registration timestamp)

### ShareNotes Model
- id (Primary Key)
- title, category, description
- file (encrypted data)
- owner (user email)
- upload_time (timestamp)
- share_token (UUID)
- encryption_key (stored key)
- is_shared (boolean)
- original_filename

---

## 🔄 Workflow

1. **Registration**: User signs up → Email verification link sent
2. **Verification**: User verifies email → Admin approval needed
3. **Login**: Approved user logs in → Session created
4. **Upload**: User uploads file → Auto-encrypted → Stored
5. **Share**: Generate link → Share token created → Public access
6. **Download**: Recipient uses link → File auto-decrypted → Download

---

## 📌 Recent Updates

- ✅ Storage quota system for users
- ✅ Expiring share links with time-based validation
- ✅ Enhanced admin dashboard
- ✅ File metadata tracking
- ✅ Improved email verification system
- ✅ Responsive CSS styling across all pages

---

## 🚧 Future Improvements

- Two-factor authentication
- Password reset via email
- Advanced file permissions
- File preview functionality
- Bulk file operations
- AWS S3 storage integration
- Rate limiting
- API endpoints

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💻 Author

**Yash Verma**
- GitHub: [@Yash-Verma-721](https://github.com/Yash-Verma-721)

---

**Last Updated**: May 2, 2026