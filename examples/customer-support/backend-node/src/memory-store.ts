import type { ThreadMetadata, Thread, ThreadItem, Page, HiddenContextItem } from './chatkit-types';

interface ThreadState {
  thread: ThreadMetadata;
  items: ThreadItem[];
}

export class MemoryStore {
  private threads: Map<string, ThreadState> = new Map();
  private threadIdCounter = 0;
  private itemIdCounter = 0;

  generateThreadId(): string {
    return `thread_${++this.threadIdCounter}`;
  }

  generateItemId(type: string): string {
    return `${type}_${++this.itemIdCounter}`;
  }

  async loadThread(threadId: string): Promise<ThreadMetadata> {
    const state = this.threads.get(threadId);
    if (!state) {
      throw new Error(`Thread ${threadId} not found`);
    }
    return { ...state.thread };
  }

  async saveThread(thread: ThreadMetadata): Promise<void> {
    const state = this.threads.get(thread.id);
    if (state) {
      state.thread = { ...thread };
    } else {
      this.threads.set(thread.id, {
        thread: { ...thread },
        items: [],
      });
    }
  }

  async loadThreads(limit: number, after: string | null, order: 'asc' | 'desc'): Promise<Page<ThreadMetadata>> {
    const threads = Array.from(this.threads.values())
      .map((state) => ({ ...state.thread }))
      .sort((a, b) => {
        const aTime = a.created_at.getTime();
        const bTime = b.created_at.getTime();
        return order === 'desc' ? bTime - aTime : aTime - bTime;
      });

    let startIndex = 0;
    if (after) {
      const afterIndex = threads.findIndex((t) => t.id === after);
      startIndex = afterIndex >= 0 ? afterIndex + 1 : 0;
    }

    const slice = threads.slice(startIndex, startIndex + limit + 1);
    const hasMore = slice.length > limit;
    const data = hasMore ? slice.slice(0, limit) : slice;
    const nextAfter = hasMore && data.length > 0 ? data[data.length - 1].id : null;

    return {
      data,
      has_more: hasMore,
      after: nextAfter,
    };
  }

  async deleteThread(threadId: string): Promise<void> {
    this.threads.delete(threadId);
  }

  async loadThreadItems(threadId: string, after: string | null, limit: number, order: 'asc' | 'desc'): Promise<Page<ThreadItem>> {
    const state = this.threads.get(threadId);
    if (!state) {
      // Return empty page for non-existent threads
      return { data: [], has_more: false, after: null };
    }

    const items = [...state.items].sort((a, b) => {
      const aTime = a.created_at.getTime();
      const bTime = b.created_at.getTime();
      return order === 'desc' ? bTime - aTime : aTime - bTime;
    });

    let startIndex = 0;
    if (after) {
      const afterIndex = items.findIndex((item) => item.id === after);
      startIndex = afterIndex >= 0 ? afterIndex + 1 : 0;
    }

    const slice = items.slice(startIndex, startIndex + limit + 1);
    const hasMore = slice.length > limit;
    const data = hasMore ? slice.slice(0, limit) : slice;
    const nextAfter = hasMore && data.length > 0 ? data[data.length - 1].id : null;

    return {
      data,
      has_more: hasMore,
      after: nextAfter,
    };
  }

  async addThreadItem(threadId: string, item: ThreadItem): Promise<void> {
    const state = this.threads.get(threadId);
    if (!state) {
      throw new Error(`Thread ${threadId} not found`);
    }
    state.items.push({ ...item });
  }

  async saveItem(threadId: string, item: ThreadItem): Promise<void> {
    const state = this.threads.get(threadId);
    if (!state) {
      throw new Error(`Thread ${threadId} not found`);
    }

    const index = state.items.findIndex((i) => i.id === item.id);
    if (index >= 0) {
      state.items[index] = { ...item };
    } else {
      state.items.push({ ...item });
    }
  }

  async loadItem(threadId: string, itemId: string): Promise<ThreadItem> {
    const state = this.threads.get(threadId);
    if (!state) {
      throw new Error(`Thread ${threadId} not found`);
    }

    const item = state.items.find((i) => i.id === itemId);
    if (!item) {
      throw new Error(`Item ${itemId} not found`);
    }

    return { ...item };
  }

  async deleteThreadItem(threadId: string, itemId: string): Promise<void> {
    const state = this.threads.get(threadId);
    if (!state) {
      return;
    }
    state.items = state.items.filter((item) => item.id !== itemId);
  }

  async loadFullThread(threadId: string): Promise<Thread> {
    const threadMeta = await this.loadThread(threadId);
    const items = await this.loadThreadItems(threadId, null, 999, 'asc');

    // Filter out hidden context items
    const filteredItems = items.data.filter((item) => item.type !== 'hidden_context_item');

    return {
      ...threadMeta,
      items: {
        ...items,
        data: filteredItems,
      },
    };
  }
}
