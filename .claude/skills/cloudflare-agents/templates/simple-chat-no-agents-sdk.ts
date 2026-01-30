/**
 * Simple Chat WITHOUT Agents SDK
 *
 * This template shows how to build a chat interface using JUST the Vercel AI SDK
 * on Cloudflare Workers - no Agents SDK, no Durable Objects, no WebSockets.
 *
 * WHAT THIS PROVIDES:
 * - ✅ AI streaming responses (SSE)
 * - ✅ React hooks (useChat, useCompletion)
 * - ✅ Multi-provider support
 * - ✅ ~100 lines of code vs ~500+ with Agents SDK
 *
 * WHAT THIS DOESN'T PROVIDE:
 * - ❌ WebSocket bidirectional communication (only SSE one-way)
 * - ❌ Built-in state persistence (add D1/KV separately if needed)
 * - ❌ Durable Objects (single Worker handles all requests)
 * - ❌ Multi-agent coordination
 *
 * USE THIS WHEN:
 * - Building a basic chat interface
 * - SSE streaming is sufficient (most cases)
 * - No persistent state needed per user
 * - Want minimal complexity
 *
 * DON'T USE THIS WHEN:
 * - Need WebSocket bidirectional real-time
 * - Need stateful agent instances
 * - Building multi-agent systems
 * - Need scheduled tasks or workflows
 *
 * MIGRATION PATH:
 * If you discover later that you need WebSockets or Durable Objects state,
 * you can migrate to Agents SDK. Start simple, add complexity only when needed.
 */

// ============================================================================
// BACKEND: Cloudflare Worker with AI SDK
// ============================================================================

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

interface Env {
  OPENAI_API_KEY: string;
}

const app = new Hono<{ Bindings: Env }>();

// Enable CORS for frontend
app.use('*', cors());

// Chat endpoint - handles streaming responses
app.post('/api/chat', async (c) => {
  const { messages } = await c.req.json();

  // Validate input
  if (!Array.isArray(messages) || messages.length === 0) {
    return c.json({ error: 'Messages array required' }, 400);
  }

  // Stream AI response using Vercel AI SDK
  const result = streamText({
    model: openai('gpt-4o-mini'),
    messages,
    system: 'You are a helpful assistant.',
    temperature: 0.7,
    maxTokens: 1000,
  });

  // Return SSE stream (automatic streaming handled by AI SDK)
  return result.toTextStreamResponse();
});

// Optional: Add completion endpoint for non-chat use cases
app.post('/api/completion', async (c) => {
  const { prompt } = await c.req.json();

  const result = streamText({
    model: openai('gpt-4o-mini'),
    prompt,
  });

  return result.toTextStreamResponse();
});

export default app;

/**
 * DEPLOYMENT:
 *
 * 1. Install dependencies:
 *    npm install hono ai @ai-sdk/openai
 *
 * 2. Create wrangler.jsonc:
 *    {
 *      "name": "simple-chat",
 *      "main": "src/worker.ts",
 *      "compatibility_date": "2025-11-19",
 *      "compatibility_flags": ["nodejs_compat"]
 *    }
 *
 * 3. Set secrets:
 *    npx wrangler secret put OPENAI_API_KEY
 *
 * 4. Deploy:
 *    npx wrangler deploy
 *
 * That's it. No Durable Objects bindings, no migrations, no complexity.
 */

// ============================================================================
// FRONTEND: React Client with useChat Hook
// ============================================================================

