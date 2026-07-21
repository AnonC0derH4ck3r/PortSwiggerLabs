# **What Are CRLF Injection Attacks?**
- A CRLF injection attack is one of several types of injection attacks. It can be used to escalate to more malicious attacks such as Cross-site Scripting (XSS), page injection, web cache poisoning, cache-based defacement, and more. A CRLF injection vulnerability exists if an attacker can inject the CRLF characters into a web application, for example using a user input form or an HTTP request.
- The CRLF abbreviation refers to Carriage Return and Line Feed. CR and LF are special characters (ASCII 13 and 10 respectively, also referred to as \r\n) that are used to signify the End of Line (EOL). The CRLF sequence is used in operating systems including Windows (but not Linux/UNIX) and Internet protocols including HTTP.
- There are two most common uses of CRLF injection attacks: log poisoning and HTTP response splitting. In the first case, the attacker falsifies log file entries by inserting an end of a line and an extra line. This can be used to hide other attacks or to confuse system administrators. In the second case, CRLF injection is used to add HTTP headers to the HTTP response and, for example, perform an XSS attack that leads to information disclosure. A similar technique, called Email Header Injection, may be used to add SMTP headers to emails.

# **What Is HTTP Response Splitting**
- The HTTP protocol uses the CRLF character sequence to signify where one header ends and another begins. It also uses it to signify where headers end and the website content begins.
- If the attacker inserts a single CRLF, they can add a new header. If it is, for example, a Location header, the attacker can redirect the user to a different website. Criminals may use this technique for phishing or defacing. This technique is often called HTTP header injection.
- If the attacker inserts a double CRLF, they can prematurely terminate HTTP headers and inject content before the actual website content. The injected content can contain JavaScript code. It can also be formulated so that the actual website content coming from the web server is ignored by the web browser. This is how HTTP response splitting is used in combination with Cross-site Scripting (XSS).
- The following simplified example uses CRLF to:
    1. Add a fake HTTP response header: Content-Length: 0. This causes the web browser to treat this as a terminated response and begin parsing a new response.
    2. Add a fake HTTP response: HTTP/1.1 200 OK. This begins the new response.
    3. Add another fake HTTP response header: Content-Type: text/html. This is needed for the web browser to properly parse the content.
    4. Add yet another fake HTTP response header: Content-Length: 25. This causes the web browser to only parse the next 25 bytes.
    5. Add page content with an XSS: <script>alert(1)</script>. This content has exactly 25 bytes.
    6. Because of the Content-Length header, the web browser ignores the original content that comes from the web server.
```url
http://www.example.com/somepage.php?page=%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0aContent-Length:%2025%0d%0a%0d%0a%3Cscript%3Ealert(1)%3C/script%3E
```

# **Finding and Mitigating CRLF Injections**
- The impact of CRLF injections may seem to be limited. CRLF injections are not even mentioned in the OWASP top 10 2017 web application security list. However, attackers can effectively use CRLF injections to escalate to much more serious attacks that exploit other web application vulnerabilities. Therefore, you should treat CRLF injection vulnerabilities seriously.
- CRLF injection vulnerabilities are usually mitigated by web frameworks automatically. Even if the vulnerability is not mitigated, it is very simple to fix:
    - Option 1: Rework your code so that content supplied by the user is never used directly in the HTTP stream.
    - Option 2: Strip any newline characters before passing content into the HTTP header.
    - Option 3: Encode the data that you pass into HTTP headers. This will effectively scramble the CR and LF codes if the attacker attempts to inject them.

# **How to Prevent CRLF Injections**
- CRLF injection vulnerabilities are usually mitigated by web frameworks automatically. Even if the vulnerability is not mitigated, it is very simple to fix.

1. Don’t trust user input
    - Rework your code so that content supplied by the user is never used directly in the HTTP stream.

2. Strip newlines
    - Strip any newline characters before passing content into the HTTP header.

3. Encode data
    - Encode the data that you pass into HTTP headers. This will effectively scramble the CR and LF codes if the attacker attempts to inject them.

4. Scan regularly (with Acunetix)
    - CRLF injections may be introduced by your developers or through external libraries/modules/software. You should regularly scan your web applications using a web vulnerability scanner such as Acunetix. If you use Jenkins, you should install the Acunetix plugin to automatically scan every build.