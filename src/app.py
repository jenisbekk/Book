from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from library import Library, LibraryError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "library.json"
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.secret_key = "library-management-system"


def get_library():
    return Library.load(DATA_FILE)


def save_library(lib):
    lib.save(DATA_FILE)


@app.route("/")
def index():
    lib = get_library()
    active = [l for l in lib.loans if l.returned is None]
    return render_template("index.html", lib=lib, active_loans=active, overdue=lib.overdue_loans())


@app.route("/books")
def books():
    lib = get_library()
    q = request.args.get("q", "").strip()
    items = lib.search_books(q) if q else list(lib.books.values())
    return render_template("books.html", books=items, q=q)


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        try:
            lib = get_library()
            lib.add_book(request.form["isbn"].strip(), request.form["title"].strip(),
                         request.form["author"].strip(), int(request.form["year"]),
                         int(request.form["copies"]))
            save_library(lib)
            flash("Book added successfully.", "success")
            return redirect(url_for("books"))
        except (LibraryError, ValueError) as e:
            flash(str(e), "error")
    return render_template("book_form.html", book=None)


@app.route("/books/<isbn>/edit", methods=["GET", "POST"])
def edit_book(isbn):
    lib = get_library()
    if isbn not in lib.books:
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    book = lib.books[isbn]
    if request.method == "POST":
        try:
            copies = int(request.form["copies"])
            lib.update_book(isbn, title=request.form["title"].strip(), author=request.form["author"].strip(),
                            year=int(request.form["year"]), copies=copies)
            save_library(lib)
            flash("Book updated successfully.", "success")
            return redirect(url_for("books"))
        except (LibraryError, ValueError) as e:
            flash(str(e), "error")
    return render_template("book_form.html", book=book)


@app.post("/books/<isbn>/delete")
def delete_book(isbn):
    try:
        lib = get_library()
        lib.remove_book(isbn)
        save_library(lib)
        flash("Book removed.", "success")
    except LibraryError as e:
        flash(str(e), "error")
    return redirect(url_for("books"))


@app.route("/readers")
def readers():
    lib = get_library()
    return render_template("readers.html", readers=list(lib.readers.values()))


@app.route("/readers/add", methods=["GET", "POST"])
def add_reader():
    if request.method == "POST":
        try:
            lib = get_library()
            lib.register_reader(request.form["card_id"].strip(), request.form["name"].strip(), request.form["contact"].strip())
            save_library(lib)
            flash("Reader registered successfully.", "success")
            return redirect(url_for("readers"))
        except LibraryError as e:
            flash(str(e), "error")
    return render_template("reader_form.html")


@app.route("/issue", methods=["GET", "POST"])
def issue():
    lib = get_library()
    if request.method == "POST":
        try:
            loan = lib.issue_book(request.form["isbn"], request.form["card_id"])
            save_library(lib)
            flash(f"Book issued. Return by {loan.due}.", "success")
            return redirect(url_for("history"))
        except LibraryError as e:
            flash(str(e), "error")
    available_books = [b for b in lib.books.values() if b.available > 0]
    return render_template("issue.html", books=available_books, readers=list(lib.readers.values()))


@app.route("/return", methods=["GET", "POST"])
def return_book():
    lib = get_library()
    if request.method == "POST":
        try:
            lib.return_book(request.form["isbn"], request.form["card_id"])
            save_library(lib)
            flash("Book returned successfully.", "success")
            return redirect(url_for("history"))
        except LibraryError as e:
            flash(str(e), "error")
    active = [l for l in lib.loans if l.returned is None]
    return render_template("return.html", loans=active, books=lib.books, readers=lib.readers)


@app.route("/history")
def history():
    lib = get_library()
    card = request.args.get("card", "").strip() or None
    loans = lib.history(card)
    return render_template("history.html", loans=loans, books=lib.books, readers=lib.readers, card=card or "")


@app.route("/overdue")
def overdue():
    lib = get_library()
    return render_template("overdue.html", loans=lib.overdue_loans(), books=lib.books, readers=lib.readers)


if __name__ == "__main__":
    app.run(debug=True)
