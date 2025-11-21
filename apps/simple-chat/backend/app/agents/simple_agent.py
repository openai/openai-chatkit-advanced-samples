"""Simple chat agent."""

from agents import Agent

simple_agent = Agent(
    name="SimpleChat",
    instructions="You are a helpful assistant.",
    model="gpt-4.1",
)
