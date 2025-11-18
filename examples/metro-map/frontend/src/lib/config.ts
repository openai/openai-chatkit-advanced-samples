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

export const GREETING = "Welcome to Orbital Transit";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Add a station",
    prompt: "I would like to add a new metro station.",
    icon: "sparkle",
  },
  {
    label: "Plan a route",
    prompt: "What's the quickest way from Cinderia to Lyra Verge?",
    icon: "maps",
  },
  {
    label: "Station overview",
    prompt: "Tell me about the Titan Border station.",
    icon: "map-pin",
  },
  {
    label: "Line overview",
    prompt: "Give me a short rundown of each line and where they cross.",
    icon: "globe",
  },
];

export const getPlaceholder = (hasThread: boolean) => {
  return hasThread ? "I'd like to add a new station." : "Tell me about the Lyra Verge station.";
};

