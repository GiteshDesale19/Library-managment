import os
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FINE_PER_DAY"] = 2
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    author = db.Column(db.String(140), nullable=False)
    isbn = db.Column(db.String(30), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    loans = db.relationship("Loan", backref="book", lazy=True)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(140), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    joined_at = db.Column(db.Date, default=date.today)
    loans = db.relationship("Loan", backref="member", lazy=True)


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    issued_on = db.Column(db.Date, nullable=False, default=date.today)
    due_on = db.Column(db.Date, nullable=False)
    returned_on = db.Column(db.Date)
    fine = db.Column(db.Float, default=0)

    @property
    def is_active(self):
        return self.returned_on is None

    @property
    def days_overdue(self):
        end_date = self.returned_on or date.today()
        return max(0, (end_date - self.due_on).days)

    @property
    def current_fine(self):
        return self.fine if self.returned_on else self.days_overdue * app.config["FINE_PER_DAY"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("librarian"):
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_positive_int(value, label):
    try:
        number = int(value)
        if number < 1:
            raise ValueError
        return number
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a positive whole number.")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["librarian"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    active_loans = Loan.query.filter_by(returned_on=None).all()
    overdue_loans = [loan for loan in active_loans if loan.days_overdue > 0]
    return render_template(
        "dashboard.html",
        book_count=Book.query.count(),
        member_count=Member.query.count(),
        active_count=len(active_loans),
        overdue_loans=overdue_loans,
    )


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    if request.method == "POST":
        try:
            total = get_positive_int(request.form.get("total_copies"), "Total copies")
            book = Book(
                title=request.form.get("title", "").strip(), author=request.form.get("author", "").strip(),
                isbn=request.form.get("isbn", "").strip(), category=request.form.get("category", "").strip(),
                total_copies=total, available_copies=total,
            )
            if not all([book.title, book.author, book.isbn, book.category]):
                raise ValueError("Please complete every book field.")
            db.session.add(book)
            db.session.commit()
            flash("Book added successfully.", "success")
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            db.session.rollback()
            flash("ISBN must be unique.", "danger")
        return redirect(url_for("books"))

    search = request.args.get("search", "").strip()
    query = Book.query
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(pattern), Book.author.ilike(pattern), Book.category.ilike(pattern), Book.isbn.ilike(pattern)))
    return render_template("books.html", books=query.order_by(Book.title).all(), search=search)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    if book.loans:
        flash("Cannot remove a book that has lending history.", "danger")
    else:
        db.session.delete(book)
        db.session.commit()
        flash("Book removed.", "success")
    return redirect(url_for("books"))


@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    if request.method == "POST":
        try:
            member = Member(name=request.form.get("name", "").strip(), email=request.form.get("email", "").strip().lower(), phone=request.form.get("phone", "").strip())
            if not all([member.name, member.email, member.phone]):
                raise ValueError("Please complete every member field.")
            db.session.add(member)
            db.session.commit()
            flash("Member registered successfully.", "success")
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            db.session.rollback()
            flash("Email address must be unique.", "danger")
        return redirect(url_for("members"))
    return render_template("members.html", members=Member.query.order_by(Member.name).all())


@app.route("/members/<int:member_id>/delete", methods=["POST"])
@login_required
def delete_member(member_id):
    member = db.get_or_404(Member, member_id)
    if member.loans:
        flash("Cannot remove a member that has lending history.", "danger")
    else:
        db.session.delete(member)
        db.session.commit()
        flash("Member removed.", "success")
    return redirect(url_for("members"))


@app.route("/loans", methods=["GET", "POST"])
@login_required
def loans():
    if request.method == "POST":
        try:
            book = db.get_or_404(Book, int(request.form.get("book_id")))
            member = db.get_or_404(Member, int(request.form.get("member_id")))
            days = get_positive_int(request.form.get("loan_days"), "Loan period")
            if book.available_copies < 1:
                raise ValueError("This book is currently unavailable.")
            existing = Loan.query.filter_by(book_id=book.id, member_id=member.id, returned_on=None).first()
            if existing:
                raise ValueError("This member already has this book issued.")
            book.available_copies -= 1
            db.session.add(Loan(book=book, member=member, due_on=date.today() + timedelta(days=days)))
            db.session.commit()
            flash("Book issued successfully.", "success")
        except (ValueError, TypeError) as error:
            flash(str(error), "danger")
        return redirect(url_for("loans"))

    active_loans = Loan.query.filter_by(returned_on=None).order_by(Loan.due_on).all()
    return render_template("loans.html", loans=active_loans, books=Book.query.filter(Book.available_copies > 0).order_by(Book.title).all(), members=Member.query.order_by(Member.name).all())


@app.route("/loans/<int:loan_id>/return", methods=["POST"])
@login_required
def return_book(loan_id):
    loan = db.get_or_404(Loan, loan_id)
    if not loan.is_active:
        flash("This loan has already been closed.", "warning")
    else:
        loan.returned_on = date.today()
        loan.fine = loan.days_overdue * app.config["FINE_PER_DAY"]
        loan.book.available_copies += 1
        db.session.commit()
        flash(f"Book returned. Fine: ₹{loan.fine:.2f}", "success")
    return redirect(url_for("loans"))


@app.route("/history")
@login_required
def history():
    return render_template("history.html", loans=Loan.query.filter(Loan.returned_on.isnot(None)).order_by(Loan.returned_on.desc()).all())


def seed_database():
    if Book.query.count() == 0:
        db.session.add_all([
            Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884", category="Programming", total_copies=3, available_copies=3),
            Book(title="Atomic Habits", author="James Clear", isbn="9780735211292", category="Self Help", total_copies=2, available_copies=2),
        ])
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_database()


if __name__ == "__main__":
    app.run(debug=True)
