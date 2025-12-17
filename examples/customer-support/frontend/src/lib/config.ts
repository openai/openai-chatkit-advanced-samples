import { StartScreenPrompt } from "@openai/chatkit";

import type { SupportView } from "../types/support";

export const THEME_STORAGE_KEY = "customer-support-theme";

const SUPPORT_API_BASE = import.meta.env.VITE_SUPPORT_API_BASE ?? "/support";

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const SUPPORT_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY ??
  "domain_pk_localhost_dev";

export const SUPPORT_CHATKIT_API_URL =
  import.meta.env.VITE_SUPPORT_CHATKIT_API_URL ?? `${SUPPORT_API_BASE}/chatkit`;

export const SUPPORT_CUSTOMER_URL =
  import.meta.env.VITE_SUPPORT_CUSTOMER_URL ?? `${SUPPORT_API_BASE}/customer`;

const OVERVIEW_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Book a flight",
    prompt:
      "Book a new trip for the traveler. Remind me to attach an inspiration photo and handle the planning as their concierge.",
    icon: "map-pin",
  },
  {
    label: "Account snapshot",
    prompt: "Give me a quick overview of my account.",
    icon: "sparkle",
  },
  {
    label: "Trip readiness",
    prompt: "Check if there are open items I should handle before my flights.",
    icon: "notebook",
  },
  {
    label: "VIP notes",
    prompt: "Summarize the VIP notes that matter most today.",
    icon: "profile",
  },
];

const TRIP_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Change my seat",
    prompt: "Move me to seat 14C on flight OA476.",
    icon: "lightbulb",
  },
  {
    label: "Cancel trip",
    prompt: "Cancel my upcoming trip and request a refund.",
    icon: "sparkle",
  },
  {
    label: "Add checked bag",
    prompt: "Add one more checked bag to the reservation.",
    icon: "suitcase",
  },
  {
    label: "Set a meal preference",
    prompt: "Set my meal preference.",
    icon: "notebook-pencil",
  },
];

const LOYALTY_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Explain Gold perks",
    prompt: "Explain what Aviator Gold currently unlocks for me.",
    icon: "star",
  },
  {
    label: "Path to Platinum",
    prompt:
      "Show how close I am to Aviator Platinum and what would help me get there.",
    icon: "chart",
  },
  {
    label: "Upgrade offers",
    prompt: "Surface any upgrade or lounge offers we should mention today.",
    icon: "sparkle-double",
  },
];

export const SUPPORT_STARTER_PROMPTS: Record<SupportView, StartScreenPrompt[]> =
  {
    overview: OVERVIEW_PROMPTS,
    trips: TRIP_PROMPTS,
    loyalty: LOYALTY_PROMPTS,
  };

export const SUPPORT_GREETINGS: Record<SupportView, string> = {
  overview: "How can I keep your day running smoothly?",
  trips: "Need help with flights, seats, or booking?",
  loyalty: "Let's talk loyalty perks, points, and status.",
};
