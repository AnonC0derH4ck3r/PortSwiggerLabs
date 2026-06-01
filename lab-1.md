# SQL Injection Vulnerability in WHERE Clause — Retrieving Hidden Data

This lab contains a SQL injection vulnerability in the product category filter. When the user selects a category, the application executes a query like:

```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```

The goal is to perform a SQL injection attack that causes the application to display one or more unreleased products.

---

## 1. Detection

- Opened the URL and clicked the `Pets` button under **Refine your search**.
- Captured the `GET` request sent to `/filter?category=Pets`.
- Appended `"` after `Pets` to probe for errors — no response. Tried `'` instead, which returned an `Internal Server Error`, indicating that user input is not sanitized and the backend likely isn't using prepared statements. This confirms the category value is wrapped in single quotes inside the backend query.
- Tested `Pets' AND 1=1--+` — returned results. Switching to `Pets' AND 1=2--+` returned nothing, since `1=2` is always false. Further tested `Pets' OR 1=1--+` — returned results, and `Pets' OR 1=2--+` returned none. This confirms SQL injection exists.

---

## 2. Extracting Column Count

- With injection confirmed, the next step was determining how many columns the query returns. Two approaches were used: `ORDER BY` and `UNION`.
- **ORDER BY approach** — `Pets' ORDER BY 1--+` returned results normally. Incrementing the value (`2`, `3`, `4`...) until `Pets' ORDER BY 9--+` threw an `Internal Server Error`, narrowing the column count down.
- **UNION approach** — `Pets' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--+` returned no error. Adding a ninth `NULL` caused an error, confirming exactly **8 columns**. Since the original query uses `SELECT *`, this means the `products` table has 8 columns.

---

## 3. Extracting Hidden Products

- With the column count confirmed, the objective was to bypass the `AND released = 1` condition.
- **Payload** — `Gifts'--+` comments out everything after `category = 'Gifts'`, causing the `AND released = 1` condition to never execute. This alone reveals hidden products under the Gifts category.
- **Lab solution** — `Gifts' OR 1=1--+` causes the query to return all products across all categories regardless of their `released` value, which solved the lab.
