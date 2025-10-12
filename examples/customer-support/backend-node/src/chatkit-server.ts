import type { Runner, StreamedRunResult } from '@openai/agents';
import type { Agent } from '@openai/agents';
import type { MemoryStore } from './memory-store';
import {
  isStreamingReq,
  type ChatKitRequest,
  type ThreadMetadata,
  type Thread,
  type ThreadItem,
  type UserMessageItem,
  type AssistantMessageItem,
  type ThreadStreamEvent,
  type ThreadCreatedEvent,
  type ThreadItemDoneEvent,
  type ThreadItemAddedEvent,
  type UserMessageInput,
  type AssistantMessageContent,
} from './chatkit-types';

export interface AgentContext<TContext = any> {
  thread: ThreadMetadata;
  store: MemoryStore;
  requestContext: TContext;
}

export abstract class ChatKitServer<TContext = any> {
  constructor(protected store: MemoryStore) {}

  abstract respond(thread: ThreadMetadata, item: UserMessageItem | null, context: TContext): AsyncIterable<ThreadStreamEvent>;

  async process(request: string | Buffer, context: TContext): Promise<{ streaming: boolean; result: AsyncIterable<Uint8Array> | object }> {
    const parsedRequest: ChatKitRequest = JSON.parse(request.toString());
    console.log('Received ChatKit request:', parsedRequest.type);

    if (isStreamingReq(parsedRequest)) {
      return {
        streaming: true,
        result: this.processStreaming(parsedRequest, context),
      };
    } else {
      const result = await this.processNonStreaming(parsedRequest, context);
      return { streaming: false, result };
    }
  }

  private async processNonStreaming(request: ChatKitRequest, context: TContext): Promise<object> {
    switch (request.type) {
      case 'threads.get_by_id':
        return await this.store.loadFullThread(request.params.thread_id);

      case 'threads.list': {
        const params = request.params;
        const threads = await this.store.loadThreads(params.limit || 20, params.after || null, params.order);
        return {
          data: await Promise.all(threads.data.map((t) => this.store.loadFullThread(t.id))),
          has_more: threads.has_more,
          after: threads.after,
        };
      }

      case 'items.list': {
        const params = request.params;
        return await this.store.loadThreadItems(params.thread_id, params.after || null, params.limit || 20, params.order);
      }

      case 'threads.update': {
        const thread = await this.store.loadThread(request.params.thread_id);
        thread.title = request.params.title;
        await this.store.saveThread(thread);
        return await this.store.loadFullThread(request.params.thread_id);
      }

      case 'threads.delete':
        await this.store.deleteThread(request.params.thread_id);
        return {};

      default:
        throw new Error(`Unknown request type: ${(request as any).type}`);
    }
  }

  private async *processStreaming(request: ChatKitRequest, context: TContext): AsyncIterable<Uint8Array> {
    const encoder = new TextEncoder();

    try {
      for await (const event of this.processStreamingImpl(request, context)) {
        const data = JSON.stringify(event, (key, value) => {
          // Omit null values to match Python's exclude_none behavior
          if (value === null) return undefined;
          return value;
        });
        yield encoder.encode(`data: ${data}\n\n`);
      }
    } catch (error) {
      console.error('Error in streaming:', error);
      const errorEvent: ThreadStreamEvent = {
        type: 'error',
        code: 'STREAM_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
        allow_retry: true,
      };
      const data = JSON.stringify(errorEvent);
      yield encoder.encode(`data: ${data}\n\n`);
    }
  }

  private async *processStreamingImpl(request: ChatKitRequest, context: TContext): AsyncIterable<ThreadStreamEvent> {
    switch (request.type) {
      case 'threads.create': {
        const thread: Thread = {
          id: this.store.generateThreadId(),
          created_at: new Date(),
          status: { type: 'active' },
          metadata: {},
          items: { data: [], has_more: false, after: null },
        };
        await this.store.saveThread(thread);

        yield {
          type: 'thread.created',
          thread,
        } as ThreadCreatedEvent;

        const userMessage = await this.buildUserMessageItem(request.params.input, thread);

        yield* this.processNewThreadItemRespond(thread, userMessage, context);
        break;
      }

      case 'threads.add_user_message': {
        const thread = await this.store.loadThread(request.params.thread_id);
        const userMessage = await this.buildUserMessageItem(request.params.input, thread);

        yield* this.processNewThreadItemRespond(thread, userMessage, context);
        break;
      }

      default:
        throw new Error(`Unknown streaming request type: ${(request as any).type}`);
    }
  }

