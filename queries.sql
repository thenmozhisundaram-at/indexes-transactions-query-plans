-- Indexes, Transactions and Query Plans
-- Run against the SQLite database created by demo.py.

-- 1. Query before index (EXPLAIN QUERY PLAN should report a table scan).
EXPLAIN QUERY PLAN
SELECT order_id, customer_id, amount, status
FROM orders
WHERE customer_id = 4242;

-- 2. Add an index on the filtered column.
CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

-- 3. Query after index (EXPLAIN QUERY PLAN should report indexed search).
EXPLAIN QUERY PLAN
SELECT order_id, customer_id, amount, status
FROM orders
WHERE customer_id = 4242;

-- 4. Demonstrate transaction rollback.
BEGIN TRANSACTION;
UPDATE orders
SET status = 'cancelled'
WHERE order_id = 1;

-- Inspect the uncommitted value, then undo the change.
SELECT order_id, status
FROM orders
WHERE order_id = 1;

ROLLBACK;

-- Confirm the original value has been restored.
SELECT order_id, status
FROM orders
WHERE order_id = 1;