/**
 * Save this as: src/ChatPage.tsx
 *
 * ```typescript
 * import { useChat } from 'ai/react';
 *
 * export function ChatPage() {
 *   const {
 *     messages,
 *     input,
 *     handleInputChange,
 *     handleSubmit,
 *     isLoading,
 *     error
 *   } = useChat({
 *     api: '/api/chat',
 *   });
 *
 *   return (
 *     <div className="flex flex-col h-screen">
 *       {/\* Messages *\/}
 *       <div className="flex-1 overflow-y-auto p-4 space-y-4">
 *         {messages.map((msg) => (
 *           <div
 *             key={msg.id}
 *             className={`flex ${
 *               msg.role === 'user' ? 'justify-end' : 'justify-start'
 *             }`}
 *           >
 *             <div
 *               className={`max-w-xs rounded-lg p-3 ${
 *                 msg.role === 'user'
 *                   ? 'bg-blue-500 text-white'
 *                   : 'bg-gray-200 text-gray-900'
 *               }`}
 *             >
 *               <p className="whitespace-pre-wrap">{msg.content}</p>
 *             </div>
 *           </div>
 *         ))}
 *
 *         {isLoading && (
 *           <div className="flex justify-start">
 *             <div className="bg-gray-200 rounded-lg p-3">
 *               <div className="flex space-x-2">
 *                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
 *                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
 *                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
 *               </div>
 *             </div>
 *           </div>
 *         )}
 *       </div>
 *
 *       {/\* Input Form *\/}
 *       <form onSubmit={handleSubmit} className="p-4 border-t">
 *         <div className="flex space-x-2">
 *           <input
 *             value={input}
 *             onChange={handleInputChange}
 *             placeholder="Type a message..."
 *             className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
 *             disabled={isLoading}
 *           />
 *           <button
 *             type="submit"
 *             disabled={isLoading || !input.trim()}
 *             className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
 *           >
 *             Send
 *           </button>
 *         </div>
 *         {error && <p className="text-red-500 text-sm mt-2">{error.message}</p>}
 *       </form>
 *     </div>
 *   );
 * }
 * ```
 */

/**
 * FEATURES PROVIDED BY useChat HOOK:
 *
 * - messages: Array of chat messages
 * - input: Current input value
 * - handleInputChange: Input onChange handler
 * - handleSubmit: Form submit handler
 * - isLoading: True during streaming
 * - error: Error object if request fails
 * - reload: Regenerate last response
 * - stop: Stop current streaming
 * - append: Add message programmatically
 * - setMessages: Update messages array
 *
 * All of this is built-in with AI SDK - no custom state management needed.
 */

/**
 * COMPARISON WITH AGENTS SDK APPROACH:
 *
 * | Feature | This Template | Agents SDK Template |
 * |---------|---------------|-------------------|
 * | Lines of code | ~150 | ~500+ |
 * | Setup complexity | Low | High |
 * | Durable Objects | ❌ | ✅ |
 * | WebSockets | ❌ | ✅ |
 * | State persistence | Manual (D1/KV) | Built-in (SQLite) |
 * | React hooks | ✅ useChat | Custom hooks |
 * | Deployment | 1 step | 3+ steps |
 * | Migrations | ❌ | ✅ Required |
 * | Use case | 80% of chats | 20% (complex) |
 *
 * START HERE. Migrate to Agents SDK only if you discover you need WebSockets or state.
 */

/**
 * ADDING STATE PERSISTENCE (Optional):
 *
 * If you need to save chat history but don't want Agents SDK complexity:
 *
 * ```typescript
 * // Add D1 binding to wrangler.jsonc
 * // Then in worker:
 *
 * app.post('/api/chat', async (c) => {
 *   const { messages, userId } = await c.req.json();
 *
 *   // Save to D1 before streaming
 *   await c.env.DB.prepare(
 *     'INSERT INTO messages (user_id, content, role) VALUES (?, ?, ?)'
 *   ).bind(userId, messages[messages.length - 1].content, 'user').run();
 *
 *   const result = streamText({
 *     model: openai('gpt-4o-mini'),
 *     messages,
 *   });
 *
 *   return result.toTextStreamResponse();
 * });
 * ```
 *
 * You get persistence without Durable Objects complexity.
 */

/**
 * SWITCHING TO WORKERS AI (Cost Savings):
 *
 * To use Cloudflare's Workers AI instead of OpenAI:
 *
 * ```typescript
 * import { createCloudflare } from '@ai-sdk/cloudflare';
 *
 * const cloudflare = createCloudflare({
 *   apiKey: c.env.CLOUDFLARE_API_KEY,
 * });
 *
 * const result = streamText({
 *   model: cloudflare('@cf/meta/llama-3-8b-instruct'),
 *   messages,
 * });
 * ```
 *
 * AI SDK handles the SSE parsing automatically (unlike manual Workers AI).
 */
