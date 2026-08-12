# Exploiting origin server normalization for web cache deception

To solve the lab, find the API key for the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

A list of possible delimiter characters is provided to help solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

---

## 1. Detection

- Accessed the lab, clicked `My Account`, and logged in with `wiener:peter`, landing on `/my-account` with `wiener`'s username and API key displayed.
- The goal was to get the API key for `carlos` — meaning the victim's account page needed to be cached and then read back.
- Sent a normal request to `/my-account` and inspected the response headers:

```http
GET /my-account HTTP/2
Host: 0a8200dc0443230b80b78a02008c00b4.web-security-academy.net
Cookie: session=rnYll1Gc1LQgiu8gDN1wxaGxddmWL1n4
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
Referer: https://0a8200dc0443230b80b78a02008c00b4.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

- No `X-Cache` or `Cache-Control` headers were present in the response — expected, since `/my-account` is dynamic, user-specific content and isn't meant to be cached publicly.

---

## 2. Identifying Cacheable Paths

- Checked requests to static asset paths like `/resources/js/` and found that anything under `/resources` returned `X-Cache` and `Cache-Control` headers in the response — confirming the cache layer was storing responses for paths starting with `/resources`.
- The idea: trick the cache into treating a request to `/my-account` as if it were a static resource under `/resources`, so the cache stores the response (which contains the victim's API key) and serves it to anyone who requests the same URL.

---

## 3. Finding the Path Traversal Trick

- First tried `/resources/../my-account` — sending this request returned `X-Cache` and `Cache-Control` response headers, confirming the cache layer was treating this path as cacheable (since it starts with `/resources`).
- However, testing this URL directly in an incognito browser window resulted in a redirect to `/my-account` — the browser normalized the `../` path traversal and resolved it to the actual path before sending the request, defeating the purpose.
- The fix: URL-encode the `/` in `../` as `%2f`, giving `/resources/..%2fmy-account`. The browser doesn't normalize `%2f` into a real `/` before sending the request, so the URL reaches the server as-is. The cache layer sees `/resources/..%2fmy-account` and considers it a cacheable static path. The origin server, however, normalizes the encoded slash and resolves the path traversal, ultimately serving the `/my-account` page content — which then gets cached under that URL.

> **Why this works:** The cache and the origin server handle the URL differently. The cache evaluates the raw URL string and decides whether to cache based on the `/resources` prefix — so `/resources/..%2fmy-account` looks like a static resource path and gets cached. The origin server decodes `%2f` back into `/` and processes `/resources/../my-account` as a path traversal, serving the actual `/my-account` page. The mismatch between how the two components normalize the URL is the core of the vulnerability — the cache stores sensitive, dynamic content under a URL that looks static and is publicly accessible.

---

## 4. Solve the Challenge

- Crafted the exploit payload to redirect the victim (`carlos`) to the path traversal URL, causing their authenticated `/my-account` page to be stored in the cache under that URL:

```html
<script>
document.location = "https://0a0f0088046a7881837b46d00058000c.web-security-academy.net/resources/..%2fmy-account";
</script>
```

- Delivered this to the victim via the exploit server. When `carlos` visited the page, his browser was redirected to `/resources/..%2fmy-account`, which the origin server served as `/my-account` (with his session cookie attached, so his API key was in the response). The cache stored that response.
- Navigated to `/resources/..%2fmy-account` without any session cookie — the cache served back `carlos`'s account page, including his API key.
- Submitted the API key. Lab solved.