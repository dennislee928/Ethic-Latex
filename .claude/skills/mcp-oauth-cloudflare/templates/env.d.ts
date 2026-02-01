/**
 * Environment type definition for MCP OAuth Cloudflare Worker
 *
 * TEMPLATE: Add your custom bindings and variables here
 */

interface Env {
  // === Required Secrets (set via `wrangler secret put`) ===
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  COOKIE_ENCRYPTION_KEY: string;

  // === Optional: Custom Google Scopes ===
  // Set this to override the default 'openid email profile' scopes
  // Example: 'openid email profile https://www.googleapis.com/auth/drive'
  GOOGLE_SCOPES?: string;

  // === Bindings ===
  OAUTH_KV: KVNamespace;
  MCP_OBJECT: DurableObjectNamespace;

  // === Add your custom bindings below ===
  // MY_KV: KVNamespace;
  // MY_D1: D1Database;
  // MY_R2: R2Bucket;
  // MY_AI: Ai;
}

declare module 'cloudflare:workers' {
  interface Env extends Env {}
}
