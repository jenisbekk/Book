# Library Management System — Web Version

A Flask website built on the original Library Management System core logic.

## Run on Windows

```powershell
cd library-management-system
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python src\app.py
```

Open **http://127.0.0.1:5000** in your browser.

Data is stored in `data/library.json`.

## Features
- Add, edit, remove and search books
- Register readers
- Issue books for 14 days
- Return books
- Overdue list
- Loan history
- JSON persistence
## Author

Zhenisbek Umaraliev
Variant: 2
