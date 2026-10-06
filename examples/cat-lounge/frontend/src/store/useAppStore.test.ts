import { afterEach, beforeEach, expect, it, vi } from "vitest";
import confetti from "canvas-confetti";
import { DEFAULT_CAT_STATE, type CatStatePayload } from "../lib/cat";
import { useAppStore } from "./useAppStore";

vi.mock("canvas-confetti", () => ({ default: Object.assign(vi.fn(), { shapeFromText: vi.fn() }) }));
const cat = (threadId: string, name: string): CatStatePayload => ({ ...DEFAULT_CAT_STATE, threadId, name, updatedAt: "2026-01-01T00:00:00Z" });
function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((ok, fail) => { resolve = ok; reject = fail; });
  return { promise, resolve, reject };
}
function reply(value: CatStatePayload) { return Response.json({ cat: value }); }
const state = () => useAppStore.getState();
beforeEach(() => {
  state().setThreadId(null);
  useAppStore.setState({ cat: { ...DEFAULT_CAT_STATE }, threadId: "first" });
  vi.stubGlobal("fetch", vi.fn());
  vi.spyOn(console, "error").mockImplementation(() => {});
});
afterEach(() => { state().setThreadId(null); vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.clearAllMocks(); });

it("ignores a response belonging to a previously selected thread", async () => {
  const old = deferred<Response>(), current = deferred<Response>();
  vi.mocked(fetch).mockReturnValueOnce(old.promise).mockReturnValueOnce(current.promise);
  const loading = state().refreshCat();
  state().setThreadId("second");
  current.resolve(reply(cat("second", "Current")));
  await vi.waitFor(() => expect(state().cat.name).toBe("Current"));
  old.resolve(reply(cat("first", "Obsolete")));
  expect(await loading).toBeUndefined();
  expect(state().cat).toMatchObject({ threadId: "second", name: "Current" });
});

it("keeps the newest same-thread refresh when requests finish out of order", async () => {
  const old = deferred<Response>();
  vi.mocked(fetch).mockReturnValueOnce(old.promise).mockResolvedValueOnce(reply(cat("first", "Newest")));
  const loading = state().refreshCat();
  await state().refreshCat();
  old.resolve(reply(cat("first", "Old")));
  expect(await loading).toBeUndefined();
  expect(state().cat.name).toBe("Newest");
});

it("does not replace a delivered state update with an older refresh", async () => {
  const old = deferred<Response>();
  vi.mocked(fetch).mockReturnValue(old.promise);
  const loading = state().refreshCat();
  state().applyCatUpdate(cat("first", "Updated"));
  old.resolve(reply(cat("first", "Old")));
  expect(await loading).toBeUndefined();
  expect(state().cat.name).toBe("Updated");
});

it("keeps a cleared thread empty when an older response arrives", async () => {
  const old = deferred<Response>();
  vi.mocked(fetch).mockReturnValueOnce(old.promise);
  const loading = state().refreshCat();
  state().setThreadId(null);
  old.resolve(reply(cat("first", "Old")));
  expect(await loading).toBeUndefined();
  expect(state().cat).toMatchObject({ threadId: null, name: "Unnamed Cat" });
});

it("invalidates the first request even after switching away and back", async () => {
  const old = deferred<Response>();
  vi.mocked(fetch).mockReturnValueOnce(old.promise)
    .mockResolvedValueOnce(reply(cat("second", "Other")))
    .mockResolvedValueOnce(reply(cat("first", "Returned")));
  const loading = state().refreshCat();
  state().setThreadId("second");
  await vi.waitFor(() => expect(state().cat.name).toBe("Other"));
  state().setThreadId("first");
  await vi.waitFor(() => expect(state().cat.name).toBe("Returned"));
  old.resolve(reply(cat("first", "Old")));
  expect(await loading).toBeUndefined();
  expect(state().cat.name).toBe("Returned");
});

it("ignores an update tagged for another thread", () => {
  state().applyCatUpdate(cat("second", "Other"));
  expect(state().cat.name).toBe("Unnamed Cat");
  expect(confetti).not.toHaveBeenCalled();
});

it("does not start a stale explicit-thread refresh", async () => {
  vi.mocked(fetch).mockResolvedValue(reply(cat("second", "Other")));
  expect(await state().refreshCat("second")).toBeUndefined();
  expect(fetch).not.toHaveBeenCalled();
  expect(state().cat.name).toBe("Unnamed Cat");
});

it("suppresses an obsolete request error without changing the current state", async () => {
  const old = deferred<Response>();
  vi.mocked(fetch).mockReturnValueOnce(old.promise).mockResolvedValueOnce(reply(cat("first", "Current")));
  const loading = state().refreshCat();
  await state().refreshCat();
  old.reject(new Error("Obsolete failure"));
  await loading;
  expect(console.error).not.toHaveBeenCalled();
  expect(state().cat.name).toBe("Current");
});

it("returns and applies a current successful response", async () => {
  const value = cat("first", "Current");
  vi.mocked(fetch).mockResolvedValue(reply(value));
  expect(await state().refreshCat()).toEqual(value);
  expect(state().cat).toEqual(value);
  expect(confetti).toHaveBeenCalledOnce();
});

it("keeps current error reporting and existing state", async () => {
  vi.mocked(fetch).mockResolvedValue(new Response("", { status: 503 }));
  expect(await state().refreshCat()).toBeUndefined();
  expect(console.error).toHaveBeenCalledOnce();
  expect(state().cat.name).toBe("Unnamed Cat");
});

it("preserves untagged partial updates to the selected cat", () => {
  useAppStore.setState({ cat: cat("first", "Current") });
  state().applyCatUpdate({ energy: 9 });
  expect(state().cat).toMatchObject({ threadId: "first", name: "Current", energy: 9 });
});
