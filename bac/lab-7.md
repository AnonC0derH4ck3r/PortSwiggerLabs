# User ID Controlled by Request Parameter with Data Leakage in Redirect

## Description

This lab contains an access control vulnerability where sensitive information is leaked in the body of a redirect response.

To solve the lab, obtain the API key for the user `carlos` and submit it as the solution.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the account page

I clicked `Access the lab`, which showed a page listing several products. I clicked `My account` and logged in using the given credentials `wiener:peter`. After logging in, I was redirected to `/my-account?id=wiener`, which displayed `wiener`'s account information.

I captured the request in Burp Suite:

```http
GET /my-account?id=wiener HTTP/2
Host: 0afa000c03ba4c3e818b5cd2005200b8.web-security-academy.net
Cookie: session=wAreTcdzfX2YJr745RtlWtPCeI1fX3OA
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
Referer: https://0afa000c03ba4c3e818b5cd2005200b8.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

The only value in the request tied to which account's data gets returned was the `id` parameter. No other cookies or parameters appeared modifiable or predictable.

### Step 2: Request another user's id

I changed the `id` parameter from `wiener` to `carlos` and sent the request through Burp Repeater:

```
GET /my-account?id=carlos
```

Unlike the earlier labs in this series, requesting another user's `id` while authenticated as `wiener` does trigger the server's access control, and the browser itself would be redirected away (to `/login`) since `wiener` is not authorized to view `carlos`'s account directly.

However, inspecting the raw response in Burp Repeater showed that the redirect response's body was still fully rendered with `carlos`'s account content before the redirect took effect:

```http
<div id=account-content>
    <p>Your username is: carlos</p>
    <div>Your API Key is: UFvlqjpQEJl4ry1RNhvAyfuEdykHUr2X</div><br/>
```

This is the data leakage in redirect the lab title refers to: the server correctly decides to deny access and issue a redirect, but it fails to strip the sensitive response body it had already generated before applying that decision. A browser following the redirect automatically would never display this leaked content, but any tool that inspects the raw HTTP response, such as Burp Repeater, reveals it in full.

### Step 3: Submit the API key

I copied the leaked API key for `carlos` from the redirect response body and submitted it, which solved the lab.

## Root Cause

The access control check for `/my-account` correctly identifies that the requesting user (`wiener`) is not authorized to view another user's (`carlos`'s) account, and issues a redirect in response. However, the sensitive account data, including the API key, is rendered into the response body before the access control decision is enforced, and this body is still transmitted alongside the redirect status code. Since the vulnerability lives in the response body rather than the final rendered page, it is invisible in a normal browser but fully exposed to anyone inspecting the raw HTTP traffic.

## Remediation

- Ensure access control decisions are made before any sensitive data is rendered into a response, not just before the final page is displayed to the browser.
- When denying access and issuing a redirect, the response body should be empty or contain only a generic message, never the data that was being protected.
- Treat all parts of an HTTP response, not just what is rendered visually by a browser, as potentially exposed to an attacker.