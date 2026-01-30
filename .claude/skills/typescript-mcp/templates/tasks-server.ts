/**
 * Tasks-Server MCP Template (v1.24.0+)
 *
 * An MCP server demonstrating the Tasks feature for long-running operations.
 * Tasks return a handle for polling results instead of blocking on response.
 *
 * Use Tasks when:
 * - Operations take >30 seconds (LLM timeout risk)
 * - You need to track progress incrementally
 * - Operations may require additional input mid-execution
 * - Batch processing with per-item status updates
 *
 * Task States: working → input_required → completed / failed / cancelled
 *
 * Setup:
 * 1. npm install @modelcontextprotocol/sdk@^1.24.0 hono zod
 * 2. npm install -D @cloudflare/workers-types wrangler typescript
 * 3. Add KV namespace binding for task state (see wrangler.jsonc)
 * 4. wrangler deploy
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { Hono } from 'hono';
import { z } from 'zod';

type Env = {
  // KV for persistent task state
  TASKS: KVNamespace;
  // Optional: D1 for operation data
  DB?: D1Database;
};

// Task state stored in KV
interface TaskState {
  id: string;
  status: 'working' | 'input_required' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
  progressMessage?: string;
  result?: unknown;
  error?: string;
  inputRequest?: {
    prompt: string;
    schema?: Record<string, unknown>;
  };
  createdAt: string;
  updatedAt: string;
  ttl: number;
}

// Server with tasks capability
const server = new McpServer({
  name: 'tasks-server',
  version: '1.0.0',
  capabilities: {
    tasks: {
      list: {},      // Enable tasks/list method
      cancel: {},    // Enable tasks/cancel method
      requests: {
        tools: { call: {} }  // Enable task mode for tools/call
      }
    }
  }
});

/**
 * Tool 1: Long-running data analysis with task support
 *
 * taskSupport options:
 * - 'forbidden': Never run as task (immediate response required)
 * - 'optional': Can run either way (client decides)
 * - 'required': Must run as task (always returns taskId)
 */
server.registerTool(
  'analyze-dataset',
  {
    description: 'Analyzes a large dataset. Returns immediately with taskId for long-running operations.',
    inputSchema: z.object({
      datasetId: z.string().describe('Dataset identifier'),
      analysisType: z.enum(['summary', 'detailed', 'full']).describe('Analysis depth')
    }),
    execution: { taskSupport: 'optional' }
  },
  async ({ datasetId, analysisType }, extra) => {
    // If running as task, extra.task contains taskId and we can update progress
    if (extra?.task) {
      const taskId = extra.task.taskId;
      const env = extra.env as Env;

      // Initialize task state
      const taskState: TaskState = {
        id: taskId,
        status: 'working',
        progress: 0,
        progressMessage: 'Starting analysis...',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        ttl: extra.task.ttl || 60000
      };

      await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState), {
        expirationTtl: Math.ceil(taskState.ttl / 1000)
      });

      // Simulate long-running analysis (in production, use Durable Objects or Queues)
      // For this template, we'll complete synchronously but demonstrate the pattern
      const result = await performAnalysis(datasetId, analysisType, async (progress, message) => {
        taskState.progress = progress;
        taskState.progressMessage = message;
        taskState.updatedAt = new Date().toISOString();
        await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState));
      });

      // Mark complete
      taskState.status = 'completed';
      taskState.result = result;
      taskState.progress = 100;
      taskState.progressMessage = 'Analysis complete';
      taskState.updatedAt = new Date().toISOString();
      await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState));

      return {
        content: [{ type: 'text', text: JSON.stringify(result) }]
      };
    }

    // Immediate mode (no task)
    const result = await performAnalysis(datasetId, analysisType);
    return {
      content: [{ type: 'text', text: JSON.stringify(result) }]
    };
  }
);

/**
 * Tool 2: Batch processing that may require input mid-execution
 *
 * Demonstrates input_required state - pauses for user confirmation
 */
