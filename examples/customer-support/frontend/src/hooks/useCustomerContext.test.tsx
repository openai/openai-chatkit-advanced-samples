// @vitest-environment jsdom
import { act, StrictMode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useCustomerContext, type CustomerProfile } from "./useCustomerContext";

function profile(name: string): CustomerProfile {
  return {
    customer_id: name, name, loyalty_status: "basic", loyalty_id: "fixture",
    email: "fixture@example.invalid", phone: "", home_airport: "LHR",
    preferred_routes: [], travel_summary: "", tier_benefits: [],
    loyalty_progress: {
      current_tier: "basic", next_tier: "silver", points_earned: 0, points_required: 1,
      segments_flown: 0, segments_required: 1, renewal_date: "2026-01-01",
    },
    segments: [], bags_checked: 0, meal_preference: null, special_assistance: null,
    timeline: [], spotlight: [],
  };
}

let root: Root;
let container: HTMLDivElement;
let current: ReturnType<typeof useCustomerContext>;
let requests: Array<{ resolve: (response: Response) => void; reject: (error: Error) => void }>;

function Harness({ threadId }: { threadId: string | null }) {
  current = useCustomerContext(threadId);
  return null;
}
async function render(threadId: string | null, strict = false) {
  await act(async () => {
    const component = <Harness threadId={threadId} />;
    root.render(strict ? <StrictMode>{component}</StrictMode> : component);
  });
}
async function succeed(index: number, name: string) {
  await act(async () => requests[index].resolve(Response.json({ customer: profile(name) })));
}
async function fail(index: number) {
  await act(async () => requests[index].reject(new Error("Synthetic profile failure")));
}

beforeEach(() => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  requests = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(() => new Promise<Response>((resolve, reject) => {
    requests.push({ resolve, reject });
  }));
  container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);
});
afterEach(async () => {
  await act(async () => root.unmount());
  container.remove();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("customer profile request ownership", () => {
  it.each([false, true])("ignores an obsolete thread response, failure=%s", async (failure) => {
    await render("old-thread");
    await render("new-thread");
    await succeed(1, "new customer");
    if (failure) await fail(0);
    else await succeed(0, "old customer");
    expect(current.profile?.name).toBe("new customer");
    expect(current.error).toBeNull();
    expect(current.loading).toBe(false);
  });

  it.each([false, true])("keeps the current request loading when obsolete work finishes, failure=%s", async (failure) => {
    await render("old-thread");
    await render("new-thread");
    if (failure) await fail(0);
    else await succeed(0, "old customer");
    expect(current.loading).toBe(true);
    expect(current.error).toBeNull();
    expect(current.profile).toBeNull();
    await succeed(1, "new customer");
    expect(current.profile?.name).toBe("new customer");
  });

  it("the newest manual refresh wins for the same thread", async () => {
    await render("thread");
    await succeed(0, "initial");
    let first!: Promise<void>, second!: Promise<void>;
    await act(async () => { first = current.refresh(); second = current.refresh(); });
    await succeed(2, "latest");
    await succeed(1, "older");
    await act(async () => { await Promise.all([first, second]); });
    expect(current.profile?.name).toBe("latest");
  });

  it.each([false, true])("an applied update supersedes an outstanding fetch, failure=%s", async (failure) => {
    await render("thread");
    await act(async () => current.setProfile(profile("updated locally")));
    if (failure) await fail(0);
    else await succeed(0, "before update");
    expect(current.profile?.name).toBe("updated locally");
    expect(current.error).toBeNull();
    expect(current.loading).toBe(false);
  });

  it("ignores the obsolete Strict Mode effect request", async () => {
    await render("thread", true);
    expect(requests).toHaveLength(2);
    await succeed(1, "current effect");
    await succeed(0, "old effect");
    expect(current.profile?.name).toBe("current effect");
  });

  it("still publishes the current request's error and clears it on retry", async () => {
    await render("thread");
    await fail(0);
    expect(current.profile).toBeNull();
    expect(current.error).toBe("Synthetic profile failure");
    expect(current.loading).toBe(false);
    let refresh!: Promise<void>;
    await act(async () => { refresh = current.refresh(); });
    expect(current.loading).toBe(true);
    expect(current.error).toBeNull();
    await succeed(1, "recovered");
    await refresh;
    expect(current.profile?.name).toBe("recovered");
  });

  it("a transition to the default profile ignores the earlier thread", async () => {
    await render("thread");
    await render(null);
    await succeed(1, "default customer");
    await succeed(0, "thread customer");
    expect(current.profile?.name).toBe("default customer");
  });
});
