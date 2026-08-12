# Exploiting origin server normalization for web cache deception

To solve the lab, find the API key for the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

A list of possible delimiter characters is provided to assist with the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

---

## 1. Detection

- Accessed the lab, clicked `My Account`, and logged in with `wiener:peter`. Was redirected to `/my-account` which displayed the username and API key for `wiener`.
- The goal was to get `carlos`'s API key — which would only appear on his `/my-account` page while he's authenticated. The attack vector: trick the cache into storing the contents of `carlos`'s `/my-account` page as if it were a static, publicly cacheable resource, then retrieve it.
- Sent a normal request to `/my-account`:

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

- Checked the response for `X-Cache` and `Cache-Control` headers — neither was present. This is expected: `/my-account` contains sensitive, user-specific content that should never be publicly cached.

---

## 2. Identifying the Cache Boundary

- Checked requests for static resources (e.g. `/resources/js/...`). These responses did include `X-Cache` and `Cache-Control` headers, confirming the cache layer stores anything under the `/resources/` path prefix.
- This suggested the cache's caching rules were path-prefix based: anything starting with `/resources` gets cached; everything else doesn't.

---

## 3. Crafting the Cache Poisoning Path

- Tried requesting `/resources/../my-account` — a path traversal that the origin server would normalise to `/my-account`, serving the account page content. The response did include `X-Cache` and `Cache-Control` headers, confirming the cache layer stored it.
- However, testing the same URL in an incognito browser showed it was being **redirected** to `/my-account`. The browser itself normalises `..` in URLs before sending the request, resolving `/resources/../my-account` to `/my-account` — which bypasses the cache entirely since that path isn't under `/resources/`.
- The fix: URL-encode the `/` in `../` as `%2f`, giving `/resources/..%2fmy-account`. The browser no longer normalises this because `%2f` is not treated as a path separator at the browser level — so the request is sent to the server with the path literally as `/resources/..%2fmy-account`.
- The origin server, however, **does** decode `%2f` back to `/` during path normalisation, resolving the path to `/my-account` and serving the account page. The cache layer sees the incoming path as `/resources/..%2fmy-account` — which starts with `/resources/` — and stores the response under that key.
- This is the discrepancy at the heart of the vulnerability: the **cache** uses the raw, encoded URL as the cache key (treats it as a static resource path), while the **origin server** normalises the encoded path and serves the dynamic `/my-account` content. The same response is stored and served to anyone who requests `/resources/..%2fmy-account`, regardless of their session.

> **Why this works:** Web cache deception relies on a mismatch between what the cache considers "cacheable" and what the origin server actually serves. Here, the cache keys on the literal request path and sees `/resources/..%2fmy-account` as a static file under the resources directory — a cache-worthy path. The origin server decodes the percent-encoded slash, resolves the path traversal, and serves the sensitive `/my-account` page. When `carlos` is tricked into visiting this URL while logged in, the cache stores his authenticated account page response. Any subsequent visitor can then retrieve it from the cache without authentication.

---

## 4. Solve the Challenge

- Crafted an exploit payload that redirects `carlos`'s browser to the poisoned URL, causing the cache to store his authenticated `/my-account` page response:

```html
<script>
document.location = "https://0a0f0088046a7881837b46d00058000c.web-security-academy.net/resources/..%2fmy-account";
</script>
```

- Delivered this to the victim via the exploit server. When `carlos` visited it, his browser was redirected to `/resources/..%2fmy-account`, his authenticated account page was served by the origin and stored by the cache under that path.
- Visited `/resources/..%2fmy-account` unauthenticated — got `carlos`'s account page back from the cache, including his API key:

```
Your username is: carlos
Your API Key is: HiPqEbRe01LvWqFuouBkht1g2Tx2uz2z
```

- Submitted the API key. Lab solved.
