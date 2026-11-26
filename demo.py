import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).with_name("demo.db")
EVIDENCE_PATH = Path(__file__).with_name("evidence.txt")
ROW_COUNT = 100_000


def explain_query_plan(connection):
    return connection.execute(
        """
        EXPLAIN QUERY PLAN
        SELECT order_id, customer_id, amount, status
        FROM orders
        WHERE customer_id = ?
        """,
        (4242,),
    ).fetchall()


def timed_query(connection, repetitions=30):
    sql = """
        SELECT order_id, customer_id, amount, status
        FROM orders
        WHERE customer_id = ?
    """
    # Warm up once, then measure repeated executions.
    connection.execute(sql, (4242,)).fetchall()
    started = time.perf_counter()
    for _ in range(repetitions):
        connection.execute(sql, (4242,)).fetchall()
    elapsed_ms = (time.perf_counter() - started) * 1000
    return elapsed_ms / repetitions


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)
    output = []

    def log(line=""):
        print(line)
        output.append(str(line))

    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        rows = (
            (order_id, (order_id * 37) % 10_000,
             round(((order_id * 13) % 50000) / 100, 2),
             "pending" if order_id % 3 == 0 else "complete")
            for order_id in range(1, ROW_COUNT + 1)
        )
        connection.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?)", rows
        )
        connection.commit()

        log("INDEXES, TRANSACTIONS AND QUERY PLANS")
        log("=" * 42)
        log(f"Rows inserted: {ROW_COUNT:,}")
        log("Query: SELECT ... FROM orders WHERE customer_id = 4242")
        log()

        log("1) QUERY PLAN BEFORE INDEX")
        for plan_row in explain_query_plan(connection):
            log(" | ".join(str(value) for value in plan_row))
        before_ms = timed_query(connection)
        log(f"Average query time before index: {before_ms:.4f} ms")
        log()

        log("2) CREATE INDEX AND QUERY PLAN AFTER INDEX")
        connection.execute(
            "CREATE INDEX idx_orders_customer_id ON orders(customer_id)"
        )
        connection.commit()
        connection.execute("ANALYZE")
        for plan_row in explain_query_plan(connection):
            log(" | ".join(str(value) for value in plan_row))
        after_ms = timed_query(connection)
        log(f"Average query time after index:  {after_ms:.4f} ms")
        if after_ms > 0:
            log(f"Speed ratio (before / after): {before_ms / after_ms:.2f}x")
        log()

        log("3) TRANSACTION ROLLBACK")
        original = connection.execute(
            "SELECT status FROM orders WHERE order_id = 1"
        ).fetchone()[0]
        log(f"Status before transaction: {original}")

        connection.execute("BEGIN")
        connection.execute(
            "UPDATE orders SET status = 'cancelled' WHERE order_id = 1"
        )
        inside_transaction = connection.execute(
            "SELECT status FROM orders WHERE order_id = 1"
        ).fetchone()[0]
        log(f"Status inside transaction: {inside_transaction}")

        connection.rollback()
        after_rollback = connection.execute(
            "SELECT status FROM orders WHERE order_id = 1"
        ).fetchone()[0]
        log(f"Status after ROLLBACK: {after_rollback}")
        log(f"Rollback successful: {after_rollback == original}")
        log()
        log("Result: the index changes the query plan, and ROLLBACK")
        log("restores the original row value after an uncommitted update.")

    finally:
        connection.close()

    EVIDENCE_PATH.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"\nEvidence saved to: {EVIDENCE_PATH.name}")


if __name__ == "__main__":
    main()
