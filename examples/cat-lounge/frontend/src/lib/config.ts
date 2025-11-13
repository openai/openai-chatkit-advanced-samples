import { StartScreenPrompt } from "@openai/chatkit";
import { DEFAULT_CAT_STATE } from "./cat";

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

export const CAT_STATE_API_URL =
  import.meta.env.VITE_CAT_STATE_API_URL ?? "/cats";

export const THEME_STORAGE_KEY = "chatkit-boilerplate-theme";

export const GREETING = "Welcome to the cozy cat lounge";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Name ideas",
    prompt: "Could you suggest some fun names for the cat?",
    icon: "book-open",
  },
  {
    label: "Check on the cat",
    prompt: "How is the cat doing today?",
    icon: "circle-question",
  },
  {
    label: "Feed time",
    prompt: "Please feed the cat something tasty.",
    icon: "sparkle",
  },
  {
    label: "Play time",
    prompt: "Please play with the cat using a fun toy.",
    icon: "confetti",
  },
  {
    label: "Profile card",
    prompt: "Can you show me the cat's profile card?",
    icon: "square-text",
  },
];

export const getPlaceholder = (catName: string | null) => {
  return catName === DEFAULT_CAT_STATE.name ? "Ask how the cat feels or what it needs" : `${catName}, what would you like to do?`;
};