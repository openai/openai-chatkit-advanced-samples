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

const DEFAULT_START_SCREEN_PROMPTS: StartScreenPrompt[] = [
    {
      label: "Add a station",
      prompt: "I would like to add a new metro station.",
      icon: "sparkle",
    },
    {
      label: "Plan a route",
      prompt: [
        {
          type: "input_text",
          text: "What's the quickest way from ",
        },
        {
          type: "input_tag",
          text: "Cinderia",
          id: "cinderia",
          group: "Stations",
          interactive: true,
          data: {
            type: "station",
            station_id: "cinderia",
            name: "Cinderia",
          },
        },
        {
          type: "input_text",
          text: " to ",
        },
        {
          type: "input_tag",
          text: "Lyra Verge",
          id: "lyra-verge",
          group: "Stations",
          interactive: true,
          data: {
            type: "station",
            station_id: "lyra-verge",
            name: "Lyra Verge",
          },
        },
        {
          type: "input_text",
          text: "?",
        },
      ],
      icon: "maps",
    },
    {
      label: "Station overview",
      prompt: [
        {
          type: "input_text",
          text: "Tell me about the ",
        },
        {
          type: "input_tag",
          text: "Titan Border",
          id: "titan-border",
          group: "Stations",
          interactive: true,
          data: {
            type: "station",
            station_id: "titan-border",
            name: "Titan Border",
          },
        },
        {
          type: "input_text",
          text: " station.",
        },
      ],
      icon: "map-pin",
    },
    {
      label: "Line overview",
      prompt: "Give me a short rundown of each line and where they cross.",
      icon: "globe",
    },
];

export const getGreeting = (selectedStationIds: string[]) => {
  if (selectedStationIds.length > 1) {
    return "Any questions about the selected stations?";
  }
  return "Welcome to Orbital Transit";
};

export const getStartScreenPrompts = (selectedStationIds: string[]): StartScreenPrompt[] => {
  if (selectedStationIds.length > 1) {
    return [
      {
        label: "Tell me about these stations.",
        prompt: "Tell me about the stations I've selected",
        icon: "map-pin",
      },
      {
        label: "Give me an itinerary to visit these stations.",
        prompt: "What is an itinerary to visit the stations I've selected?",
        icon: "maps",
      },
    ];
  }
  return DEFAULT_START_SCREEN_PROMPTS;
};

export const getPlaceholder = (hasThread: boolean) => {
  return hasThread ? "I'd like to add a new station." : "Tell me about the Lyra Verge station.";
};

