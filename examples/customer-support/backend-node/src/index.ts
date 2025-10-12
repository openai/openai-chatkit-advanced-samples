import dotenv from 'dotenv';
dotenv.config();

import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { Runner } from '@openai/agents';
import { stateManager, supportAgent } from './support-agent';
import type { CustomerProfile } from './airline-state';
import { ChatKitServer, streamAgentResponse } from './chatkit-server';
import type { ThreadMetadata, UserMessageItem, ThreadStreamEvent } from './chatkit-types';
import { MemoryStore } from './memory-store';

const DEFAULT_THREAD_ID = 'demo_default_thread';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

function formatCustomerContext(profile: CustomerProfile): string {
  const segments = profile.segments
    .map((segment) => `- ${segment.flight_number} ${segment.origin}->${segment.destination} on ${segment.date} seat ${segment.seat} (${segment.status})`)
    .join('\n');

  const timeline = profile.timeline.slice(0, 3);
  const recent = timeline.map((entry) => `  * ${entry.entry} (${entry.timestamp})`).join('\n');

  return `Customer Profile
Name: ${profile.name} (${profile.loyalty_status})
Loyalty ID: ${profile.loyalty_id}
Contact: ${profile.email}, ${profile.phone}
Checked Bags: ${profile.bags_checked}
Meal Preference: ${profile.meal_preference || 'Not set'}
Special Assistance: ${profile.special_assistance || 'None'}
Upcoming Segments:
${segments}
Recent Service Timeline:
${recent || '  * No service actions recorded yet.'}`;
}

function userMessageText(item: UserMessageItem): string {
  return item.content
    .filter((part) => part.type === 'input_text')
    .map((part) => part.text)
    .join(' ')
    .trim();
}

class CustomerSupportServer extends ChatKitServer<any> {
  constructor(private agentState: typeof stateManager) {
    super(new MemoryStore());
  }

  async *respond(thread: ThreadMetadata, item: UserMessageItem | null, _context: any): AsyncIterable<ThreadStreamEvent> {
    if (!item) {
      return;
    }

    const messageText = userMessageText(item);
    if (!messageText) {
      return;
    }

    // Use thread ID or default
    const threadKey = thread.id || DEFAULT_THREAD_ID;
    const profile = this.agentState.getProfile(threadKey);
    const contextPrompt = formatCustomerContext(profile);

    // const threadContext = await this.store.loadThread(threadKey);
    // ToDo: put message history into context, maybe ChatKitServer should do this?

    const combinedPrompt = `${contextPrompt}\n\nCurrent request: ${messageText}\nRespond as the OpenSkies concierge.`;

    const runner = new Runner();
    const result = await runner.run(supportAgent, combinedPrompt, {
      context: { threadId: threadKey },
      stream: true,
    });

    // streamAgentResponse will emit thread.item.added when it sees the first output
    yield* streamAgentResponse(result, thread.id, this.store);
  }
}

const supportServer = new CustomerSupportServer(stateManager);

// Main ChatKit endpoint
app.post('/support/chatkit', async (c) => {
  try {
    const payload = await c.req.arrayBuffer();
    const result = await supportServer.process(Buffer.from(payload), {
      request: c.req,
    });

    if (result.streaming) {
      const stream = ReadableStream.from(result.result as AsyncIterable<Uint8Array>);
      return new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          Connection: 'keep-alive',
        },
      });
    } else {
      return c.json(result.result);
    }
  } catch (error) {
    console.error('Error in chatkit endpoint:', error);
    return c.json(
      {
        error: error instanceof Error ? error.message : 'Internal server error',
      },
      500
    );
  }
});

// Get customer profile endpoint
app.get('/support/customer', (c) => {
  const threadId = c.req.query('thread_id') || DEFAULT_THREAD_ID;
  const data = stateManager.toDict(threadId);
  return c.json({ customer: data });
});

// Health check endpoint
app.get('/support/health', (c) => {
  return c.json({ status: 'healthy' });
});

const port = 4001;
console.log(`Server is running on port ${port}`);

serve({
  fetch: app.fetch,
  port,
});
