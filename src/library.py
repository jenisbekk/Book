"""Core logic of the Library Management System (standard library only)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

LOAN_DAYS = 14


class LibraryError(Exception):
    """Raised when an operation violates a library rule."""


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    year: int
    copies: int
    available: int


@dataclass
class Reader:
    card_id: str
    name: str
    contact: str


@dataclass
class Loan:
    isbn: str
    card_id: str
    issued: str
    due: str
    returned: str | None = None


class Library:
    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.readers: dict[str, Reader] = {}
        self.loans: list[Loan] = []

    # ---- books -------------------------------------------------------
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int = 1) -> Book:
        if isbn in self.books:
            raise LibraryError(f"Book with ISBN {isbn} already exists")
        if copies < 1:
            raise LibraryError("Copies must be at least 1")
        book = Book(isbn, title, author, year, copies, copies)
        self.books[isbn] = book
        return book

    def update_book(self, isbn: str, title=None, author=None, year=None, copies=None) -> Book:
        book = self._get_book(isbn)
        if copies is not None:
            borrowed = book.copies - book.available
            if copies < max(borrowed, 1):
                raise LibraryError("Copies cannot be less than borrowed books (and at least 1)")
            book.copies = copies
            book.available = copies - borrowed
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if year is not None:
            book.year = year
        return book

    def remove_book(self, isbn: str) -> None:
        self._get_book(isbn)
        if any(l.isbn == isbn and l.returned is None for l in self.loans):
            raise LibraryError("Cannot remove a book that is currently borrowed")
        del self.books[isbn]

    def search_books(self, query: str) -> list[Book]:
        q = query.strip().lower()
        return [
            b for b in self.books.values()
            if q in b.title.lower() or q in b.author.lower() or q in b.isbn.lower()
        ]

    # ---- readers -----------------------------------------------------
    def register_reader(self, card_id: str, name: str, contact: str) -> Reader:
        if card_id in self.readers:
            raise LibraryError(f"Reader with card {card_id} already exists")
        reader = Reader(card_id, name, contact)
        self.readers[card_id] = reader
        return reader

    # ---- loans -------------------------------------------------------
    def issue_book(self, isbn: str, card_id: str, today: date | None = None) -> Loan:
        today = today or date.today()
        book = self._get_book(isbn)
        self._get_reader(card_id)
        if book.available < 1:
            raise LibraryError("No copies available")
        if self._active_loan(isbn, card_id):
            raise LibraryError("Reader already has this book")
        loan = Loan(isbn, card_id, today.isoformat(), (today + timedelta(days=LOAN_DAYS)).isoformat())
        book.available -= 1
        self.loans.append(loan)
        return loan

    def return_book(self, isbn: str, card_id: str, today: date | None = None) -> Loan:
        today = today or date.today()
        loan = self._active_loan(isbn, card_id)
        if loan is None:
            raise LibraryError("No active loan found for this book and reader")
        loan.returned = today.isoformat()
        self.books[isbn].available += 1
        return loan

    def overdue_loans(self, today: date | None = None) -> list[Loan]:
        today = (today or date.today()).isoformat()
        return [l for l in self.loans if l.returned is None and l.due < today]

    def history(self, card_id: str | None = None) -> list[Loan]:
        if card_id is None:
            return list(self.loans)
        return [l for l in self.loans if l.card_id == card_id]

    # ---- storage -----------------------------------------------------
    def save(self, path: str | Path) -> None:
        data = {
            "books": [asdict(b) for b in self.books.values()],
            "readers": [asdict(r) for r in self.readers.values()],
            "loans": [asdict(l) for l in self.loans],
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Library":
        lib = cls()
        path = Path(path)
        if not path.exists():
            return lib
        data = json.loads(path.read_text(encoding="utf-8"))
        lib.books = {b["isbn"]: Book(**b) for b in data.get("books", [])}
        lib.readers = {r["card_id"]: Reader(**r) for r in data.get("readers", [])}
        lib.loans = [Loan(**l) for l in data.get("loans", [])]
        return lib

    # ---- helpers -----------------------------------------------------
    def _get_book(self, isbn: str) -> Book:
        if isbn not in self.books:
            raise LibraryError(f"Book with ISBN {isbn} not found")
        return self.books[isbn]

    def _get_reader(self, card_id: str) -> Reader:
        if card_id not in self.readers:
            raise LibraryError(f"Reader with card {card_id} not found")
        return self.readers[card_id]

    def _active_loan(self, isbn: str, card_id: str) -> Loan | None:
        for loan in self.loans:
            if loan.isbn == isbn and loan.card_id == card_id and loan.returned is None:
                return loan
        return None
