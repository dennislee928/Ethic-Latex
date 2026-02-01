---
globs: ["**/snowflake*.ts", "**/snowflake*.py", "**/*snowflake*", "**/wrangler.jsonc", "**/.env*"]
---

# Snowflake JWT Key-Pair Authentication

Snowflake REST API authentication requires careful handling of account identifiers. They have TWO different formats used in different contexts.

## Account Identifier Formats

| Format | Example | Used For |
|--------|---------|----------|
| **Organization-Account** | `irjoewf-wq46213` | REST API URL subdomain |
| **Account Locator** | `NZ90655` | JWT claims (`iss`, `sub`) |

**Critical**: These are NOT interchangeable. Using org-account in JWT claims causes silent auth failures.

## How to Discover Your Account Locator

```sql
SELECT CURRENT_ACCOUNT();  -- Returns: NZ90655
```

Or via snow CLI:
```bash
snow sql -q "SELECT CURRENT_ACCOUNT()" -c your_connection
```

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Single `SNOWFLAKE_ACCOUNT` env var | Separate `SNOWFLAKE_ACCOUNT_URL` and `SNOWFLAKE_ACCOUNT_LOCATOR` |
| `irjoewf-wq46213` in JWT iss claim | Account locator (e.g., `NZ90655`) |
| Guessing account format from URL | Run `SELECT CURRENT_ACCOUNT()` to get actual locator |

## JWT Claim Format

```
iss: ACCOUNT_LOCATOR.USERNAME.SHA256:fingerprint
sub: ACCOUNT_LOCATOR.USERNAME
```

**Example**:
```
iss: NZ90655.JEZWEB.SHA256:jpZO6LvU2SpKd8tE61OGfas5ZXpfHloiJd7XHLPDEEA=
sub: NZ90655.JEZWEB
```

## REST API URL Format

Uses org-account format (NOT account locator):
```
https://irjoewf-wq46213.snowflakecomputing.com/api/v2/statements
```

## Configuration Pattern

```typescript
// In wrangler.jsonc vars
"SNOWFLAKE_ACCOUNT_URL": "irjoewf-wq46213",      // For REST URLs
"SNOWFLAKE_ACCOUNT_LOCATOR": "NZ90655",          // For JWT claims
"SNOWFLAKE_USER": "JEZWEB",
"SNOWFLAKE_PUBLIC_KEY_FP": "SHA256:jpZO6LvU2SpKd8tE61OGfas5ZXpfHloiJd7XHLPDEEA=",

// In generateSnowflakeJWT()
const issuer = `${accountLocator}.${user}.${fingerprint}`;

// In executeSnowflakeSQL()
const url = `https://${accountUrl}.snowflakecomputing.com/api/v2/statements`;
```

## RSA Key Setup

```bash
# Generate key pair (PKCS#8 format required)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out ~/.snowflake/rsa_key.p8 -nocrypt
openssl rsa -in ~/.snowflake/rsa_key.p8 -pubout -out ~/.snowflake/rsa_key.pub

# Get fingerprint for JWT claims
openssl rsa -in ~/.snowflake/rsa_key.p8 -pubout -outform DER | openssl dgst -sha256 -binary | openssl enc -base64

# Add public key to Snowflake user (in Snowflake worksheet)
ALTER USER JEZWEB SET RSA_PUBLIC_KEY='MIIBIj...';
```

## Debugging with snow CLI

The `snow` CLI is useful for verifying credentials work before debugging REST API:

```bash
# Test connection
snow connection test -c your_connection

# Discover actual account values
snow sql -q "SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_REGION()" -c your_connection
```

## Symptom of Wrong Account Identifier

- REST API returns 200 but with JWT validation error
- Queries don't appear in Snowflake Query History
- No clear error message indicating which identifier is wrong

**Fix**: Always use `SELECT CURRENT_ACCOUNT()` to get the actual account locator for JWT claims.
