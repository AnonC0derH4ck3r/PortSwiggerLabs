# SQL Injection — Solved Labs

This repository contains write-ups and solutions for all SQL injection labs from [PortSwigger Web Security Academy](https://portswigger.net/web-security/sql-injection).

Each lab includes a step-by-step breakdown covering detection, exploitation, and the final payload used to solve it.

---

## What's Covered

- Retrieving hidden data via WHERE clause manipulation
- Subverting application logic
- UNION-based attacks for extracting data from other tables
- Examining the database type and structure
- Blind SQL injection (boolean-based and time-based)
- And more

---

## Structure

Each lab is a standalone markdown file named sequentially.

```
lab-1.md
lab-2.md
lab-3.md
...
```

## Labs

| Lab | Topic |
|-----|-------|
| [lab-1.md](./lab-1.md) | SQL injection vulnerability in WHERE clause allowing retrieval of hidden data |
| [lab-2.md](./lab-2.md) | SQL injection vulnerability allowing login bypass |
| [lab-3.md](./lab-3.md) | SQL injection attack, querying the database type and version on Oracle |
| [lab-4.md](./lab-4.md) | SQL injection attack, querying the database type and version on MySQL and Microsoft |
| [lab-5.md](./lab-5.md) | SQL injection attack, listing database contents on non-Oracle databases |
| [lab-6.md](./lab-6.md) | SQL injection attack, listing the database contents on Oracle |
| [lab-7.md](./lab-7.md) | SQL injection UNION attack, determining the number of columns returned by the query |
| [lab-8.md](./lab-8.md) | SQL injection UNION attack, finding a column containing text |

---

## Prerequisites

- Basic understanding of SQL
- Familiarity with HTTP requests (Burp Suite recommended)
- A free [PortSwigger Academy](https://portswigger.net/web-security) account to follow along

---

## Author
- Huzefa Khalil Ahmed Dayanji
