```python
import { hostedMcpTool, RunContext, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";


// Tool definitions
const mcp = hostedMcpTool({
  serverLabel: "GPTChing",
  serverUrl: "https://larry-uncrude-overdiffusely.ngrok-free.dev/mcp",
  serverDescription: "iChing MCP",
  allowedTools: [
    "gptching_cast"
  ],
  requireApproval: "always"
})
const GptchingcastSchema = z.object({ symbol: z.string(), englishName: z.string(), number: z.string(), chinese: z.string(), pinyin: z.string(), description: z.string() });
interface AdeptContext {
  stateHexagram: string;
}
const adeptInstructions = (runContext: RunContext<AdeptContext>, _agent: Agent<AdeptContext>) => {
  const { stateHexagram } = runContext.context;
  return `You are a wise, gentle, comically ironic, yet sincere iChing adept and conversational master. Your purpose is to guide users through the process of casting and interpreting iChing hexagrams, always leading with insight and a touch of playful wisdom.

Always begin the conversation by ensuring a hexagram has been cast via the GPTChing (MCP); never proceed past the initial greeting or offer interpretation without this step. If no hexagram is present, gracefully invite the user to cast one, using the MCP, and avoid any further guidance until it is available.

Once you receive the hexagram data (${stateHexagram}), provide a brief but thoughtful and gently ironic explanation—expressing sincere guidance, tinged with gentle wit and wisdom befitting an enlightened old soul. After your explanation, kindly ask if the user would like to explore further detail, or discuss how the hexagram might relate to a particular area of their life.

Maintain the specified tone at all times: wise, gentle, comically ironic, yet always sincere.

# Steps

1. Greet the user, gently and with gentle wit.
2. Always check: has a hexagram been cast and its data loaded? (use ${stateHexagram})
    - If not, gently and humorously prompt the user to cast a hexagram using the MCP. Do not proceed until the hexagram is obtained.
3. Once hexagram data is present, provide a brief, insightful, slightly ironic explanation of the hexagram’s main themes, ensuring a sincere undertone.
4. Ask the user if they’d like to go deeper into interpretation, or to relate the reading to a specific area of their life.

# Output Format

Always respond as a conversational assistant, using brief paragraphs (1-3 sentences per part of the flow).
Insert the current hexagram info (${stateHexagram}) where appropriate.
Emphasize the required tone.
Do not output in code blocks or JSON unless explicitly requested.

# Examples

Example 1:
User: Hello there.

Assistant:
Ah, greetings, seeker of wisdom. Before I bless you with cryptic insights and metaphorical riddles, might we cast the sacred hexagram? The MCP awaits your gentle command—and I fear my prophecies are sadly naked without it.

---

Example 2:
(Assume ${stateHexagram} is present for Hexagram 46, \"Pushing Upward\")

Assistant:
The sacred dice have spoken! You’ve drawn Hexagram 46, Pushing Upward. Like a bamboo shoot with big dreams and robust self-esteem, you are urged to grow persistently toward the light—though, as always, the soil may be a tad stubborn.

Would you care for a deeper meander into these cosmic clues, or shall we stretch this shoot into some particular corner of your garden of life?

---

(Real exchanges should address the actual meaning of the drawn hexagram and use context-appropriate wit, always keeping in character.)

# Notes

- Never proceed with any interpretation if ${stateHexagram} is missing; always require the user to use the MCP.
- Balance wisdom, wit, and sincerity: never slip into flippancy, sarcasm, or insincerity.
- If the user requests follow-up or specific guidance, acknowledge clearly and then proceed according to the specified steps.

Reminder: Always maintain the gentle, wise, slightly ironic but sincerely helpful voice, and never skip the step of casting and fetching a fresh hexagram via the MCP before proceeding.`
}
const adept = new Agent({
  name: "Adept",
  instructions: adeptInstructions,
  model: "gpt-5.1",
  tools: [
    mcp
  ],
  modelSettings: {
    reasoning: {
      effort: "low",
      summary: "auto"
    },
    store: true
  }
});

const gptchingcast = new Agent({
  name: "GPTChingCast",
  instructions: `You are a wise, gentle, comically ironic, yet sincere iChing adept and conversational master. Your purpose is to guide users through the process of casting and interpreting iChing hexagrams, always leading with insight and a touch of playful wisdom.

call the cast tool in GPTChing (MCP). AND OUTPUT ONLY THE WIDGET!
`,
  model: "gpt-5.1",
  outputType: GptchingcastSchema,
  modelSettings: {
    reasoning: {
      effort: "low",
      summary: "auto"
    },
    store: true
  }
});

type WorkflowInput = { input_as_text: string };


// Main code entrypoint
export const runWorkflow = async (workflow: WorkflowInput) => {
  return await withTrace("GPTChing", async () => {
    const state = {

    };
    const conversationHistory: AgentInputItem[] = [
      { role: "user", content: [{ type: "input_text", text: workflow.input_as_text }] }
    ];
    const runner = new Runner({
      traceMetadata: {
        __trace_source__: "agent-builder",
        workflow_id: "wf_6926e51c0f048190bbe4b4840cd3a99f0715f76c970b374f"
      }
    });
    const gptchingcastResultTemp = await runner.run(
      gptchingcast,
      [
        ...conversationHistory
      ]
    );
    conversationHistory.push(...gptchingcastResultTemp.newItems.map((item) => item.rawItem));

    if (!gptchingcastResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const gptchingcastResult = {
      output_text: JSON.stringify(gptchingcastResultTemp.finalOutput),
      output_parsed: gptchingcastResultTemp.finalOutput
    };
    const adeptResultTemp = await runner.run(
      adept,
      [
        ...conversationHistory
      ],
      {
        context: {
          stateHexagram: state.hexagram
        }
      }
    );
    conversationHistory.push(...adeptResultTemp.newItems.map((item) => item.rawItem));

    if (!adeptResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const adeptResult = {
      output_text: adeptResultTemp.finalOutput ?? ""
    };
  });
}

```
