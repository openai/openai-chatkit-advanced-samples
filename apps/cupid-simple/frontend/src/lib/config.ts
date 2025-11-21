import { StartScreenPrompt } from "@openai/chatkit";

export const CHATKIT_API_URL =
  import.meta.env.VITE_CHATKIT_API_URL ?? "/chatkit";

export const CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const THEME_STORAGE_KEY = "cupid-simple-theme";

export const GREETING = "Cupid v0.1";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Play",
    prompt: "Play",
    icon: "play",
  },
];
