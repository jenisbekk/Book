import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from library import Library, LibraryError  # noqa: E402


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.lib = Library()
        self.lib.add_book("111", "Abai Zholy", "Mukhtar Auezov", 1942, 2)
        self.lib.add_book("222", "Clean Code", "Robert Martin", 2008, 1)
        self.lib.register_reader("R1", "Zhenisbek", "+7 700 000 00 00")

    def test_duplicate_book(self):
        with self.assertRaises(LibraryError):
            self.lib.add_book("111", "X", "Y", 2000)

    def test_search(self):
        self.assertEqual(len(self.lib.search_books("clean")), 1)
        self.assertEqual(len(self.lib.search_books("auezov")), 1)
        self.assertEqual(len(self.lib.search_books("222")), 1)
        self.assertEqual(self.lib.search_books("zzz"), [])

    def test_issue_and_return(self):
        self.lib.issue_book("222", "R1")
        self.assertEqual(self.lib.books["222"].available, 0)
        self.lib.return_book("222", "R1")
        self.assertEqual(self.lib.books["222"].available, 1)

    def test_no_copies_left(self):
        self.lib.register_reader("R2", "Aigerim", "a@mail.kz")
        self.lib.issue_book("222", "R1")
        with self.assertRaises(LibraryError):
            self.lib.issue_book("222", "R2")

    def test_same_book_twice(self):
        self.lib.issue_book("111", "R1")
        with self.assertRaises(LibraryError):
            self.lib.issue_book("111", "R1")

    def test_overdue(self):
        long_ago = date.today() - timedelta(days=30)
        self.lib.issue_book("111", "R1", today=long_ago)
        self.assertEqual(len(self.lib.overdue_loans()), 1)
        self.lib.return_book("111", "R1")
        self.assertEqual(self.lib.overdue_loans(), [])

    def test_remove_borrowed_book(self):
        self.lib.issue_book("111", "R1")
        with self.assertRaises(LibraryError):
            self.lib.remove_book("111")

    def test_update_copies(self):
        self.lib.issue_book("111", "R1")
        self.lib.update_book("111", copies=5)
        self.assertEqual(self.lib.books["111"].available, 4)
        with self.assertRaises(LibraryError):
            self.lib.update_book("111", copies=0)

    def test_save_and_load(self):
        self.lib.issue_book("111", "R1")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lib.json"
            self.lib.save(path)
            loaded = Library.load(path)
        self.assertEqual(len(loaded.books), 2)
        self.assertEqual(len(loaded.loans), 1)
        self.assertEqual(loaded.books["111"].available, 1)


if __name__ == "__main__":
    unittest.main()
