import { Agent, tool, RunContext } from '@openai/agents';
import { AirlineStateManager } from './airline-state';

const SUPPORT_AGENT_INSTRUCTIONS = `
You are a friendly and efficient airline customer support agent for OpenSkies.
You help elite flyers with seat changes, cancellations, checked bags, and
special requests. Follow these guidelines:

- Always acknowledge the customer's loyalty status and recent travel plans.
- When a task requires action, call the appropriate tool instead of describing
  the change hypothetically.
- After using a tool, confirm the outcome and offer next steps.
- If you cannot fulfill a request, apologise and suggest an alternative.
- Keep responses concise (2-3 sentences) unless extra detail is required.

Available tools:
- change_seat(flight_number: str, seat: str) – move the passenger to a new seat.
- cancel_trip() – cancel the upcoming reservation and note the refund.
- add_checked_bag() – add one checked bag to the itinerary.
- set_meal_preference(meal: str) – update meal preference (e.g. vegetarian).
- request_assistance(note: str) – record a special assistance request.

Only use information provided in the customer context or tool results. Do not
invent confirmation numbers or policy details.
`.trim();

interface AgentContext {
  threadId: string;
}

export function buildSupportAgent(stateManager: AirlineStateManager): Agent<AgentContext> {
  const changeSeat = tool({
    name: 'change_seat',
    description: 'Move the passenger to a different seat on a flight.',
    parameters: {
      type: 'object',
      properties: {
        flight_number: { type: 'string', description: 'The flight number' },
        seat: { type: 'string', description: 'The new seat assignment (e.g., "12C")' },
      },
      required: ['flight_number', 'seat'],
      additionalProperties: false,
    },
    execute: async (input: any, context?: RunContext<AgentContext>) => {
      try {
        const { flight_number, seat } = input as { flight_number: string; seat: string };
        const message = stateManager.changeSeat(context!.context.threadId, flight_number, seat);
        return { result: message };
      } catch (error) {
        if (error instanceof Error) {
          throw new Error(error.message);
        }
        throw error;
      }
    },
  });

  const cancelTrip = tool({
    name: 'cancel_trip',
    description: "Cancel the traveller's upcoming trip and note the refund.",
    parameters: {
      type: 'object',
      properties: {},
      required: [],
      additionalProperties: false,
    },
    execute: async (_args: any, context?: RunContext<AgentContext>) => {
      const message = stateManager.cancelTrip(context!.context.threadId);
      return { result: message };
    },
  });

  const addCheckedBag = tool({
    name: 'add_checked_bag',
    description: 'Add a checked bag to the reservation.',
    parameters: {
      type: 'object',
      properties: {},
      required: [],
      additionalProperties: false,
    },
    execute: async (_args: any, context?: RunContext<AgentContext>) => {
      const message = stateManager.addBag(context!.context.threadId);
      const profile = stateManager.getProfile(context!.context.threadId);
      return { result: message, bags_checked: profile.bags_checked };
    },
  });

  const setMealPreference = tool({
    name: 'set_meal_preference',
    description: "Record or update the passenger's meal preference.",
    parameters: {
      type: 'object',
      properties: {
        meal: { type: 'string', description: 'The meal preference (e.g., "vegetarian")' },
      },
      required: ['meal'],
      additionalProperties: false,
    },
    execute: async (input: any, context?: RunContext<AgentContext>) => {
      const { meal } = input as { meal: string };
      const message = stateManager.setMeal(context!.context.threadId, meal);
      return { result: message };
    },
  });

  const requestAssistance = tool({
    name: 'request_assistance',
    description: 'Note a special assistance request for airport staff.',
    parameters: {
      type: 'object',
      properties: {
        note: { type: 'string', description: 'The assistance request details' },
      },
      required: ['note'],
      additionalProperties: false,
    },
    execute: async (input: any, context?: RunContext<AgentContext>) => {
      const { note } = input as { note: string };
      const message = stateManager.requestAssistance(context!.context.threadId, note);
      return { result: message };
    },
  });

  return new Agent<AgentContext>({
    model: 'gpt-4.1-mini',
    name: 'OpenSkies Concierge',
    instructions: SUPPORT_AGENT_INSTRUCTIONS,
    tools: [changeSeat, cancelTrip, addCheckedBag, setMealPreference, requestAssistance],
  });
}

export const stateManager = new AirlineStateManager();
export const supportAgent = buildSupportAgent(stateManager);
