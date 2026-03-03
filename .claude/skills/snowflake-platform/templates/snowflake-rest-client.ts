/**
 * Snowflake REST API Client for Cloudflare Workers
 *
 * Handles:
 * - Consistent headers across all endpoints
 * - Fetch timeouts with AbortController
 * - Async polling with subrequest limits
 * - Query cancellation on timeout
 */

interface Env {
  SNOWFLAKE_ACCOUNT_URL: string; // e.g., "myorg-myaccount"
  SNOWFLAKE_USER: string;
  SNOWFLAKE_WAREHOUSE: string;
  SNOWFLAKE_DATABASE: string;
  SNOWFLAKE_SCHEMA: string;
  SNOWFLAKE_PRIVATE_KEY: string;
  SNOWFLAKE_PUBLIC_KEY_FP: string;
}

interface SnowflakeQueryResult {
  code: string;
  sqlState: string;
  message: string;
  statementHandle?: string;
  statementStatusUrl?: string;
  data?: string[][];
  resultSetMetaData?: {
    numRows: number;
    rowType: Array<{ name: string; type: string }>;
  };
}

interface PollingConfig {
  intervalMs: number;
  maxAttempts: number;
  fetchTimeoutMs: number;
}

// Configuration - adjust based on Workers plan
const POLLING_CONFIG: PollingConfig = {
  intervalMs: 2000, // 2 seconds (free plan safe)
  maxAttempts: 45, // Stay under 50 subrequest limit
  fetchTimeoutMs: 30000, // 30 seconds per request
};

/**
 * Creates consistent headers for ALL Snowflake API requests
 * CRITICAL: Missing Accept header causes "Unsupported Accept header null" error
 */
function getSnowflakeHeaders(jwt: string): HeadersInit {
  return {
    Authorization: `Bearer ${jwt}`,
    'Content-Type': 'application/json',
    Accept: 'application/json', // REQUIRED - must be on ALL requests
    'User-Agent': 'CloudflareWorker/1.0',
    'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
  };
}

/**
 * Generate JWT for Snowflake key-pair authentication
 * NOTE: Account identifier must be UPPERCASE in claims
 */
async function generateSnowflakeJWT(env: Env): Promise<string> {
  // Implementation depends on your JWT library (e.g., jose)
  // Key points:
  // - iss: ACCOUNT.USERNAME.SHA256:fingerprint (uppercase)
  // - sub: ACCOUNT.USERNAME (uppercase)
  // - exp: max 1 hour from now

  const accountUpper = env.SNOWFLAKE_ACCOUNT_URL.toUpperCase();
  const userUpper = env.SNOWFLAKE_USER.toUpperCase();

  const claims = {
    iss: `${accountUpper}.${userUpper}.${env.SNOWFLAKE_PUBLIC_KEY_FP}`,
    sub: `${accountUpper}.${userUpper}`,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
  };

  // Use jose or similar library to sign with RS256
  // return await signJWT(claims, env.SNOWFLAKE_PRIVATE_KEY);
  throw new Error('Implement JWT signing with your preferred library');
}

/**
 * Submit a SQL query to Snowflake
 * Returns immediately with statementHandle for async queries
 */
async function submitQuery(
  sql: string,
  jwt: string,
  env: Env
): Promise<SnowflakeQueryResult> {
  const url = `https://${env.SNOWFLAKE_ACCOUNT_URL}.snowflakecomputing.com/api/v2/statements`;

  const response = await fetch(url, {
    method: 'POST',
    headers: getSnowflakeHeaders(jwt),
    signal: AbortSignal.timeout(POLLING_CONFIG.fetchTimeoutMs),
    body: JSON.stringify({
      statement: sql,
      timeout: 300, // Server-side timeout in seconds
      database: env.SNOWFLAKE_DATABASE,
      schema: env.SNOWFLAKE_SCHEMA,
      warehouse: env.SNOWFLAKE_WAREHOUSE,
    }),
  });

  if (!response.ok && response.status !== 202) {
    const error = await response.text();
    throw new Error(`Snowflake query failed: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Poll for query completion
 * Handles Workers subrequest limits with configurable intervals
 */
async function pollForResult(
  statementHandle: string,
  jwt: string,
  env: Env
): Promise<SnowflakeQueryResult> {
  const statusUrl = `https://${env.SNOWFLAKE_ACCOUNT_URL}.snowflakecomputing.com/api/v2/statements/${statementHandle}`;

  for (let attempt = 0; attempt < POLLING_CONFIG.maxAttempts; attempt++) {
    const response = await fetch(statusUrl, {
      method: 'GET',
      headers: getSnowflakeHeaders(jwt), // SAME headers required!
      signal: AbortSignal.timeout(POLLING_CONFIG.fetchTimeoutMs),
    });

    // Rate limited - back off
    if (response.status === 429) {
      await sleep(POLLING_CONFIG.intervalMs * 2);
      continue;
    }

    const result: SnowflakeQueryResult = await response.json();

    // 200 = complete, 202 = still running
    if (response.status === 200 && !result.statementStatusUrl) {
      return result; // Query complete with results
    }

    // Still running (code 090001 = success/running, not error)
    if (response.status === 202 || result.statementStatusUrl) {
      await sleep(POLLING_CONFIG.intervalMs);
      continue;
    }

    // Error
    throw new Error(`Query failed: ${result.message}`);
  }

  // Timeout - cancel the query to avoid warehouse costs
  await cancelQuery(statementHandle, jwt, env);
  throw new Error(
    `Query timeout after ${POLLING_CONFIG.maxAttempts} polling attempts`
  );
}

/**
 * Cancel a running query
 * Call this when timeout occurs to stop warehouse usage
 */
async function cancelQuery(
  statementHandle: string,
  jwt: string,
  env: Env
): Promise<void> {
  try {
    await fetch(
      `https://${env.SNOWFLAKE_ACCOUNT_URL}.snowflakecomputing.com/api/v2/statements/${statementHandle}/cancel`,
      {
        method: 'POST',
        headers: getSnowflakeHeaders(jwt),
        signal: AbortSignal.timeout(5000), // Short timeout for cancel
      }
    );
  } catch {
    // Best effort - log but don't throw
    console.error('Failed to cancel Snowflake query:', statementHandle);
  }
}

/**
 * Resume warehouse before queries (optional, for time-sensitive ops)
 */
async function resumeWarehouse(jwt: string, env: Env): Promise<void> {
  const url = `https://${env.SNOWFLAKE_ACCOUNT_URL}.snowflakecomputing.com/api/v2/warehouses/${env.SNOWFLAKE_WAREHOUSE}:resume`;

  await fetch(url, {
    method: 'POST',
    headers: getSnowflakeHeaders(jwt),
    signal: AbortSignal.timeout(10000),
  });
}

/**
 * Execute a SQL query and wait for results
 * Main entry point for query execution
 */
export async function executeQuery(
  sql: string,
  env: Env
): Promise<SnowflakeQueryResult> {
  const jwt = await generateSnowflakeJWT(env);

  // Submit query
  const submitResult = await submitQuery(sql, jwt, env);

  // If sync response (rare), return immediately
  if (submitResult.data && !submitResult.statementStatusUrl) {
    return submitResult;
  }

  // Async response - poll for completion
  if (!submitResult.statementHandle) {
    throw new Error('No statement handle returned');
  }

  return pollForResult(submitResult.statementHandle, jwt, env);
}

// Helper
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Export for use in Workers
export {
  getSnowflakeHeaders,
  generateSnowflakeJWT,
  submitQuery,
  pollForResult,
  cancelQuery,
  resumeWarehouse,
  POLLING_CONFIG,
};
