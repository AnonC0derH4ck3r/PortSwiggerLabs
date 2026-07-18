# Username enumeration via different responses

This lab is vulnerable to username enumeration and password brute-force attacks. It has an account with a predictable username and password, which can be found in the following wordlists:

- [Candidate usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames)
- [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page.

---

## 1. Detection

- Clicked `ACCESS THE LAB` and was presented with a blog page. Clicked `My Account` in the top navigation, which led to a login page.
- Submitted a dummy username `admin` and password `password`, capturing the request in BurpSuite and sending it to Repeater:

```http
POST /login HTTP/2
Host: 0a73008d03d516e58034714400660052.web-security-academy.net
Cookie: session=LDNRobMoaSSe4UtpNVqxB735NOgo18Ff
Content-Length: 32
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a73008d03d516e58034714400660052.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a73008d03d516e58034714400660052.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

username=admin&password=password
```

- Got back:

```html
<p class=is-warning>Invalid username</p>
```

- This was the key observation: the application returns **different error messages** depending on whether the username exists or not — `"Invalid username"` when the username doesn't exist, versus (as discovered later) `"Incorrect password"` when the username is valid but the password is wrong. This difference is enough to enumerate valid usernames.

---

## 2. Username Enumeration via Burp Intruder

- Copied the full username wordlist from [portswigger.net/web-security/authentication/auth-lab-usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames).
- Sent the login request to Burp Intruder, marked `username` as the injection point (`username=§§`), and loaded the wordlist as the payload.
- Ran the attack. Every response came back as `200 OK` with a response body length of `3352` bytes — except for one: the username `athena` returned a response of `3354` bytes.
- Inspecting that response confirmed the difference:
  - All other usernames: `<p class=is-warning>Invalid username</p>`
  - Username `athena`: `<p class=is-warning>Incorrect password</p>`

- This confirmed `athena` was a valid username — the server was now telling us the username existed and only the password was wrong.

> **Why this works:** The application uses two distinct error messages — one for an unknown username and one for a wrong password on a known username — rather than a single generic message like "Invalid username or password." This subtle difference leaks whether a submitted username exists in the system, allowing an attacker to enumerate valid accounts one at a time purely from response content.

---

## 3. Password Brute-force for `athena`

- Copied the password wordlist from [portswigger.net/web-security/authentication/auth-lab-passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords).
- Fixed the username as `athena` in the Intruder request, marked the `password` field as the new injection point, and loaded the password wordlist.
- Ran the attack. Every response returned `200 OK` — except one: the password `nicole` returned a `302 Found` with:

```http
Location: /my-account?id=athena
```

- A `302` redirect to `/my-account` confirmed a successful login.

---

## 4. Solve the Challenge

- Navigated to the login page and submitted the discovered credentials:
  - **Username:** `athena`
  - **Password:** `nicole`
- Was redirected to `/my-account?id=athena`, successfully logged in as `athena`.
- Lab solved.