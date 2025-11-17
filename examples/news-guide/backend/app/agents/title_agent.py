from agents import Agent
from chatkit.agents import AgentContext

title_agent = Agent[AgentContext](
    model="gpt-5-nano",
    name="Title generator",
    instructions="""
    Generate a short conversation title for a news editorial assistant
    chatting with a user. The first user message in the thread is
    included below to provide context. Use your own words, respond with
    2-5 words, and avoid punctuation.
    """,
)
