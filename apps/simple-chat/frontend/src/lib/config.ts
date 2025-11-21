import { StartScreenPrompt } from "@openai/chatkit";

export const CHATKIT_API_URL =
  import.meta.env.VITE_CHATKIT_API_URL ?? "/chatkit";

export const CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const THEME_STORAGE_KEY = "simple-chat-theme";

export const GREETING = "Welcome! How can I help you today?";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Tell me a joke",
    prompt: "Tell me a funny joke",
    icon: "sparkle",
  },
  {
    label: "Explain something",
    prompt: "Can you explain how machine learning works?",
    icon: "book-open",
  },
  {
    label: "Help me write",
    prompt: "Help me write a professional email",
    icon: "square-text",
  },
];
