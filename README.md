# Library-managment

# LibraryHub — Library Management System

A beginner-friendly Library Management System built with Python, Flask, SQLite, and Bootstrap.

## Features

- Librarian login system
- Add, search, and remove books
- Register and remove library members
- Issue books to members
- Return books with automatic fine calculation
- Track overdue loans
- View returned-book history
- SQLite database created automatically

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5
- HTML and CSS

## How to Run the Project

1. Clone the repository:

```bash
git clone https://github.com/GiteshDesale19/library-management.git
```

2. Open the project folder:

```bash
cd library-management
```

3. Install required packages:

```bash
python -m pip install -r requirements.txt
```

4. Start the application:

```bash
python app.py
```

5. Open this address in your browser:

```text
http://127.0.0.1:5000
```

## Demo Login

```text
Username: admin
Password: admin123
```

## Project Structure

```text
library-management/
├── app.py
├── requirements.txt
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

## Usage

1. Log in with the demo credentials.
2. Add books through the **Books** section.
3. Add library members through the **Members** section.
4. Issue an available book from the **Loans** section.
5. Return books when they are received back.
6. Check overdue books and fines from the dashboard and history pages.

## Future Improvements

- Real user accounts with password hashing
- Book cover images
- Email reminders for overdue books
- Export reports as PDF or CSV
- Role-based access for librarians and administrators

Gitesh Desale
