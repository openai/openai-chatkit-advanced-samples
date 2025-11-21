"""Simple chat agent with reasoning capabilities."""

from agents import Agent, ModelSettings
from openai.types.shared.reasoning import Reasoning

simple_agent = Agent(
    name="SimpleChat",
    instructions="You are a helpful assistant.",
    model="gpt-4.1",
    model_settings=ModelSettings(
        store=True,
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
)
