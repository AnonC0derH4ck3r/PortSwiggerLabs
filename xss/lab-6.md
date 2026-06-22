# DOM XSS in jQuery selector sink using a hashchange event

This lab contains a DOM-based cross-site scripting vulnerability on the home page. It uses jQuery's `$()` selector function to auto-scroll to a given post, whose title is passed via the `location.hash` property.

To solve the lab, deliver an exploit to the victim that calls the `print()` function in their browser.

---

# 1. Understanding the Application

- Accessed the lab and saw a homepage with a bunch of blog posts.
- As per the lab description, the app is supposed to auto-scroll to a blog post if the URL's `#` (hash) value matches one of the post titles.
- Opened dev tools and looked through the page source to find the code responsible for this behavior. Found the following script:

```javascript
$(window).on('hashchange', function(){
    var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
    if (post) post.get(0).scrollIntoView();
});
```

- Breaking this down:
    - It listens for the `hashchange` event, which fires every time the `#` part of the URL changes.
    - When triggered, it takes `window.location.hash`, strips the leading `#` using `.slice(1)`, and URL-decodes it using `decodeURIComponent`.
    - That decoded string gets passed directly into jQuery's `$()` selector as `:contains(...)` to find a matching `<h2>` inside `.blog-list`.
    - If a match is found, it scrolls that element into view using `.scrollIntoView()`.

# 2. Finding the Vulnerability

- At first I was staring at this code trying to figure out how it could be exploitable. There's no `.innerHTML`, no `document.write`, no obvious place where HTML tags can be injected. Looked pretty harmless.
- Then I went and did some research on how jQuery's `$()` function actually works under the hood, and found a pretty weird quirk.

### The jQuery $() Quirk

- When you pass a CSS selector like `$("p")`, jQuery goes and **finds** all `<p>` tags already present in the DOM.
- But if you pass something that looks like an HTML tag, like `$("<p>")`, jQuery doesn't try to find anything. Instead, it **creates** a brand new `<p>` element in memory by calling `document.createElement("p")` behind the scenes.
- This is the key behavior that makes this exploitable.

### Why the Element Executes Without Being Appended

- When I pass `$("<img src=x onerror=print()>")`, jQuery creates a real detached `HTMLImageElement` node in the browser's background memory.
- The moment the browser creates that `<img>` element and sees the `src` attribute, it immediately fires off a network request to fetch the image — even though the element isn't attached to the page yet.
- Since `src=x` is an invalid path, the request fails instantly.
- The browser then fires the `onerror` event handler on that image, running whatever JS is inside it.
- So `print()` executes without the element ever touching the actual DOM.

# 3. Crafting the Payload

- With that understanding, the payload was straightforward. Just pass an `<img>` tag with a broken `src` and an `onerror` handler into the hash:

```
https://[lab-url]/#%3Cimg%20src=x%20onerror=print()%3E
```

- This triggered `print()` in my own browser, confirming the XSS works. But the goal was to get it running in the **victim's** browser, not mine.

# 4. Delivering the Exploit to the Victim

- Went to the exploit server to craft the delivery payload.
- First tried `document.location` redirect, but that didn't solve the lab.
- Then tried a plain `<iframe>` pointing directly to the URL with the hash payload already in it:

```html
<iframe src="https://[lab-url]/#<img src=x onerror=print()>"></iframe>
```

- Didn't work either. The issue here is that when an `<iframe>` loads a page, no `hashchange` event fires because the hash was already part of the URL from the start, not changed after load. The event only triggers when the hash **changes**, not on initial page load.

- The fix was to load the page first with just the `#` and then change the hash after the iframe has loaded, using `onload`:

```html
<iframe src="https://[lab-url]/#" onload="this.src+='<img src=x onerror=print()>'"></iframe>
```

- What this does:
    - The iframe loads the page with an empty hash (`#`).
    - Once the page is fully loaded, `onload` fires and appends `<img src=x onerror=print()>` to the `src`, changing the hash.
    - That hash change triggers the `hashchange` event listener inside the page.
    - jQuery picks up the `<img>` tag, creates the element, browser fires `onerror`, and `print()` runs in the victim's browser.
- Delivered this to the victim via the exploit server and the lab was solved.