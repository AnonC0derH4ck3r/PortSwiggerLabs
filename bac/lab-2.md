# Unprotected Admin Functionality with Unpredictable URL

## Description

This lab has an unprotected admin panel. It's located at an unpredictable location, but the location is disclosed somewhere in the application.

Solve the lab by accessing the admin panel, and using it to delete the user `carlos`.

## Solution

### Step 1: Explore the application

I accessed the lab, which displayed product details. In the top right corner there was a `My account` option. Clicking it led to a login page. No test credentials were provided for this lab, so the goal was to locate the unpredictable admin panel URL and use it to delete `carlos`, without needing to authenticate as any particular user.

### Step 2: Inspect the front-end source

I inspected the front-end source code of the `/login` page and found the following inline script:

```html
<script>
var isAdmin = false;
if (isAdmin) {
   var topLinksTag = document.getElementsByClassName("top-links")[0];
   var adminPanelTag = document.createElement('a');
   adminPanelTag.setAttribute('href', '/admin-7rpto5');
   adminPanelTag.innerText = 'Admin panel';
   topLinksTag.append(adminPanelTag);
   var pTag = document.createElement('p');
   pTag.innerText = '|';
   topLinksTag.appendChild(pTag);
}
</script>
```

This script checks the client-side `isAdmin` flag. If it were `true`, it would locate the element with class `top-links`, create an anchor element pointing to `/admin-7rpto5`, label it `Admin panel`, and append it to the page's navigation links.

Since `isAdmin` is hardcoded to `false` on this page load, the link is never actually rendered or appended for a normal user. However, the admin panel's URL, `/admin-7rpto5`, is still present in the plaintext JavaScript source sent to every client, regardless of whether the link is displayed. This is a case of relying on client-side logic to hide a sensitive URL, when the URL itself is already exposed in the response body.

### Step 3: Access the disclosed admin panel

I sent a direct request to the disclosed path:

```
GET /admin-7rpto5
```

The admin dashboard loaded directly, with no authentication or authorization check enforced on the endpoint.

### Step 4: Delete the user carlos

The admin panel had a `Delete` button next to each user. I clicked `Delete` for `carlos`, which removed the account and solved the lab.

## Root Cause

The admin panel's URL is unpredictable, but the application discloses it directly in client-side JavaScript that is sent to every visitor, regardless of their privilege level. The decision to show or hide the admin panel link is also made entirely on the client side (`if (isAdmin)`), which has no bearing on whether the endpoint itself is protected. Since the endpoint enforces no server-side authentication or authorization, simply knowing the URL is enough to access it.

## Remediation

- Never rely on obscuring a URL as a substitute for real access control. Enforce authentication and authorization checks server-side on every request to sensitive endpoints.
- Do not embed sensitive paths, feature flags, or privilege-dependent logic in client-side code that is delivered to all users. If a link should only be visible to admins, it should be rendered server-side, only in responses to already-authenticated admin users.
- Treat any conditional client-side rendering logic as informational only, never as an enforcement mechanism, since all client-side code and data is visible to the end user regardless of the condition's outcome.