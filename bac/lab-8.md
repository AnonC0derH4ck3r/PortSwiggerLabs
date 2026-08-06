# User ID Controlled by Request Parameter with Password Disclosure

## Description

This lab has a user account page that contains the current user's existing password, prefilled in a masked input.

To solve the lab, retrieve the administrator's password, then use it to delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the account page

I accessed the lab, which showed a page listing several products. I clicked on `My account`, which took me to `/my-account?id=wiener`. The response included the following change password form:

```html
<form class="login-form" action="/my-account/change-password" method="POST">
    <br/>
    <label>Password</label>
    <input required type="hidden" name="csrf" value="0ilhODuXL1kl3BnTWpWF0Vro66KLcFzC">
    <input required type=password name=password value='peter'/>
    <button class='button' type='submit'> Update password </button>
</form>
```

Although the `password` field is rendered as a masked `type=password` input in the browser, its `value` attribute contains the account's actual current password in clear text within the HTML source (`peter`, matching the login credentials used).

### Step 2: Apply the same id manipulation

Based on the pattern from the earlier user ID horizontal privilege escalation labs, I changed the `id` parameter in the request from `wiener` to `administrator`:

```
GET /my-account?id=administrator
```

The response rendered the same change password form, but this time prefilled with the administrator account's actual password:

```
2iol18xfiw7ugk9n02tl
```

### Step 3: Log in as administrator

I logged out of `wiener`'s session and logged in using the disclosed credentials:

```
administrator : 2iol18xfiw7ugk9n02tl
```

### Step 4: Delete the user carlos

With administrator access, I navigated to the admin functionality and deleted the user `carlos`, which solved the lab.

## Root Cause

The account page embeds the currently viewed user's real password directly into the HTML as the `value` attribute of a password input field, intending only to visually mask it in the rendered page. Combined with the same missing object-level authorization check seen in the related labs, where the `id` parameter is trusted without verifying it belongs to the requesting user, this allows any authenticated user to retrieve another user's plaintext password simply by changing the `id` parameter, including the administrator's.

## Remediation

- Never populate a password field, or any sensitive credential, with the user's actual current password. Leave such fields empty and only accept a new value on submission.
- Enforce object-level authorization checks so that a user can only view or modify their own account, regardless of the value supplied in an `id` parameter.
- Assume that any value rendered into a masked input field on the client is still fully visible in the underlying HTML source and page response.