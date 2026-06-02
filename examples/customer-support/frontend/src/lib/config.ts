import { StartScreenPrompt } from "@openai/chatkit";

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

export const SUPPORT_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Download issues",
    prompt: "I'm having trouble downloading a resource I purchased. Can you help?",
    icon: "lightbulb",
  },
  {
    label: "Refund request",
    prompt: "How do I request a refund for a purchase?",
    icon: "sparkle",
  },
  {
    label: "Seller account",
    prompt: "How do I become a seller on TPT and start uploading resources?",
    icon: "profile",
  },
  {
    label: "Payment & billing",
    prompt: "I have a question about a charge on my account.",
    icon: "notebook",
  },
];

export const SUPPORT_GREETING = "How can I help you with TPT today?";
