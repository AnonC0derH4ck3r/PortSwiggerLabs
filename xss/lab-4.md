# DOM XSS in `innerHTML` sink using source `location.search`

This lab contains a DOM-based cross-site scripting vulnerability in the search blog functionality. It uses an `innerHTML` sink, which assigns content directly to the page. The `innerHTML` assignment is made with data from `location.search`, which you can control using the website URL.

To solve this lab, perform a cross-site scripting attack that calls the `alert` function.

---

# 1. Detection

- I accessed the lab and went straight to the search bar this time, since the lab title already gave away that it's the search functionality with an `innerHTML` sink.
- Searched for "test" first, just to see how the result gets displayed.
- ![Normal Search](./pocs/poc-4.0.png)
- Page showed `1 search results for 'test'`, with my input reflected inside the message.

# 2. Finding the Sink

- Opened dev tools and went looking through the page source for how the search query is being handled.
- Found the relevant script block pretty quickly:
- ![innerHTML Sink](./pocs/poc-4.1.png)

```javascript
function doSearchQuery(query) {
    document.getElementById('searchMessage').innerHTML = query;
}
var query = (new URLSearchParams(window.location.search)).get('search');
if (query) {
    doSearchQuery(query);
}
```

- Same pattern as the last lab basically. The `query` value comes straight from the `search` parameter in the URL (via `URLSearchParams` on `location.search`), and gets passed to `doSearchQuery`, which assigns it directly to `searchMessage`'s `innerHTML`, no sanitization at all.
- Difference here is the sink itself. Instead of `document.write`, it's `innerHTML`, which behaves a bit differently when it comes to executing scripts.

# 3. First Attempt — Script Tag Didn't Fire

- Since the sink takes raw input and renders it as HTML, my first thought was just to throw a `<script>` tag in there.
- I injected:

```html
<script>alert(1)</script>
```

- The tag did show up in the DOM when I inspected it, sitting right inside the `searchMessage` span.
- ![Script Tag in DOM](./pocs/poc-4.2.png)
- But no alert popped. Nothing happened.
- This makes sense actually, when you assign HTML to `innerHTML`, the browser parses it as markup, but it deliberately does NOT execute any `<script>` tags inside it. That's a built-in browser behavior, `innerHTML` just doesn't run inline scripts even though the tag itself gets added to the DOM.

# 4. Switching the Payload

- Since `<script>` tags are a dead end with `innerHTML`, I needed an HTML element that triggers JavaScript through an event handler instead of an actual `<script>` block.
- Used the classic broken image trick:

```html
<img src=x onerror=alert(1)>
```

- This forces the browser to try loading an image from an invalid source (`x`), which fails, and the `onerror` handler fires as a result, running my JS.
- Checked the DOM and saw the tag had landed properly inside `searchMessage`.
- ![Img Tag in DOM](./pocs/poc-4.3.png)

```html
<span id="searchMessage">
    <img src="x" onerror="alert(1)">
</span>
```

# 5. Triggering an Alert (Lab Solved)

- Sent the final payload through the URL directly:

```
/?search=<img+src%3Dx+onerror%3Dalert%281%29>
```

- This popped the alert box with `1` in it, and the lab marked itself as solved.
- ![Lab Solved](./pocs/poc-4.4.png)