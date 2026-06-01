# SQL Injection Vulnerability Allowing Login Bypass

This lab contains a SQL injection vulnerability in the login function.

The goal is to perform a SQL injection attack that logs into the application as the administrator user.

---

## 1. Detection

- Opened the URL and clicked the `My Account` button.
- Captured the `POST` request sent to the `/login` endpoint.
- The request was sending three parameters - `csrf` (the CSRF token), `username`, and `password`.
- Tried breaking the query by inserting a single quote `'` in the `csrf` parameter, but the server returned `"Invalid CSRF token"`. Tried the same in the `username` parameter and got an `Internal Server Error`, confirming the vulnerability exists in the `username` field.

---

## 2. Login Bypass as Administrator

- The objective was to log in as the administrator user. The following payloads were used in the `username` field:
  - `administrator'--+` — comments out the password check entirely, logging in as administrator directly.
  - `administrator' OR 1=1--+` - alternate payload that achieves the same result.
- Both payloads bypass the `password` condition in the backend query, granting access as administrator and solving the lab.