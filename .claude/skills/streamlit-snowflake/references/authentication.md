# Snowflake Authentication Patterns

Password-only authentication is being deprecated. This guide covers modern authentication methods.

## Deprecation Timeline

| Milestone | Date | Requirement |
|-----------|------|-------------|
| Milestone 1 | Sept 2025 - Jan 2026 | MFA required for Snowsight users with password auth |
| Milestone 2 | May - July 2026 | All new users must use MFA |
| Milestone 3 | Aug - Oct 2026 | All users must use MFA or alternative auth |

**Recommendation:** Migrate to key-pair or OAuth before Oct 2026.

## Authentication Methods

### 1. Key-Pair Authentication (Recommended for Service Accounts)

Best for: CI/CD pipelines, automated deployments, service accounts

#### Generate Key Pair

```bash
# Generate private key (with passphrase)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8

# Generate public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# For unencrypted private key (not recommended for production)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
```

#### Assign Public Key to User

```sql
ALTER USER my_service_user SET RSA_PUBLIC_KEY='MIIBIjANBgkq...';
```

#### Use in Python

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector

# Load private key
with open("rsa_key.p8", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password="your_passphrase".encode(),  # Remove if unencrypted
        backend=default_backend()
    )

# Connect
conn = snowflake.connector.connect(
    account="your_account",
    user="my_service_user",
    private_key=private_key,
    warehouse="my_warehouse",
    database="my_database",
    schema="my_schema"
)
```

#### Use in Snowflake CLI

```bash
# In connections.toml (~/.snowflake/connections.toml)
[my_connection]
account = "your_account"
user = "my_service_user"
authenticator = "SNOWFLAKE_JWT"
private_key_path = "/path/to/rsa_key.p8"
private_key_passphrase = "your_passphrase"  # Or use env var
```

### 2. OAuth Client Credentials (Recommended for M2M)

Best for: Machine-to-machine communication, API integrations

#### Create Security Integration

```sql
-- Create OAuth integration
CREATE OR REPLACE SECURITY INTEGRATION oauth_integration
  TYPE = OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = 'https://localhost'
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_REFRESH_TOKEN_VALIDITY = 86400;

-- Get client ID and secret
SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('OAUTH_INTEGRATION');
```

#### Use in Python

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account="your_account",
    authenticator="oauth",
    token="your_access_token",
    warehouse="my_warehouse"
)
```

### 3. Workload Identity Federation (Cloud-Native)

Best for: Apps running on AWS/Azure/GCP with native identity

#### AWS IAM Integration

```sql
-- Create security integration for AWS
CREATE OR REPLACE SECURITY INTEGRATION aws_integration
  TYPE = API_AUTHENTICATION
  AUTH_TYPE = AWS_IAM_ROLE
  ENABLED = TRUE
  AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/SnowflakeRole';
```

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account="your_account",
    authenticator="WORKLOAD_IDENTITY",
    # AWS credentials auto-discovered from environment
)
```

#### Azure Managed Identity

```sql
CREATE OR REPLACE SECURITY INTEGRATION azure_integration
  TYPE = API_AUTHENTICATION
  AUTH_TYPE = AZURE_AD
  ENABLED = TRUE
  AZURE_AD_APPLICATION_ID = 'your-app-id'
  AZURE_TENANT_ID = 'your-tenant-id';
```

### 4. Personal Access Tokens (PAT)

Best for: Developer access, testing (new in 2025)

```sql
-- Create PAT for a user
ALTER USER my_user SET NETWORK_POLICY = 'my_policy';
-- PATs are managed via Snowsight UI
```

## Snowflake CLI Authentication

### connections.toml

Location: `~/.snowflake/connections.toml`

```toml
# Password auth (deprecated, use for development only)
[dev]
account = "your_account"
user = "your_user"
password = "your_password"  # Better: use env var
warehouse = "my_warehouse"

# Key-pair auth (recommended)
[prod]
account = "your_account"
user = "service_user"
authenticator = "SNOWFLAKE_JWT"
private_key_path = "/secure/path/rsa_key.p8"
private_key_passphrase_env_var = "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
warehouse = "my_warehouse"

# SSO/Browser auth (for interactive use)
[sso]
account = "your_account"
user = "your_user"
authenticator = "externalbrowser"
warehouse = "my_warehouse"
```

### Environment Variables

```bash
# Avoid storing secrets in files
export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE="your_passphrase"
export SNOWFLAKE_PASSWORD="your_password"  # For dev only
```

## CI/CD Authentication

### GitHub Actions

```yaml
- name: Deploy Streamlit
  env:
    SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
    SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
    SNOWFLAKE_PRIVATE_KEY: ${{ secrets.SNOWFLAKE_PRIVATE_KEY }}
  run: |
    # Write private key to file
    echo "$SNOWFLAKE_PRIVATE_KEY" > /tmp/rsa_key.p8
    chmod 600 /tmp/rsa_key.p8

    # Configure connection
    snow connection add \
      --connection-name deploy \
      --account $SNOWFLAKE_ACCOUNT \
      --user $SNOWFLAKE_USER \
      --authenticator SNOWFLAKE_JWT \
      --private-key-path /tmp/rsa_key.p8

    # Deploy
    snow streamlit deploy --connection deploy --replace
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use secrets management** (GitHub Secrets, AWS Secrets Manager, etc.)
3. **Rotate keys regularly** (90 days recommended)
4. **Use separate accounts** for dev/staging/prod
5. **Apply network policies** to restrict access
6. **Monitor authentication** via ACCESS_HISTORY view

## Resources

- [Key-Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth)
- [OAuth Overview](https://docs.snowflake.com/en/user-guide/oauth)
- [Workload Identity](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-overview)
- [Authentication Deprecation](https://community.snowflake.com/s/article/Authentication-Changes-2025)
