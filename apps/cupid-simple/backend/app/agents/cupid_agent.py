"""Cupid game agent - guides the romantic matchmaking game."""

from pathlib import Path

from agents import Agent

# Load game instructions from external file
INSTRUCTIONS_PATH = Path(__file__).parent.parent / "data" / "instructions.md"
with open(INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
    INSTRUCTIONS = f.read()

cupid_agent = Agent(
    name="Cupid",
    instructions=INSTRUCTIONS,
    model="gpt-5.1",
)
