# Snowflake REST API (SQL API v2) Reference

Comprehensive guide for Snowflake REST API integration, especially for Cloudflare Workers.

## Endpoint

```
https://{account-identifier}.snowflakecomputing.com/api/v2/statements
```

Use **organization-account** format: `myorg-myaccount` (not account locator).

## Required Headers (ALL Endpoints)

Every Snowflake REST API request requires these headers:

| Header | Value | Notes |
|--------|-------|-------|
| `Authorization` | `Bearer <jwt_token>` | Required |
| `Accept` | `application/json` | **Required - causes "null" error if missing** |
| `Content-Type` | `application/json` | Required for POST |
| `User-Agent` | `MyApp/1.0` | Required (RFC 7231) |

**Optional but recommended:**

| Header | Value |
|--------|-------|
| `X-Snowflake-Authorization-Token-Type` | `KEYPAIR_JWT` |
| `X-Snowflake-Role` | `MY_ROLE` |
| `X-Snowflake-Warehouse` | `MY_WH` |

## Async Query Behavior

**Critical**: Even simple queries like `SELECT CURRENT_TIMESTAMP()` may return async (HTTP 202).

| Response Code | Meaning | Action |
|---------------|---------|--------|
| **200** | Query complete | Parse `data` array from response |
| **202** | Still executing | Poll `statementStatusUrl` |
| **408** | Timeout | Query exceeded timeout |
| **422** | Execution error | Check `message` for details |
| **429** | Rate limited | Retry with backoff |

### Response Format (202 Accepted)

```json
{
  "code": "090001",
  "sqlState": "00000",
  "message": "Statement executed successfully.",
  "statementHandle": "01abc123-0000-0000-0000-000000000000",
  "statementStatusUrl": "/api/v2/statements/01abc123-..."
}
```

### Status Code 090001

`090001` with `sqlState: "00000"` means **success** (query still running or complete), not an error.

## Polling Best Practices

### Cloudflare Workers Constraints

| Plan | Subrequest Limit | Max Poll Attempts |
|------|------------------|-------------------|
| **Free** | 50 | ~45 (leave buffer) |
| **Paid** | 1,000 | ~100 (conservative) |

### Recommended Configuration

```typescript
// Free plan
const POLLING_CONFIG = {
  intervalMs: 2000,        // Poll every 2 seconds
  maxAttempts: 45,         // Stay under 50 limit
  fetchTimeoutMs: 30000,   // 30s per request
  totalTimeoutMs: 90000,   // 90s total
};

// Paid plan
const POLLING_CONFIG = {
  intervalMs: 500,         // Poll every 500ms
  maxAttempts: 100,        // Stay well under 1000
  fetchTimeoutMs: 30000,
  totalTimeoutMs: 60000,
};
```

## Warehouse Auto-Resume

Auto-resume **works** with REST API when `AUTO_RESUME = TRUE` (default).

| Warehouse Size | Resume Time |
|----------------|-------------|
| X-Small/Small | 1-2 seconds |
| Medium | 1-3 seconds |
| Large+ | 2-5+ seconds |

**For time-sensitive operations**, explicitly resume first:

```
POST /api/v2/warehouses/{warehouse_name}:resume
```

Or via SQL API:
```sql
ALTER WAREHOUSE MY_WH RESUME IF SUSPENDED
```

## JWT Authentication Format

### Claims

| Claim | Format |
|-------|--------|
| `iss` | `ACCOUNT.USERNAME.SHA256:fingerprint` |
| `sub` | `ACCOUNT.USERNAME` |
| `iat` | Unix timestamp (seconds) |
| `exp` | Max 1 hour from iat |

**Account identifier**: Use `MYORG-MYACCOUNT` format (uppercase).

### Finding Your Identifiers

```sql
SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME();
-- Returns: MYORG-MYACCOUNT

SELECT CURRENT_ACCOUNT();
-- Returns legacy locator: NZ90655 (use org-account instead)
```

### Common Auth Errors

| Error | Cause |
|-------|-------|
| `390144 JWT_TOKEN_INVALID` | Wrong account identifier in `iss` |
| `394300 JWT_TOKEN_INVALID_USER_IN_ISSUER` | Username doesn't match `LOGIN_NAME` |
| `394302 JWT_TOKEN_INVALID_ISSUE_TIME` | Clock skew >60 seconds |
| `394304 PUBLIC_KEY_FINGERPRINT_MISMATCH` | Fingerprint doesn't match stored key |

## Timeout Handling in Workers

Cloudflare Workers `fetch()` has **no default timeout**. Always use AbortController:

```typescript
const response = await fetch(url, {
  signal: AbortSignal.timeout(30000), // 30 seconds
  headers: getSnowflakeHeaders(jwt),
});
```

## Cancel Query on Timeout

When timeout occurs, cancel the Snowflake query to avoid warehouse costs:

```
POST /api/v2/statements/{statementHandle}/cancel
```

## Alternative: Cloudflare Workflows

For queries >90 seconds, use Cloudflare Workflows instead of direct polling:
- Each step has its own subrequest limit
- Automatic retries with backoff
- Can wait up to 30 days

## Reference

- [SQL API Reference](https://docs.snowflake.com/en/developer-guide/sql-api/reference)
- [Authentication](https://docs.snowflake.com/en/developer-guide/sql-api/authenticating)
- [Handling Responses](https://docs.snowflake.com/en/developer-guide/sql-api/handling-responses)
