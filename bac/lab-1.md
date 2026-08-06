# Unprotected Admin Functionality

## Description

This lab has an unprotected admin panel.

Solve the lab by deleting the user `carlos`.

## Solution

### Step 1: Explore the application

I accessed the lab, which displayed a list of blog posts. In the top right corner there was a `My account` option. Clicking it led to a login page. The lab did not provide any credentials, so logging in with a known account such as `wiener` was not an option.

### Step 2: Attempt to guess the admin panel path

I tried a few common variations of admin panel paths directly, including:

```
/admin
/admin-login
/admin-panel
/administrator
```

None of these returned a valid page.

### Step 3: Check robots.txt

I then checked whether the application exposed a `robots.txt` file. This file is normally used to instruct search engine crawlers which paths they should and should not index, based on the crawler's user agent. However, since it explicitly lists paths the site owner wants hidden from search engines, it can also leak the existence of sensitive or unlinked pages to an attacker.

I requested it directly:

```http
GET /robots.txt HTTP/2
```

Response:

```http
HTTP/2 200 OK
Content-Type: text/plain; charset=utf-8
Set-Cookie: session=WyFEfuyw06HwdUJJuH54uZNzADfXsO6j; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 45

User-agent: *
Disallow: /administrator-panel
```

The `Disallow` entry revealed a hidden path: `/administrator-panel`.

### Step 4: Access the admin panel

I sent a request to the disclosed path:

```
GET /administrator-panel
```

The admin dashboard loaded directly, with no authentication or authorization check in place.

### Step 5: Delete the user carlos

The admin panel had an option to delete users. I selected the delete option for `carlos`, which removed the account and solved the lab.

## Root Cause

The admin panel at `/administrator-panel` performs no authentication or authorization checks. Access control relies entirely on the URL being unlinked and unpublished ("security through obscurity"), rather than being properly enforced server-side. Listing the path in `robots.txt` to keep it out of search engine indexes also had the side effect of disclosing its existence to anyone who requested the file directly.

## Remediation

- Enforce proper authentication and authorization checks on all administrative functionality, independent of whether the URL is publicly linked.
- Do not rely on `robots.txt`, obscure paths, or lack of navigation links as a substitute for access control, since these are trivially discoverable.
- If sensitive paths must be excluded from search engines, consider that `robots.txt` itself is publicly readable, and ensure the underlying resource is still properly protected regardless.