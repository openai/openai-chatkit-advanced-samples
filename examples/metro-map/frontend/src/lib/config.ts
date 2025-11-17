import { StartScreenPrompt, ToolOption } from "@openai/chatkit";

export const CHATKIT_API_URL = import.meta.env.VITE_CHATKIT_API_URL ?? "/chatkit";

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const MAP_API_URL = import.meta.env.VITE_MAP_API_URL ?? "/map";

export const THEME_STORAGE_KEY = "metro-map-theme";

export const GREETING = "Welcome aboard—where are you headed on the metro map?";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Fastest route",
    prompt: "What's the quickest way from North Pier to Harborfront?",
    icon: "globe",
  },
  {
    label: "Line overview",
    prompt: "Give me a short rundown of each line and where they cross.",
    icon: "maps",
  },
  {
    label: "Interchanges",
    prompt: "Show me the best transfer stations on this map.",
    icon: "sparkle",
  },
];

export const getPlaceholder = (hasThread: boolean) => {
  return hasThread ? "Ask about a line or transfer" : "Where should we start on this map?";
};

