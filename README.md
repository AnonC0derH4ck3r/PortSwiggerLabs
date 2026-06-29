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
| [xss/lab-2.md](./xss/lab-2.md)   | Stored XSS into HTML context with nothing encoded                                   |
| [xss/lab-3.md](./xss/lab-3.md)   | DOM XSS in document.write sink using source location.search                         |
| [xss/lab-4.md](./xss/lab-4.md)   | DOM XSS in innerHTML sink using source location.search                              |
| [xss/lab-5.md](./xss/lab-5.md)   | DOM XSS in jQuery anchor href attribute sink using location.search source           |
| [xss/lab-6.md](./xss/lab-6.md)   | DOM XSS in jQuery selector sink using a hashchange event                            |
| [xss/lab-7.md](./xss/lab-7.md)   | Reflected XSS into attribute with angle brackets HTML-encoded                       |
| [xss/lab-8.md](./xss/lab-8.md)   | Stored XSS into anchor href attribute with double quotes HTML-encoded               |
| [xss/lab-9.md](./xss/lab-9.md)   | Reflected XSS into a JavaScript string with angle brackets HTML encoded             |
| [xss/lab-10.md](./xss/lab-10.md)   | DOM XSS in document.write sink using source location.search inside a select element               |
| [xss/lab-11.md](./xss/lab-11.md)   | DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded               |
| [xss/lab-12.md](./xss/lab-12.md)   | Reflected DOM XSS                                                                 |
| [xss/lab-13.md](./xss/lab-13.md)   | Stored DOM XSS                                                                 |

## OS Command Injection

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [os-ce/lab-1.md](./os-ce/lab-1.md)   | OS command injection, simple case                                               |
| [os-ce/lab-2.md](./os-ce/lab-2.md)   | Blind OS command injection with time delays                                     |
| [os-ce/lab-3.md](./os-ce/lab-3.md)   | Blind OS command injection with output redirection                              |

## GraphQL Vulnerabilities

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [graphql/lab-1.md](./graphql/lab-1.md)   | Accessing private GraphQL posts                                               |
| [graphql/lab-2.md](./graphql/lab-2.md)   | Accidental exposure of private GraphQL fields                                  |

## HTTP Header Attacks

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [hha/lab-1.md](./hha/lab-1.md)   | Basic password reset poisoning                                               |
| [hha/lab-2.md](./hha/lab-2.md)   | Host header authentication bypass                                               |

## JWT Vulnerabilities

| Lab                              | Topic                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| [jwt/lab-1.md](./jwt/lab-1.md)   | JWT authentication bypass via unverified signature                                  |
| [jwt/lab-2.md](./jwt/lab-2.md)   | JWT authentication bypass via flawed signature verification                         |

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
