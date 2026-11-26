# Indexes, Transactions and Query Plans

A small SQLite project demonstrating:
1. A query plan before and after adding an index.
2. Measured query timings in milliseconds.
3. A transaction rollback that protects stored data.

## Requirements
- Python 3.9 or newer
- No third-party packages

## Run
From this folder:

```bash
python demo.py
```

The script creates a fresh `demo.db`, inserts 100,000 sample orders, runs the same filtered query before and after creating an index, prints the query plans and timings, and demonstrates a rollback.

It also writes the run output to `evidence.txt`. Timings vary by computer and are not guaranteed to match the sample evidence included in this repository.

## What to look for
- **Before index:** the query plan should show a table scan (`SCAN orders`).
- **After index:** the query plan should show an indexed search (`SEARCH orders USING INDEX ...`).
- **Rollback:** the temporary update is undone after `ROLLBACK`; the original status remains unchanged.

## Files
- `demo.py` — complete runnable demonstration.
- `queries.sql` — the SQL statements used in the demonstration.
- `evidence.txt` — sample output from running the script.
- `demo.db` — generated locally when you run the script (not required in GitHub).

## GitHub submission
Create a **public** repository, upload these files, and submit the repository URL. You can name the repository `indexes-transactions-query-plans`.
