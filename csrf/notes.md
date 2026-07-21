# **What is CSRF?**
- Cross-site request forgery (CSRF) is a cyberattack that tricks an authenticated user into executing unintended actions on a web application, such as changing their password or transfering funds. It exploits the browser's tendency to automatically include stored credentials (like session cookies) with every request sent to a website.

# **How the Attack Works**
- For a CSRF attack to succeed, three conditions must be met:
    - Relevant Action: The application performs a state-changing action (e.g., updating user details or buying an item).
    - Session Handling: The app relies completely on cookie-based or browser-handled sessions, meaning no additional re-authentication is required for the action.
    - Predictable Parameters: The attacker can determine the exact URL and parameters required to trigger the specific action.
    - If these conditions are met, an attacker can create a malicious website with a hidden form or script that silently sends a request to the target site on the victim's behalf. Because the user is already logged in, the server processes the request as if the user authorized it.

# **How to Prevent CSRF**
- Developers utilize multiple, overlapping layers of defense to protect web applications from CSRF:
    - Anti-CSRF Tokens: The server generates a unique, unpredictable, and secret token for the user's session. This token is embedded in user forms or API headers. When a request is made, the server verifies if the submitted token matches the one in the user's session.
    - SameSite Cookie Attribute: Setting cookies to SameSite=Strict or SameSite=Lax prevents the browser from sending session cookies in cross-site requests.
    - Custom Request Headers: Frameworks may require requests to include a custom header, which browsers will block during cross-origin requests unless permitted by a strict CORS policy.