import { StartScreenPrompt } from "@openai/chatkit";

export const CHATKIT_API_URL =
  import.meta.env.VITE_CHATKIT_API_URL ?? "/chatkit";

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const ARTICLES_API_URL =
  import.meta.env.VITE_ARTICLES_API_URL ?? "/articles";

export const THEME_STORAGE_KEY = "news-guide-theme";

export const GREETING = "I’m here to help you find the latest news from Foxhollow";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Browse trending stories",
    prompt: "What's trending right now?",
    icon: "globe",
  },
  {
    label: "Read some gossip",
    prompt: "Any small-town drama lately?",
    icon: "sparkle",
  },
  {
    label: "Get public works updates",
    prompt: "What's the latest on public infrastructure projects?",
    icon: "sparkle",
  },
  {
    label: "Summarize this page",
    prompt: "Give me a summary of this page.",
    icon: "book-open",
  },
];

export const getPlaceholder = (hasThread: boolean) => {
  return hasThread
    ? "Ask for related stories"
    : "Any small-town drama this week?";
};
