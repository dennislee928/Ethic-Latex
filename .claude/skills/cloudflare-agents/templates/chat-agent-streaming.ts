/**
 * Chat Agent with Streaming AI Responses
 *
 * ARCHITECTURE DECISION:
 * This template uses Agents SDK + Vercel AI SDK together. Understanding WHY helps you decide if you need both.
 *
 * ┌─────────────────────────────────────────────────────┐
 * │  Agents SDK (AIChatAgent)      Vercel AI SDK        │
 * │  ├─ WebSocket connections  +   ├─ AI inference      │
 * │  ├─ Durable Objects state      ├─ Auto streaming    │
 * │  ├─ Message persistence        ├─ Multi-provider    │
 * │  └─ Real-time sync             └─ React hooks       │
 * └─────────────────────────────────────────────────────┘
 *
 * WHAT AGENTS SDK PROVIDES (AIChatAgent):
 * - ✅ WebSocket bidirectional real-time communication
 * - ✅ Durable Objects (globally unique agent instance per user/room)
 * - ✅ Built-in message history (this.messages) with state persistence
 * - ✅ Lifecycle methods (onStart, onConnect, onMessage, onClose)
 * - ✅ SQLite storage for custom data (up to 1GB per agent)
 *
 * WHAT VERCEL AI SDK PROVIDES (streamText):
 * - ✅ Automatic streaming response handling (no manual SSE parsing)
 * - ✅ Multi-provider support (OpenAI, Anthropic, Google, etc.)
 * - ✅ React hooks on client (useChat, useCompletion)
 * - ✅ Unified API across providers
 * - ✅ Works on Cloudflare Workers
 *
 * WHEN TO USE THIS COMBINATION:
 * - ✅ Need WebSocket real-time chat (bidirectional, client can send while streaming)
 * - ✅ Need persistent state across sessions (agent remembers previous conversations)
 * - ✅ Need multi-user chat rooms (each room is a unique agent instance)
 * - ✅ Want clean AI integration without manual SSE parsing
 *
 * WHEN YOU DON'T NEED THIS (Simpler Alternative):
 * If you just need a basic chat interface with SSE streaming and no persistent state,
 * you can use JUST the Vercel AI SDK without Agents SDK:
 *
 * ```typescript
 * // worker.ts - No Agents SDK, 10x less code
 * import { streamText } from 'ai';
 * import { openai } from '@ai-sdk/openai';
 *
 * export default {
 *   async fetch(request: Request, env: Env) {
 *     const { messages } = await request.json();
 *     const result = streamText({ model: openai('gpt-4o-mini'), messages });
 *     return result.toTextStreamResponse(); // SSE streaming
 *   }
 * }
 *
 * // client.tsx - Built-in React hooks
 * import { useChat } from 'ai/react';
 * function Chat() {
 *   const { messages, input, handleSubmit } = useChat({ api: '/api/chat' });
 *   return <form onSubmit={handleSubmit}>...</form>;
 * }
 * ```
 *
 * That's it. No Durable Objects, no WebSockets, no migrations. Works for 80% of chat apps.
 *
 * ALTERNATIVE: Agents SDK + Workers AI (Cost-Optimized)
 * If you need Agents SDK infrastructure but want to save money, you can use Workers AI
 * instead of external providers. Trade-off: manual SSE parsing required.
 * See rag-agent-streaming-workers-ai.ts template for that approach.
 *
 * VERDICT: Use this template if you need WebSocket + state. Otherwise, start simpler.
 */

import { AIChatAgent } from "agents/ai-chat-agent";
import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";

interface Env {
  OPENAI_API_KEY?: string;
  ANTHROPIC_API_KEY?: string;
}

export class StreamingChatAgent extends AIChatAgent<Env> {
  // Handle incoming chat messages and stream response
  async onChatMessage(onFinish) {
    // Choose model based on available API keys
    const model = this.env.ANTHROPIC_API_KEY
      ? anthropic('claude-sonnet-4-5')
      : openai('gpt-4o-mini');

    // Stream text generation
    const result = streamText({
      model,
      messages: this.messages,  // Built-in message history
      onFinish,                  // Called when response complete
      temperature: 0.7,
      maxTokens: 1000
    });

    // Return streaming response
    return result.toTextStreamResponse();
  }

  // Optional: Customize state updates
  async onStateUpdate(state, source) {
    console.log('Chat updated:');
    console.log('  Messages:', this.messages.length);
    console.log('  Last message:', this.messages[this.messages.length - 1]?.content);
  }

  // Optional: Custom message persistence
  async onStart() {
    // Load previous messages from SQL if needed
    const saved = await this.sql`SELECT * FROM messages ORDER BY timestamp`;

    if (saved.length > 0) {
      // Restore message history
      console.log('Restored', saved.length, 'messages');
    }
  }
}

export default StreamingChatAgent;
