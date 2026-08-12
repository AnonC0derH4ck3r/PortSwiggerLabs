# Exploiting cache server normalization for web cache deception

To solve the lab, find the API key for the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

A list of possible delimiter characters is provided to help solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

---

## 1. Detection

- Accessed the lab, clicked `My Account`, and logged in with `wiener:peter`, landing on `/my-account` with `wiener`'s username and API key displayed.
- The goal was to get the API key for `carlos` by tricking the cache into storing his authenticated account page under a URL that looks like a static resource — so it can be read back without authentication.

---

## 2. Understanding the Attack Surface

- This lab is a variant of web cache deception, but the key difference from the previous lab is which component does the normalization — here it's the **cache server** that normalizes encoded path sequences, while the **origin server** treats certain characters as path delimiters.
- The delimiter list was used to probe which characters the origin treats as path terminators. The character `%23` (URL-encoded `#`) was found to be recognized as a delimiter by the origin but **not** by the cache — which is exactly the discrepancy needed.

---

## 3. How the Exploit URL Works

The final exploit URL was:

```
/my-account%23%2f%2e%2e%2fresources
```

Decoding the encoded characters:

```
%23 = #
%2f = /
%2e = .
```

So conceptually the URL reads as:

```
/my-account#/../resources
```

But the origin and the cache interpret this URL very differently:

**Origin server:**
- Treats `%23` (i.e. `#`) as a path delimiter — everything after it is ignored for path resolution.
- Sees: `/my-account` → serves the authenticated account page containing the user's API key.

**Cache server:**
- Does **not** treat `%23` as a delimiter.
- Instead, normalizes the encoded traversal sequence `%2f%2e%2e%2f` into `/../`.
- Resolves `/my-account#/../resources` → `/resources` (a static, cacheable directory).
- Sees: `/resources` → decides this is a cacheable static resource and stores the response.

Putting both perspectives side by side:

| Component | Interprets URL as | Result |
|---|---|---|
| Origin | `/my-account#...` → `#` is a delimiter | Serves `/my-account` (private account page) |
| Cache | `/my-account#/../resources` → normalizes traversal | Resolves to `/resources`, caches the response |

The flow end-to-end:

```
Victim visits /my-account%23%2f%2e%2e%2fresources
        |
        v
     CACHE
     "This normalizes to /resources"
     "It's a static resource — I'll cache this"
        |
        v
     ORIGIN
     "%23 is a delimiter — everything after it is irrelevant"
     "This is /my-account"
        |
        v
     Private /my-account response (with API key)
        |
        v
     CACHE STORES IT under /my-account%23%2f%2e%2e%2fresources
```

**Why `%23` instead of a literal `#`?**

If the URL used an actual `#` character, the victim's browser would treat it as a fragment identifier and strip everything from `#` onwards before sending the request — so the server would only receive `GET /my-account`, defeating the attack entirely. Using `%23` ensures the character is transmitted as part of the HTTP request path, so the origin server receives and decodes it itself.

> **One-line mental model:** The origin asks *"what resource should I serve?"* and answers `/my-account`. The cache asks *"what resource should I cache this under?"* and answers `/resources`. The attacker has tricked the origin into generating private content while tricking the cache into believing that content belongs to a public, cacheable static path.

---

## 4. Solve the Challenge

- Crafted the exploit payload to redirect `carlos` to the specially crafted URL:

```html
<script>
document.location = "https://0a0f0088046a7881837b46d00058000c.web-security-academy.net/my-account%23%2f%2e%2e%2fresources";
</script>
```

- Delivered this to the victim via the exploit server. When `carlos` visited the exploit page, his browser was redirected to `/my-account%23%2f%2e%2e%2fresources`. The origin served his authenticated `/my-account` page; the cache stored that response under the traversal URL.
- Visited `/my-account%23%2f%2e%2e%2fresources` without any session cookie — the cache served back `carlos`'s account page from storage, revealing his API key.
- Submitted the API key. Lab solved.