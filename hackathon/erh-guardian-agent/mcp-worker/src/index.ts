/**
 * ERH Guardian MCP server (Cloudflare Worker + Durable Object + D1).
 *
 * Exposes the guardian's persistence layer as MCP tools so the Strands agent
 * (Python, on Bedrock) can read/write value-alignment profiles and log every
 * gate decision over streamable HTTP (/mcp) or SSE (/sse).
 */

import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { drizzle } from "drizzle-orm/d1";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { decisions, profiles } from "./db/schema";

export interface Env {
  DB: D1Database;
  ERH_GUARDIAN_MCP: DurableObjectNamespace;
  /** Shared secret for the MCP write surface (`wrangler secret put MCP_AUTH_TOKEN`).
   * Unset (local `wrangler dev`) leaves the worker open for development. */
  MCP_AUTH_TOKEN?: string;
}

const json = (data: unknown) => ({
  content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
});

export class ErhGuardianMCP extends McpAgent<Env> {
  server = new McpServer({ name: "erh-guardian-mcp", version: "0.1.0" });

  async init() {
    const db = drizzle(this.env.DB);

    this.server.tool(
      "get_profile",
      "Fetch a user's value-alignment profile (risk threshold, protected topics, auto-approve tools).",
      { profile_id: z.string().default("default") },
      async ({ profile_id }) => {
        const rows = await db
          .select()
          .from(profiles)
          .where(eq(profiles.id, profile_id))
          .limit(1);
        return json(rows[0] ?? { id: profile_id, exists: false });
      },
    );

    this.server.tool(
      "update_profile",
      "Create or update a value-alignment profile. Only provided fields change.",
      {
        profile_id: z.string().default("default"),
        name: z.string().optional(),
        risk_threshold: z.number().min(0).max(100).optional(),
        protected_topics: z.array(z.string()).optional(),
        auto_approve_tools: z.array(z.string()).optional(),
      },
      async ({ profile_id, name, risk_threshold, protected_topics, auto_approve_tools }) => {
        const now = new Date();
        const existing = await db
          .select()
          .from(profiles)
          .where(eq(profiles.id, profile_id))
          .limit(1);
        const base = existing[0];
        const row = {
          id: profile_id,
          name: name ?? base?.name ?? "default",
          riskThreshold: risk_threshold ?? base?.riskThreshold ?? 40,
          protectedTopics: protected_topics ?? base?.protectedTopics ?? [],
          autoApproveTools: auto_approve_tools ?? base?.autoApproveTools ?? [],
          updatedAt: now,
        };
        await db
          .insert(profiles)
          .values(row)
          .onConflictDoUpdate({ target: profiles.id, set: row });
        return json(row);
      },
    );

    this.server.tool(
      "log_decision",
      "Record one GuardianGate decision in the audit log (feeds the transparency panel).",
      {
        profile_id: z.string().default("default"),
        tool_name: z.string(),
        action_text: z.string(),
        risk_score: z.number().min(0).max(100),
        ethical_value: z.number().min(-1).max(1),
        erh_satisfied: z.boolean().optional(),
        estimated_exponent: z.number().optional(),
        verdict: z.enum(["auto_approved", "human_approved", "blocked"]),
      },
      async (input) => {
        const inserted = await db
          .insert(decisions)
          .values({
            profileId: input.profile_id,
            toolName: input.tool_name,
            actionText: input.action_text,
            riskScore: input.risk_score,
            ethicalValue: input.ethical_value,
            erhSatisfied: input.erh_satisfied,
            estimatedExponent: input.estimated_exponent,
            verdict: input.verdict,
            createdAt: new Date(),
          })
          .returning({ id: decisions.id });
        return json({ logged: true, id: inserted[0]?.id });
      },
    );

    this.server.tool(
      "list_decisions",
      "List recent gate decisions for a profile, newest first.",
      {
        profile_id: z.string().default("default"),
        limit: z.number().int().min(1).max(100).default(20),
      },
      async ({ profile_id, limit }) => {
        const rows = await db
          .select()
          .from(decisions)
          .where(eq(decisions.profileId, profile_id))
          .orderBy(desc(decisions.createdAt), desc(decisions.id))
          .limit(limit);
        return json(rows);
      },
    );
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

/**
 * Bearer-token guard for the write surface (/mcp, /sse, and any non-GET /api/*).
 * The transparency panel's read-only GETs and /health stay public by design.
 * Returns null when the request may proceed, or a 401 response otherwise.
 */
function requireAuth(request: Request, env: Env): Response | null {
  if (!env.MCP_AUTH_TOKEN) {
    console.warn(
      "MCP_AUTH_TOKEN is not set — /mcp, /sse and write endpoints are UNAUTHENTICATED. " +
        "Fine for local dev; set it with `wrangler secret put MCP_AUTH_TOKEN` before deploying.",
    );
    return null;
  }
  const header = request.headers.get("Authorization") ?? "";
  if (header === `Bearer ${env.MCP_AUTH_TOKEN}`) return null;
  return Response.json(
    { error: "unauthorized", detail: "Missing or invalid bearer token." },
    { status: 401, headers: CORS },
  );
}

// Read-only REST endpoints feeding the transparency panel UI.
async function handleApi(pathname: string, url: URL, env: Env): Promise<Response | null> {
  const db = drizzle(env.DB);
  const profileId = url.searchParams.get("profile_id") ?? "default";

  if (pathname === "/api/profile") {
    const rows = await db.select().from(profiles).where(eq(profiles.id, profileId)).limit(1);
    return Response.json(rows[0] ?? null, { headers: CORS });
  }
  if (pathname === "/api/decisions") {
    const limit = Math.min(100, Number(url.searchParams.get("limit") ?? 50) || 50);
    const rows = await db
      .select()
      .from(decisions)
      .where(eq(decisions.profileId, profileId))
      .orderBy(desc(decisions.createdAt), desc(decisions.id))
      .limit(limit);
    return Response.json(rows, { headers: CORS });
  }
  return null;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    const { pathname } = url;

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: { ...CORS, "Access-Control-Max-Age": "86400" },
      });
    }

    if (pathname.startsWith("/api/")) {
      // GETs feed the public transparency panel; anything else needs the token.
      if (request.method !== "GET") {
        const denied = requireAuth(request, env);
        if (denied) return denied;
      }
      const apiResponse = await handleApi(pathname, url, env);
      if (apiResponse) return apiResponse;
    }

    if (pathname === "/health") {
      return Response.json({
        status: "ok",
        name: "erh-guardian-mcp",
        transports: { sse: "/sse", streamable_http: "/mcp" },
      });
    }
    if (pathname.startsWith("/sse")) {
      const denied = requireAuth(request, env);
      if (denied) return denied;
      return ErhGuardianMCP.serveSSE("/sse").fetch(request, env, ctx);
    }
    if (pathname.startsWith("/mcp")) {
      const denied = requireAuth(request, env);
      if (denied) return denied;
      return ErhGuardianMCP.serve("/mcp").fetch(request, env, ctx);
    }
    return new Response("Not Found", { status: 404 });
  },
};