server.registerTool(
  'batch-process',
  {
    description: 'Processes items in batch, may pause for confirmation on certain items',
    inputSchema: z.object({
      items: z.array(z.string()).describe('Items to process'),
      requireConfirmation: z.boolean().default(false).describe('Pause for confirmation on flagged items')
    }),
    execution: { taskSupport: 'required' }
  },
  async ({ items, requireConfirmation }, extra) => {
    if (!extra?.task) {
      return {
        content: [{ type: 'text', text: 'Error: This tool requires task mode' }],
        isError: true
      };
    }

    const taskId = extra.task.taskId;
    const env = extra.env as Env;

    const taskState: TaskState = {
      id: taskId,
      status: 'working',
      progress: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ttl: extra.task.ttl || 300000
    };

    const results: { item: string; status: string }[] = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      taskState.progress = Math.round((i / items.length) * 100);
      taskState.progressMessage = `Processing ${i + 1}/${items.length}: ${item}`;
      taskState.updatedAt = new Date().toISOString();
      await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState));

      // Example: flag items with "review" in name
      if (requireConfirmation && item.toLowerCase().includes('review')) {
        taskState.status = 'input_required';
        taskState.inputRequest = {
          prompt: `Item "${item}" requires review. Approve processing?`,
          schema: {
            type: 'object',
            properties: {
              approved: { type: 'boolean' }
            },
            required: ['approved']
          }
        };
        await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState));

        // In production, wait for client to provide input via tasks/respond
        // For this template, we'll auto-approve
        await new Promise(resolve => setTimeout(resolve, 100));

        taskState.status = 'working';
        taskState.inputRequest = undefined;
      }

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 50));
      results.push({ item, status: 'processed' });
    }

    taskState.status = 'completed';
    taskState.progress = 100;
    taskState.progressMessage = `Completed ${items.length} items`;
    taskState.result = results;
    taskState.updatedAt = new Date().toISOString();
    await env.TASKS.put(`task:${taskId}`, JSON.stringify(taskState));

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ processed: results.length, results })
      }]
    };
  }
);

/**
 * Tool 3: Quick operation - explicitly forbids task mode
 */
server.registerTool(
  'quick-lookup',
  {
    description: 'Fast lookup that must return immediately',
    inputSchema: z.object({
      key: z.string().describe('Lookup key')
    }),
    execution: { taskSupport: 'forbidden' }
  },
  async ({ key }) => {
    // Simulated lookup
    const data = { key, value: `Result for ${key}`, timestamp: Date.now() };
    return {
      content: [{ type: 'text', text: JSON.stringify(data) }]
    };
  }
);

// Helper: Simulated analysis function
async function performAnalysis(
  datasetId: string,
  analysisType: string,
  onProgress?: (progress: number, message: string) => Promise<void>
): Promise<Record<string, unknown>> {
  const steps = analysisType === 'full' ? 5 : analysisType === 'detailed' ? 3 : 1;

  for (let i = 0; i < steps; i++) {
    if (onProgress) {
      await onProgress(
        Math.round(((i + 1) / steps) * 100),
        `Step ${i + 1}/${steps} complete`
      );
    }
    // Simulate work
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return {
    datasetId,
    analysisType,
    recordCount: Math.floor(Math.random() * 10000),
    summary: {
      mean: 42.5,
      median: 40,
      stdDev: 12.3
    },
    completedAt: new Date().toISOString()
  };
}

// HTTP endpoint setup
const app = new Hono<{ Bindings: Env }>();

app.get('/', (c) => {
  return c.json({
    name: 'tasks-server',
    version: '1.0.0',
    features: ['tasks'],
    tools: [
      { name: 'analyze-dataset', taskSupport: 'optional' },
      { name: 'batch-process', taskSupport: 'required' },
      { name: 'quick-lookup', taskSupport: 'forbidden' }
    ]
  });
});

// Task status endpoint (for debugging)
app.get('/tasks/:taskId', async (c) => {
  const taskId = c.req.param('taskId');
  const state = await c.env.TASKS.get(`task:${taskId}`);

  if (!state) {
    return c.json({ error: 'Task not found' }, 404);
  }

  return c.json(JSON.parse(state));
});

app.post('/mcp', async (c) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true
  });

  c.res.raw.on('close', () => transport.close());

  await server.connect(transport);
  await transport.handleRequest(c.req.raw, c.res.raw, await c.req.json());

  return c.body(null);
});

export default app;
