// ChatKit Protocol Types based on Python chatkit.types

export interface ThreadMetadata {
  id: string;
  title?: string;
  created_at: Date;
  status?: { type: string };
  metadata?: Record<string, any>;
}

export interface Thread extends ThreadMetadata {
  items: Page<ThreadItem>;
}

export interface Page<T> {
  data: T[];
  has_more: boolean;
  after: string | null;
}

export type ThreadItem =
  | UserMessageItem
  | AssistantMessageItem
  | HiddenContextItem;

export interface UserMessageItem {
  type: 'user_message';
  id: string;
  thread_id: string;
  content: UserMessageContent[];
  created_at: Date;
  attachments?: any[];
  quoted_text?: string;
  inference_options?: any;
}

export type UserMessageContent = UserMessageTextContent;

export interface UserMessageTextContent {
  type: 'input_text';
  text: string;
}

export interface AssistantMessageItem {
  type: 'assistant_message';
  id: string;
  thread_id: string;
  content: AssistantMessageContent[];
  created_at: Date;
}

export interface AssistantMessageContent {
  type: 'output_text';
  text: string;
  annotations?: any[];
}

export interface HiddenContextItem {
  type: 'hidden_context_item';
  id: string;
  thread_id: string;
  content: string;
  created_at: Date;
}

// Request types
export type ChatKitRequest =
  | ThreadsListReq
  | ThreadsCreateReq
  | ThreadsGetByIdReq
  | ThreadsAddUserMessageReq
  | ThreadsUpdateReq
  | ThreadsDeleteReq
  | ItemsListReq;

export interface ThreadsListReq {
  type: 'threads.list';
  params: {
    limit?: number;
    after?: string | null;
    order: 'asc' | 'desc';
  };
}

export interface ThreadsCreateReq {
  type: 'threads.create';
  params: {
    input: UserMessageInput;
  };
}

export interface ThreadsGetByIdReq {
  type: 'threads.get_by_id';
  params: {
    thread_id: string;
  };
}

export interface ThreadsAddUserMessageReq {
  type: 'threads.add_user_message';
  params: {
    thread_id: string;
    input: UserMessageInput;
  };
}

export interface ThreadsUpdateReq {
  type: 'threads.update';
  params: {
    thread_id: string;
    title: string;
  };
}

export interface ThreadsDeleteReq {
  type: 'threads.delete';
  params: {
    thread_id: string;
  };
}

export interface ItemsListReq {
  type: 'items.list';
  params: {
    thread_id: string;
    limit?: number;
    after?: string | null;
    order: 'asc' | 'desc';
  };
}

export interface UserMessageInput {
  content: UserMessageContent[];
  attachments?: string[];
  quoted_text?: string;
  inference_options?: any;
}

// Event types for streaming
export type ThreadStreamEvent =
  | ThreadCreatedEvent
  | ThreadItemAddedEvent
  | ThreadItemDoneEvent
  | ThreadItemUpdatedEvent
  | ThreadUpdatedEvent
  | ErrorEvent;

export interface ThreadCreatedEvent {
  type: 'thread.created';
  thread: Thread;
}

export interface ThreadItemAddedEvent {
  type: 'thread.item.added';
  item: ThreadItem;
}

export interface ThreadItemDoneEvent {
  type: 'thread.item.done';
  item: ThreadItem;
}

export interface ThreadItemUpdatedEvent {
  type: 'thread.item.updated';
  item_id: string;
  update: any;
}

export interface ThreadUpdatedEvent {
  type: 'thread.updated';
  thread: Thread;
}

export interface ErrorEvent {
  type: 'error';
  code: string;
  message?: string;
  allow_retry: boolean;
}

export function isStreamingReq(req: ChatKitRequest): boolean {
  return (
    req.type === 'threads.create' ||
    req.type === 'threads.add_user_message'
  );
}

export { isStreamingReq as isStreamingRequest };
