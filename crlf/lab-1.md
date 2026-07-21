# HTTP request smuggling, confirming a CL.TE vulnerability via differential responses

This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.

To solve the lab, smuggle a request to the back-end server, so that a subsequent request for `/` (the web root) triggers a `404 Not Found` response.

---

## 1. Understanding the Setup

- The lab has a two-server architecture: a **front-end** server that receives incoming requests and forwards them to a **back-end** server. The front-end doesn't support chunked transfer encoding — it reads the request body using the `Content-Length` header. The back-end, however, *does* honour `Transfer-Encoding: chunked`.
- This discrepancy is the root of the CL.TE smuggling class of vulnerabilities. When both headers are present in the same request:
  - The **front-end** uses `Content-Length` to decide where the request ends and forwards what it believes to be a single, complete request to the back-end.
  - The **back-end** uses `Transfer-Encoding: chunked` to parse the body instead. In chunked encoding, the body ends when a chunk of size `0` is encountered. Any bytes that come *after* the zero-chunk are treated by the back-end as the beginning of the **next** request.
- This means an attacker can "smuggle" a partial request into the back-end's request buffer — bytes that the front-end sent as part of one request's body, but that the back-end will interpret as the start of a completely new request.

---

## 2. Crafting the Smuggling Request

- Sent the following request to the target:

```http
POST / HTTP/1.1
Host: 0a2d004b04ed9e4d80b880c400ba007a.web-security-academy.net
Content-Length: 35
Transfer-Encoding: chunked

0

GET /404 HTTP/1.1
X-Ignore: X
```

- Breaking down exactly what's happening here:

  - `Content-Length: 35` — tells the front-end that the body is 35 bytes long. The front-end counts those 35 bytes, considers the request complete, and forwards the entire thing (including the `GET /404` part) to the back-end as one request body.
  - `Transfer-Encoding: chunked` — the back-end uses this header instead and begins reading the body as chunked data. It reads `0`, which is the zero-length terminating chunk, and considers the POST body finished right there.
  - Everything after the `0\r\n\r\n` — that is, `GET /404 HTTP/1.1\r\nX-Ignore: X` — is left sitting in the back-end's TCP buffer, unprocessed. The back-end now treats those leftover bytes as the start of the **next incoming request**.

- When the **next** legitimate request arrives (the browser or the lab's automated checker requesting `/`), the back-end prepends the smuggled `GET /404 HTTP/1.1` prefix to it, effectively turning the innocent `/` request into a request for `/404` — a path that doesn't exist.

> **Why this works:** The front-end and back-end disagree on which header governs the request body boundary. The front-end strips or ignores `Transfer-Encoding` (since it doesn't support chunked encoding) and relies solely on `Content-Length`, so it forwards the full payload as one request. The back-end honours `Transfer-Encoding: chunked` and stops reading the POST body at the zero-chunk, leaving the attacker's smuggled `GET /404` fragment poisoning the connection buffer for the next request.

---

## 3. Solve the Challenge

- Sent the smuggling request above to the server. The back-end's buffer was left containing the partial `GET /404 HTTP/1.1` prefix.
- The next request to arrive at the back-end (a `GET /` for the web root) was prefixed with the smuggled data, causing the back-end to process it as a request for `/404` — a non-existent path.
- The back-end returned a `404 Not Found` in response to what was nominally a request for `/`, confirming the smuggle was successful and solving the lab.