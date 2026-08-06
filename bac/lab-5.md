# User ID Controlled by Request Parameter

## Description

This lab has a horizontal privilege escalation vulnerability on the user account page.

To solve the lab, obtain the API key for the user `carlos` and submit it as the solution.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the account page

I accessed the lab and clicked on the `My account` page. I logged in using the given credentials `wiener:peter` and was redirected to `/my-account?id=wiener`. This page displayed the username `wiener` along with an API key: `XHxNxPL4CtVn31JVrmJ85w8pcKKr3t2r`.

### Step 2: Identify the controllable parameter

Inspecting the request, the only user-controllable value tied to which account's data was returned was the `id` parameter in the URL itself. There were no other parameters, tokens, or session-bound identifiers involved in determining which account's details were displayed.

### Step 3: Modify the id parameter

I changed the `id` parameter from `wiener` to `carlos`:

```
/my-account?id=carlos
```

The page returned `carlos`'s account details, including their API key, without any authorization check confirming that the currently logged-in user (`wiener`) should be allowed to view another user's data.

### Step 4: Submit the API key

I submitted the API key retrieved for `carlos`, which solved the lab.

## Root Cause

The `/my-account` endpoint determines whose account data to return based solely on the client-supplied `id` parameter, without verifying that the requested `id` belongs to the currently authenticated user. This is a horizontal privilege escalation (broken object-level authorization) vulnerability: any authenticated user can view another user's private data simply by changing an identifier in the request.

## Remediation

- Never derive which resource to return based purely on a client-supplied identifier. Always verify that the requested resource belongs to, or is otherwise accessible by, the currently authenticated user.
- Enforce object-level authorization checks server-side on every request that accesses user-specific data, regardless of whether the user is otherwise authenticated.
- Consider deriving the user's identity from the session itself rather than accepting it as a separate, independently modifiable request parameter.