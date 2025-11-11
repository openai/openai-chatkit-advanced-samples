import { StartScreenPrompt } from "@openai/chatkit";

export const THEME_STORAGE_KEY = "customer-support-theme";

const SUPPORT_API_BASE =
  import.meta.env.VITE_SUPPORT_API_BASE ?? "/support";

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const SUPPORT_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const SUPPORT_CHATKIT_API_URL =
  import.meta.env.VITE_SUPPORT_CHATKIT_API_URL ??
  `${SUPPORT_API_BASE}/chatkit`;

export const SUPPORT_CUSTOMER_URL =
  import.meta.env.VITE_SUPPORT_CUSTOMER_URL ??
  `${SUPPORT_API_BASE}/customer`;

export const SUPPORT_GREETING =
  import.meta.env.VITE_SUPPORT_GREETING ??
  "How can I make your trip smoother today?";

export const SUPPORT_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Change my seat",
    prompt: "Can you move me to seat 14C on flight OA476?",
    icon: "lightbulb",
  },
  {
    label: "Cancel trip",
    prompt: "I need to cancel my trip and request a refund.",
    icon: "sparkle",
  },
  {
    label: "Add checked bag",
    prompt: "Add one more checked bag to my reservation.",
    icon: "suitcase",
  },
  {
    label: "Set a meal preference",
    prompt: "Set a meal preference for my trip.",
    icon: "notebook-pencil",
  },
];
