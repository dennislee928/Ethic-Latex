---
globs:
  - "**/*snowflake*"
  - "**/snow*.py"
  - "**/snow*.ts"
---

# Snowflake Authentication Corrections

## Account Identifier Confusion (Critical)

Snowflake uses TWO different account identifier formats:

| Format | Example | Used For |
|--------|---------|----------|
| **Organization-Account** | `irjoewf-wq46213` | REST API URLs, connection strings |
| **Account Locator** | `NZ90655` | JWT claims (`iss`, `sub`) |

**These are NOT interchangeable!**

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Single `SNOWFLAKE_ACCOUNT` env var | Separate `SNOWFLAKE_ACCOUNT_URL` and `SNOWFLAKE_ACCOUNT_LOCATOR` |
| `irjoewf-wq46213` in JWT iss claim | Account locator (e.g., `NZ90655`) |
| Guessing account format from URL | Run `SELECT CURRENT_ACCOUNT()` to get actual locator |

## Discover Account Locator

```sql
SELECT CURRENT_ACCOUNT();  -- Returns account locator (e.g., NZ90655)
```

Or via snow CLI:
```bash
snow sql -q "SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_REGION()" -c your_connection
```

## JWT Claim Format

```
iss: ACCOUNT_LOCATOR.USERNAME.SHA256:fingerprint
sub: ACCOUNT_LOCATOR.USERNAME
```

**Example:**
```
iss: NZ90655.JEZWEB.SHA256:jpZO6LvU2SpKd8tE61OGfas5ZXpfHloiJd7XHLPDEEA=
sub: NZ90655.JEZWEB
```

## REST API URL Format

Uses org-account format (NOT account locator):
```
https://irjoewf-wq46213.snowflakecomputing.com/api/v2/statements
```

## RSA Key Setup

```bash
# Generate key pair (PKCS#8 format required)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out ~/.snowflake/rsa_key.p8 -nocrypt
openssl rsa -in ~/.snowflake/rsa_key.p8 -pubout -out ~/.snowflake/rsa_key.pub

# Get fingerprint
openssl rsa -in ~/.snowflake/rsa_key.p8 -pubout -outform DER | openssl dgst -sha256 -binary | openssl enc -base64

# Register with Snowflake user
ALTER USER my_user SET RSA_PUBLIC_KEY='MIIBIj...';
```

## Symptoms of Wrong Identifier

- REST API returns 200 but with JWT validation error
- Queries don't appear in Snowflake Query History
- No clear error message indicating which identifier is wrong

**Fix**: Always use `SELECT CURRENT_ACCOUNT()` to get actual account locator.
