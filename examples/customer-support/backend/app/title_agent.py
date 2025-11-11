from agents import Agent
from chatkit.agents import AgentContext

title_agent = Agent[AgentContext](
    model="gpt-5-nano",
    name="Title generator",
    instructions="""
    Generate a title for a conversation between an airline customer support
    assistant and a user.
    The first user message in the conversation is included below.
    Do not just repeat the user message, use your own words.
    YOU MUST respond with 2-5 words without punctuation.
    """,
)
