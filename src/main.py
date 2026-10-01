"""Console interface for the Library Management System."""
from pathlib import Path

from library import Library, LibraryError

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "library.json"

MENU = """
=== Library Management System ===
1. Add book
2. Update book
3. Remove book
4. Search books
5. Register reader
6. Issue book
7. Return book
8. Overdue books
9. Loan history
0. Exit
"""


def ask_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a number.")


def print_books(books) -> None:
    if not books:
        print("Nothing found.")
    for b in books:
        print(f"{b.isbn} | {b.title} | {b.author} | {b.year} | available {b.available}/{b.copies}")


def print_loans(loans) -> None:
    if not loans:
        print("No records.")
    for l in loans:
        status = f"returned {l.returned}" if l.returned else f"due {l.due}"
        print(f"{l.isbn} | reader {l.card_id} | issued {l.issued} | {status}")


def main() -> None:
    lib = Library.load(DATA_FILE)
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                lib.add_book(input("ISBN: "), input("Title: "), input("Author: "),
                             ask_int("Year: "), ask_int("Copies: "))
                print("Book added.")
            elif choice == "2":
                isbn = input("ISBN: ")
                title = input("New title (Enter to skip): ") or None
                author = input("New author (Enter to skip): ") or None
                copies = input("New copies (Enter to skip): ")
                lib.update_book(isbn, title=title, author=author,
                                copies=int(copies) if copies else None)
                print("Book updated.")
            elif choice == "3":
                lib.remove_book(input("ISBN: "))
                print("Book removed.")
            elif choice == "4":
                print_books(lib.search_books(input("Title, author or ISBN: ")))
            elif choice == "5":
                lib.register_reader(input("Card ID: "), input("Full name: "), input("Contact: "))
                print("Reader registered.")
            elif choice == "6":
                loan = lib.issue_book(input("ISBN: "), input("Card ID: "))
                print(f"Issued. Return by {loan.due}.")
            elif choice == "7":
                lib.return_book(input("ISBN: "), input("Card ID: "))
                print("Book returned.")
            elif choice == "8":
                print_loans(lib.overdue_loans())
            elif choice == "9":
                card = input("Card ID (Enter for all): ").strip() or None
                print_loans(lib.history(card))
            elif choice == "0":
                lib.save(DATA_FILE)
                print("Saved. Goodbye!")
                break
            else:
                print("Unknown option.")
                continue
            lib.save(DATA_FILE)
        except (LibraryError, ValueError) as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    main()