  private async *processNewThreadItemRespond(thread: ThreadMetadata, item: UserMessageItem, context: TContext): AsyncIterable<ThreadStreamEvent> {
    await this.store.addThreadItem(thread.id, item);

    // Emit thread.item.done for user message IMMEDIATELY
    // This closes the user message right away
    yield {
      type: 'thread.item.done',
      item,
    } as ThreadItemDoneEvent;

    // Now process assistant response
    // The respond() method will emit thread.item.added for the assistant
    yield* this.processEvents(thread, context, () => this.respond(thread, item, context));
  }

  private async *processEvents(thread: ThreadMetadata, context: TContext, stream: () => AsyncIterable<ThreadStreamEvent>): AsyncIterable<ThreadStreamEvent> {
    // Allow the response to start streaming
    await new Promise((resolve) => setImmediate(resolve));

    try {
      for await (const event of stream()) {
        if (event.type === 'thread.item.done') {
          await this.store.addThreadItem(thread.id, event.item);
        }

        // Don't send hidden context items back to the client
        const shouldSwallowEvent = event.type === 'thread.item.done' && (event.item as any).type === 'hidden_context_item';

        if (!shouldSwallowEvent) {
          yield event;
        }
      }
    } catch (error) {
      yield {
        type: 'error',
        code: 'STREAM_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
        allow_retry: true,
      };
    }
  }

  private async buildUserMessageItem(input: UserMessageInput, thread: ThreadMetadata): Promise<UserMessageItem> {
    return {
      type: 'user_message',
      id: this.store.generateItemId('message'),
      content: input.content,
      thread_id: thread.id,
      created_at: new Date(),
      attachments: [],
      quoted_text: input.quoted_text,
      inference_options: input.inference_options,
    };
  }
}

// Helper to stream agent response to ChatKit events
export async function* streamAgentResponse(result: StreamedRunResult<any, any>, threadId: string, store: MemoryStore): AsyncIterable<ThreadStreamEvent> {
  let fullText = '';
  let itemAdded = false;
  let contentPartAdded = false;
  const itemId = store.generateItemId('message');
  const createdAt = new Date();

  // Stream the events
  for await (const event of result) {
    const data = (event as any).data;
    const eventType = data?.type;

    if (eventType === 'output_text_delta' && data?.delta) {
      // First delta: emit thread.item.added
      if (!itemAdded) {
        yield {
          type: 'thread.item.added',
          item: {
            type: 'assistant_message',
            id: itemId,
            thread_id: threadId,
            content: [
              {
                annotations: [],
                text: '',
                type: 'output_text',
              },
            ],
            created_at: createdAt,
          },
        } as ThreadItemAddedEvent;
        itemAdded = true;
      }

      // Second: emit content_part.added
      if (!contentPartAdded) {
        yield {
          type: 'thread.item.updated',
          item_id: itemId,
          update: {
            type: 'assistant_message.content_part.added',
            content_index: 0,
            content: {
              annotations: [],
              text: '',
              type: 'output_text',
            },
          },
        };
        contentPartAdded = true;
      }

      // Emit delta
      fullText += data.delta;
      yield {
        type: 'thread.item.updated',
        item_id: itemId,
        update: {
          type: 'assistant_message.content_part.text_delta',
          content_index: 0,
          delta: data.delta,
        },
      };
    }
  }

  // Emit content_part.done
  if (contentPartAdded) {
    yield {
      type: 'thread.item.updated',
      item_id: itemId,
      update: {
        type: 'assistant_message.content_part.done',
        content_index: 0,
        content: {
          annotations: [],
          text: fullText,
          type: 'output_text',
        },
      },
    };
  }

  // Send final done event with either accumulated text or final output
  const finalItem: AssistantMessageItem = {
    type: 'assistant_message',
    id: itemId,
    thread_id: threadId,
    content: [
      {
        annotations: [],
        text: fullText || result.finalOutput || '',
        type: 'output_text',
      },
    ],
    created_at: createdAt,
  };

  yield {
    type: 'thread.item.done',
    item: finalItem,
  } as ThreadItemDoneEvent;
}
