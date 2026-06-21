# PortSwigger Web Security Academy — Solved Labs

This repository contains write-ups and solutions for labs from PortSwigger Web Security Academy.

Each lab includes a step-by-step breakdown covering vulnerability identification, exploitation, and the payloads used to solve the challenge.

---

## Current Coverage

### SQL Injection (SQLi)

* Retrieving hidden data via WHERE clause manipulation
* Authentication bypass
* Database fingerprinting and version enumeration
* Database structure enumeration
* UNION-based data extraction
* And more

---

## Planned Categories

Additional lab categories will be added over time, including:

* Cross-Site Scripting (XSS)
* Cross-Site Request Forgery (CSRF)
* Server-Side Request Forgery (SSRF)
* XML External Entity Injection (XXE)
* Access Control Vulnerabilities
* Authentication Vulnerabilities
* Business Logic Vulnerabilities
* File Upload Vulnerabilities
* Path Traversal
* Deserialization
* Web Cache Poisoning
* And other topics covered by PortSwigger Web Security Academy

---

## Structure

```text
sqli/
├── lab-1.md
├── lab-2.md
├── lab-3.md
├── ...
└── lab-9.md
```

As more categories are completed, the repository will be organized as:

```text
sqli/
xss/
csrf/
ssrf/
xxe/
...
```

---

## SQL Injection Labs (Pending...)

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [sqli/lab-1.md](./sqli/lab-1.md) | SQL injection vulnerability in WHERE clause allowing retrieval of hidden data       |
| [sqli/lab-2.md](./sqli/lab-2.md) | SQL injection vulnerability allowing login bypass                                   |
| [sqli/lab-3.md](./sqli/lab-3.md) | SQL injection attack, querying the database type and version on Oracle              |
| [sqli/lab-4.md](./sqli/lab-4.md) | SQL injection attack, querying the database type and version on MySQL and Microsoft |
| [sqli/lab-5.md](./sqli/lab-5.md) | SQL injection attack, listing database contents on non-Oracle databases             |
| [sqli/lab-6.md](./sqli/lab-6.md) | SQL injection attack, listing database contents on Oracle                           |
| [sqli/lab-7.md](./sqli/lab-7.md) | SQL injection UNION attack, determining the number of columns returned by the query |
| [sqli/lab-8.md](./sqli/lab-8.md) | SQL injection UNION attack, finding a column containing text                        |
| [sqli/lab-9.md](./sqli/lab-9.md) | SQL injection UNION attack, retrieving data from other tables                       |
| [sqli/lab-10.md](./sqli/lab-10.md) | SQL injection UNION attack, retrieving multiple values in a single column                       |
| [sqli/lab-11.md](./sqli/lab-11.md) | Blind SQL injection with time delays                       |
| [sqli/lab-12.md](./sqli/lab-12.md) | Blind SQL injection with time delays and information retrieval                       |

## File Upload Vulnerabilities (Completed)

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [fuv/lab-1.md](./fuv/lab-1.md)   | Remote code execution via web shell upload                                          |
| [fuv/lab-2.md](./fuv/lab-2.md)   | Web shell upload via Content-Type restriction bypass                                          |
| [fuv/lab-3.md](./fuv/lab-3.md)   | Web shell upload via path traversal                                          |
| [fuv/lab-4.md](./fuv/lab-4.md)   | Web shell upload via extension blacklist bypass                                          |
| [fuv/lab-5.md](./fuv/lab-5.md)   | Web shell upload via obfuscated file extension                                          |
| [fuv/lab-6.md](./fuv/lab-6.md)   | Remote code execution via polyglot web shell upload                                          |
| [fuv/lab-7.md](./fuv/lab-7.md)   | Web shell upload via race condition                                          |

## Cross-Site Scripting (XSS) (Completed)

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [xss/lab-1.md](./xss/lab-1.md)   | Reflected XSS into HTML context with nothing encoded                                |

---

## Prerequisites

* Basic understanding of SQL
* Familiarity with HTTP requests
* Burp Suite (Community or Professional)
* A free PortSwigger Web Security Academy account

---

## Disclaimer

These write-ups are intended for educational purposes and should only be used against systems that you own or have explicit permission to test.

---

## Author

**Huzefa Khalil Ahmed Dayanji**
