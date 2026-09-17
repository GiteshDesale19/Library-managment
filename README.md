# LibraryHub — Library Management System

A beginner-friendly, full-stack Library Management System built with Python, Flask, and SQLite. It provides a librarian dashboard for managing books, members, book issues, returns, overdue books, and fines.

## Features

- Secure session-based librarian sign-in
- Add, search, and remove books
- Register and remove library members
- Issue available books and prevent duplicate active issues
- Return books with automatic fine calculation
- Overdue-loan dashboard and full return history
- SQLite database created automatically on first run

## Tech stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5

## Run locally

```bash
git clone https://github.com/YOUR-USERNAME/library-management.git
cd library-management
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

**Demo credentials:** username `admin`, password `admin123`.

## Project structure

```text
library-management/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── books.html
    ├── members.html
    ├── loans.html
    └── history.html
```

## Notes for production

Before deploying, set a strong `SECRET_KEY` environment variable and replace the demonstration login with real user accounts and password hashing.

## Resume description

Developed a Library Management System using Python, Flask, and SQLite to manage books, members, lending records, returns, overdue tracking, and automatic fine calculation. Built a responsive Bootstrap dashboard with CRUD operations, search, session-based authentication, and reporting history.
