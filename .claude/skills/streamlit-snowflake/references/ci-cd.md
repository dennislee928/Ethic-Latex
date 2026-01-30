# CI/CD for Streamlit in Snowflake

Automate deployment of Streamlit apps using GitHub Actions and Snowflake CLI.

## GitHub Actions Workflow

### Basic Deployment

`.github/workflows/deploy-streamlit.yml`:

```yaml
name: Deploy Streamlit to Snowflake

on:
  push:
    branches: [main]
    paths:
      - 'streamlit_app.py'
      - 'pages/**'
      - 'common/**'
      - 'environment.yml'
      - 'snowflake.yml'

  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Snowflake CLI
        run: pip install snowflake-cli-labs

      - name: Configure Snowflake connection
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PRIVATE_KEY: ${{ secrets.SNOWFLAKE_PRIVATE_KEY }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
          SNOWFLAKE_SCHEMA: ${{ secrets.SNOWFLAKE_SCHEMA }}
        run: |
          # Write private key
          echo "$SNOWFLAKE_PRIVATE_KEY" > /tmp/rsa_key.p8
          chmod 600 /tmp/rsa_key.p8

          # Create config directory
          mkdir -p ~/.snowflake

          # Write connections.toml
          cat > ~/.snowflake/connections.toml << EOF
          [deploy]
          account = "$SNOWFLAKE_ACCOUNT"
          user = "$SNOWFLAKE_USER"
          authenticator = "SNOWFLAKE_JWT"
          private_key_path = "/tmp/rsa_key.p8"
          warehouse = "$SNOWFLAKE_WAREHOUSE"
          database = "$SNOWFLAKE_DATABASE"
          schema = "$SNOWFLAKE_SCHEMA"
          EOF

      - name: Deploy Streamlit app
        run: |
          snow streamlit deploy --connection deploy --replace

      - name: Get app URL
        run: |
          snow streamlit describe --connection deploy | grep -i url

      - name: Cleanup
        if: always()
        run: rm -f /tmp/rsa_key.p8
```

### With Environment-Specific Deployments

```yaml
name: Deploy Streamlit

on:
  push:
    branches:
      - main      # Deploy to prod
      - staging   # Deploy to staging

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set environment
        id: env
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "ENV=prod" >> $GITHUB_OUTPUT
            echo "STREAMLIT_NAME=my_app" >> $GITHUB_OUTPUT
          else
            echo "ENV=staging" >> $GITHUB_OUTPUT
            echo "STREAMLIT_NAME=my_app_staging" >> $GITHUB_OUTPUT
          fi

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install CLI
        run: pip install snowflake-cli-labs

      - name: Configure connection
        env:
          # Use environment-specific secrets
          SNOWFLAKE_ACCOUNT: ${{ secrets[format('SNOWFLAKE_ACCOUNT_{0}', steps.env.outputs.ENV)] }}
          SNOWFLAKE_USER: ${{ secrets[format('SNOWFLAKE_USER_{0}', steps.env.outputs.ENV)] }}
          SNOWFLAKE_PRIVATE_KEY: ${{ secrets[format('SNOWFLAKE_PRIVATE_KEY_{0}', steps.env.outputs.ENV)] }}
        run: |
          echo "$SNOWFLAKE_PRIVATE_KEY" > /tmp/rsa_key.p8
          chmod 600 /tmp/rsa_key.p8

          mkdir -p ~/.snowflake
          cat > ~/.snowflake/connections.toml << EOF
          [deploy]
          account = "$SNOWFLAKE_ACCOUNT"
          user = "$SNOWFLAKE_USER"
          authenticator = "SNOWFLAKE_JWT"
          private_key_path = "/tmp/rsa_key.p8"
          EOF

      - name: Deploy
        run: |
          snow streamlit deploy ${{ steps.env.outputs.STREAMLIT_NAME }} \
            --connection deploy \
            --replace

      - name: Cleanup
        if: always()
        run: rm -f /tmp/rsa_key.p8
```

## Required GitHub Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `SNOWFLAKE_ACCOUNT` | Account identifier | `xy12345.us-east-1` |
| `SNOWFLAKE_USER` | Service account username | `deploy_user` |
| `SNOWFLAKE_PRIVATE_KEY` | Private key (PEM format) | Full key content |
| `SNOWFLAKE_WAREHOUSE` | Warehouse name | `COMPUTE_WH` |
| `SNOWFLAKE_DATABASE` | Database name | `MY_DB` |
| `SNOWFLAKE_SCHEMA` | Schema name | `PUBLIC` |

### Setting Private Key Secret

```bash
# Copy entire private key including headers
cat rsa_key.p8 | pbcopy  # macOS
cat rsa_key.p8 | xclip   # Linux

# Paste into GitHub secret (Settings > Secrets > New)
```

## Alternative: Using Snowflake CLI Configuration

### Pre-configured CLI

If using self-hosted runners with pre-configured Snowflake CLI:

```yaml
- name: Deploy
  run: snow streamlit deploy --connection prod --replace
```

### Using config.toml

```yaml
- name: Configure
  run: |
    mkdir -p ~/.snowflake
    cat > ~/.snowflake/config.toml << EOF
    default_connection_name = "deploy"
    EOF
```

## Native App CI/CD

For Marketplace Native Apps:

```yaml
name: Deploy Native App

on:
  push:
    branches: [main]
    paths:
      - 'manifest.yml'
      - 'setup.sql'
      - 'streamlit/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup
        # ... same as above ...

      - name: Upload to Stage
        run: |
          snow stage put manifest.yml @my_package.versions.v1/ --overwrite
          snow stage put setup.sql @my_package.versions.v1/ --overwrite
          snow stage put streamlit/ @my_package.versions.v1/streamlit/ --overwrite --recursive

      - name: Update Version
        run: |
          snow sql -q "ALTER APPLICATION PACKAGE my_package
            ADD VERSION v${{ github.run_number }}
            USING '@my_package.versions.v1'"
```

## Best Practices

### 1. Use Dedicated Service Account

```sql
-- Create deploy user
CREATE USER deploy_user
  DEFAULT_ROLE = deploy_role
  DEFAULT_WAREHOUSE = deploy_wh;

-- Grant minimal permissions
GRANT ROLE deploy_role TO USER deploy_user;
GRANT CREATE STREAMLIT ON SCHEMA my_schema TO ROLE deploy_role;
```

### 2. Validate Before Deploy

```yaml
- name: Validate snowflake.yml
  run: |
    python -c "import yaml; yaml.safe_load(open('snowflake.yml'))"

- name: Validate environment.yml
  run: |
    python -c "import yaml; yaml.safe_load(open('environment.yml'))"
```

### 3. Add Deployment Notifications

```yaml
- name: Notify Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Streamlit app deployed successfully!"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 4. Run Tests First

```yaml
- name: Test Streamlit app
  run: |
    pip install streamlit pytest
    # Syntax check
    python -m py_compile streamlit_app.py
    python -m py_compile pages/*.py
    # Unit tests if any
    pytest tests/ -v || true
```

## Troubleshooting

### Authentication Fails
- Verify private key format (PKCS#8)
- Check key passphrase if encrypted
- Confirm user has correct permissions

### Deploy Timeout
- Increase GitHub Actions timeout: `timeout-minutes: 30`
- Check warehouse availability

### Stage Upload Fails
- Verify stage exists
- Check write permissions on stage
