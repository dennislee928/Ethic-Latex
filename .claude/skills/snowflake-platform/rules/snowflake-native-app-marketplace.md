---
globs: ["**/snowflake.yml", "**/snowflake.yaml", "**/manifest.yml", "**/setup_script.sql", "**/PROVIDER_STUDIO.md"]
---

# Snowflake Native App Marketplace

Rules for publishing Native Apps to Snowflake Marketplace.

## Security Review Workflow (snow CLI - Recommended)

Use the `snow` CLI (Snowflake CLI) for native app workflows. Legacy SQL commands still work but CLI is preferred.

| Step | snow CLI Command |
|------|------------------|
| 1. Deploy app | `snow app run` |
| 2. Create version | `snow app version create V1_0` |
| 3. Check status | `snow app version list` |
| 4. Wait for approval | `review_status` must be `APPROVED` |
| 5. Publish to channel | `snow app publish --version V1_0 --patch 0` |

📚 **Source**: https://docs.snowflake.com/en/developer-guide/snowflake-cli/native-apps/publish-app

## Release Channels (Feb 2025 - Preview)

Release channels allow separate release tracks for different customer groups:

| Channel | Purpose |
|---------|---------|
| `DEFAULT` | Production releases |
| `ALPHA` | Early access customers |
| Custom channels | QA, beta testing, specific customer groups |

**Enable in snowflake.yml**:
```yaml
native_app:
  name: my_app
  package:
    name: my_app_pkg
  application:
    name: my_app
  enable_release_channels: true  # Required for release channels
```

**snow CLI commands**:
```bash
# List channels
snow app release-channel list

# Add version to channel
snow app release-channel add-version --channel ALPHA --version V1_0

# Publish with specific directive
snow app publish --version V1_0 --patch 0 --channel ALPHA --directive early_access
```

📚 **Source**: https://docs.snowflake.com/en/developer-guide/native-apps/release-channels

## Legacy SQL Workflow (Still Works)

| Step | SQL Command |
|------|-------------|
| 1. Set distribution | `ALTER APPLICATION PACKAGE pkg SET DISTRIBUTION = 'EXTERNAL';` |
| 2. Create version | `ALTER APPLICATION PACKAGE pkg ADD VERSION V1_0 USING '@pkg.stage/v1';` |
| 3. Check status | `SHOW VERSIONS IN APPLICATION PACKAGE pkg;` |
| 4. Add to channel | `ALTER APPLICATION PACKAGE pkg MODIFY RELEASE CHANNEL DEFAULT ADD VERSION V1_0;` |

## Security Review Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `NOT_REVIEWED` | Scan hasn't run | Wait or check DISTRIBUTION is EXTERNAL |
| `IN_PROGRESS` | Scan running | Wait a few minutes |
| `APPROVED` | Passed | Can publish to marketplace |
| `REJECTED` | Failed | Fix issues or appeal |
| `MANUAL_REVIEW` | Automated passed, human reviewing | Wait (can take business days) |

**Apps that trigger manual review**: External access integrations, Streamlit components, network calls to external services.

## External Access Integration (Streamlit Apps)

Native Apps with Streamlit that call external APIs need 4-step setup:

```sql
-- 1. Network rule
CREATE OR REPLACE NETWORK RULE app_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.example.com:443');

-- 2. Integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION app_integration
  ALLOWED_NETWORK_RULES = (app_network_rule)
  ENABLED = TRUE;

-- 3. Grant to app
GRANT USAGE ON INTEGRATION app_integration
  TO APPLICATION MY_APP;

-- 4. CRITICAL: Attach to Streamlit object
ALTER STREAMLIT MY_APP.schema.streamlit_name
  SET EXTERNAL_ACCESS_INTEGRATIONS = (app_integration);
```

**Note**: Step 4 resets on every app redeploy. Users must re-run it after updates.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `GRANT ON FUTURE TABLES TO APPLICATION` | Remove - apps own tables they create |
| Testing external access against httpbin.org | Test against the actual allowed domain |
| Only 4 review statuses | Include `MANUAL_REVIEW` as 5th status |

## Provider Studio Content

- Description field uses WYSIWYG editor - cannot paste HTML
- Use plain text and format with editor toolbar
- Business Needs require individual descriptions (not just selection)
