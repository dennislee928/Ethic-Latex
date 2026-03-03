/**
 * MCP Server with OAuth Authentication
 *
 * TEMPLATE: Copy and customize for your MCP server
 *
 * Features:
 * - OAuth authentication via Google
 * - User props available in tool handlers (email, name, id)
 * - Claude.ai compatible (DCR support)
 * - Durable Objects for session management
 */

import OAuthProvider from '@cloudflare/workers-oauth-provider';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { McpAgent } from 'agents/mcp';
import { z } from 'zod';
import { GoogleHandler } from './oauth/google-handler';

// Props from OAuth - user info stored in token
type Props = {
  id: string;        // Google user ID
  email: string;     // User's email
  name: string;      // User's display name
  picture?: string;  // Profile picture URL
  accessToken: string; // Google access token
};

/**
 * Your MCP Server
 * TEMPLATE: Rename this class and add your tools
 */
export class MyMcpServer extends McpAgent<Env, Record<string, never>, Props> {
  server = new McpServer({
    name: 'my-mcp-server', // TODO: Change this
    version: '1.0.0',
  });

  async init() {
    // Log authenticated user
    if (this.props) {
      console.log(`MCP session initialized for user: ${this.props.email}`);
    }

    // === Example Tool ===
    this.server.tool(
      'example_tool',
      'An example tool that uses user context',
      {
        message: z.string().describe('A message to process'),
      },
      async (args) => {
        // Access authenticated user info
        const userEmail = this.props?.email || 'anonymous';
        const userName = this.props?.name || 'Unknown';

        // Your tool logic here
        const result = {
          message: args.message,
          processedBy: userName,
          userEmail: userEmail,
          timestamp: new Date().toISOString(),
        };

        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }
    );

    // === Add more tools here ===

    // this.server.tool(
    //   'another_tool',
    //   'Description of another tool',
    //   {
    //     param1: z.string(),
    //     param2: z.number().optional(),
    //   },
    //   async (args) => {
    //     // Tool implementation
    //     return {
    //       content: [{ type: 'text', text: 'Result' }],
    //     };
    //   }
    // );
  }
}

/**
 * OAuth Provider - Main export
 * Handles OAuth flow and routes MCP requests to your server
 */
export default new OAuthProvider({
  apiHandlers: {
    '/sse': MyMcpServer.serveSSE('/sse'),   // SSE protocol (legacy)
    '/mcp': MyMcpServer.serve('/mcp'),       // Streamable HTTP protocol
  },
  authorizeEndpoint: '/authorize',
  clientRegistrationEndpoint: '/register',
  defaultHandler: GoogleHandler as any,
  tokenEndpoint: '/token',
});
