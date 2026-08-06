# User Role Controlled by Request Parameter

## Description

This lab has an admin panel at `/admin`, which identifies administrators using a forgeable cookie.

Solve the lab by accessing the admin panel and using it to delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and capture the request

I accessed the lab and clicked on the `My account` page. I logged in using the given credentials `wiener:peter`. After a successful login, I was redirected to `/my-account?id=wiener`.

I captured this request in Burp Suite and sent it to Repeater:

```http
GET /my-account?id=wiener HTTP/2
Host: 0a8100c3042d818c82cc9206006d00f2.web-security-academy.net
Cookie: Admin=false; session=7zH6HyAn4aCGvCyZCoi57A4bAyJ8dhbg
Cache-Control: max-age=0
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Referer: https://0a8100c3042d818c82cc9206006d00f2.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

A cookie named `Admin` stood out, currently set to `false`.

### Step 2: Test whether the cookie controls access

This raised the question of whether the server was trusting this client-controlled cookie to make an access control decision, rather than deriving the user's role from server-side state tied to the authenticated session.

To test this, I changed the cookie value from `false` to `true` and replayed the request:

```http
Cookie: Admin=true; session=7zH6HyAn4aCGvCyZCoi57A4bAyJ8dhbg
```

The response confirmed the theory. It now included a link to the admin panel:

```html
<a href="/admin">Admin panel</a>
```

### Step 3: Access the admin panel

With the `Admin` cookie still set to `true`, I visited `/admin` and gained access to the admin dashboard.

### Step 4: Delete the user carlos

From the admin panel, I located the delete link for `carlos`:

```html
<span>carlos - </span>
<a href="/admin/delete?username=carlos">Delete</a>
```

I sent a request to this path, which deleted the user and solved the lab.

## Root Cause

The application determines whether a user has administrator privileges based on a client-controlled `Admin` cookie, rather than validating the user's role against server-side session data. Since cookies are fully controlled by the client, any user can set `Admin=true` and be treated as an administrator, regardless of their actual privileges.

## Remediation

- Never derive authorization decisions from client-supplied values such as cookies, headers, or request parameters. Role and privilege information must be stored and validated server-side, tied to the authenticated session.
- Enforce access control checks on the server for every request to privileged functionality, independent of any client-supplied flags.
- Treat all client-controlled input, including cookies, as untrusted and potentially adversarial.