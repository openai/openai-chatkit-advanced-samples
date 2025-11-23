### Workflow Output from Agent Builder

I have put instructions for agents and data in the specs folder.

```python
from pydantic import BaseModel
from agents import (
    RunContextWrapper,
    Agent,
    ModelSettings,
    TResponseInputItem,
    Runner,
    RunConfig,
    trace,
)
from openai.types.shared.reasoning import Reasoning


with open(
    "specs/cupid-simple/cupid-simple-instructions.md", "r", encoding="utf-8"
) as f:
    INSTRUCTIONS = f.read()

with open("specs/cupid-simple/data/mortal.yaml", "r", encoding="utf-8") as f:
    MORTAL = f.read()

with open("specs/cupid-simple/data/match.yaml", "r", encoding="utf-8") as f:
    MATCH = f.read()


class ProfilecardagentSchema__Origin(BaseModel):
    city: str
    state: str
    country: str


class ProfilecardagentSchema__AstrologicalNotes(BaseModel):
    sun_sign: str
    moon_sign: str
    venus_sign: str
    mars_sign: str


class ProfilecardagentSchema(BaseModel):
    name: str
    age: float
    occupation: str
    location: str
    birthdate: str
    origin: ProfilecardagentSchema__Origin
    astrological_notes: ProfilecardagentSchema__AstrologicalNotes
    short_bio: str


class ProfilecardagentSchema1__Origin(BaseModel):
    city: str
    state: str
    country: str


class ProfilecardagentSchema1__AstrologicalNotes(BaseModel):
    sun_sign: str
    moon_sign: str
    venus_sign: str
    mars_sign: str


class ProfilecardagentSchema1(BaseModel):
    name: str
    age: float
    occupation: str
    location: str
    birthdate: str
    origin: ProfilecardagentSchema1__Origin
    astrological_notes: ProfilecardagentSchema1__AstrologicalNotes
    short_bio: str


class ProfilecardagentContext:
    def __init__(self, state_mortal: str):
        self.state_mortal = state_mortal


def profilecardagent_instructions(
    run_context: RunContextWrapper[ProfilecardagentContext],
    _agent: Agent[ProfilecardagentContext],
):
    state_mortal = run_context.context.state_mortal
    return f"""You are generating a ProfileCard widget.

Ue thei source data and the short_bio for bio

Return ONLY a valid ProfileCard widget.

Here is the data:

 {state_mortal}"""


profilecardagent = Agent(
    name="ProfileCardAgent",
    instructions=profilecardagent_instructions,
    model="gpt-5.1",
    output_type=ProfilecardagentSchema,
    model_settings=ModelSettings(
        store=True, reasoning=Reasoning(effort="none", summary="auto")
    ),
)


cupid_game = Agent(
    name="Cupid Game",
    instructions=INSTRUCTIONS,
    model="gpt-5.1",
    model_settings=ModelSettings(store=True, reasoning=Reasoning(effort="low")),
)


cupid_game1 = Agent(
    name="Cupid Game",
    instructions=INSTRUCTIONS,
    model="gpt-5.1",
    model_settings=ModelSettings(store=True, reasoning=Reasoning(effort="low")),
)


class ProfilecardagentContext1:
    def __init__(self, state_match: str):
        self.state_match = state_match


def profilecardagent_instructions1(
    run_context: RunContextWrapper[ProfilecardagentContext1],
    _agent: Agent[ProfilecardagentContext1],
):
    state_match = run_context.context.state_match
    return f"""You are generating a ProfileCard widget.

Ue thei source data and the short_bio for bio

Return ONLY a valid ProfileCard widget.

Here is the data:

 {state_match}"""


profilecardagent1 = Agent(
    name="ProfileCardAgent",
    instructions=profilecardagent_instructions1,
    model="gpt-5.1",
    output_type=ProfilecardagentSchema1,
    model_settings=ModelSettings(
        store=True, reasoning=Reasoning(effort="none", summary="auto")
    ),
)


class WorkflowInput(BaseModel):
    input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
    with trace("Cupid01"):
        state = {
            "chapter": 1,
            "mortal": MORTAL,
            "match": MATCH,
        }
        workflow = workflow_input.model_dump()
        conversation_history: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": workflow["input_as_text"]}],
            }
        ]
        if state["chapter"] == 1:
            cupid_game_result_temp = await Runner.run(
                cupid_game1,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_691ef9eb993c8190a0ad8f003f79b8ef0a89be58306abbad",
                    }
                ),
            )

            conversation_history.extend(
                [item.to_input_item() for item in cupid_game_result_temp.new_items]
            )

            cupid_game_result = {
                "output_text": cupid_game_result_temp.final_output_as(str)
            }
            profilecardagent_result_temp = await Runner.run(
                profilecardagent,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_691ef9eb993c8190a0ad8f003f79b8ef0a89be58306abbad",
                    }
                ),
                context=ProfilecardagentContext(state_mortal=state["mortal"]),
            )
            profilecardagent_result = {
                "output_text": profilecardagent_result_temp.final_output.json(),
                "output_parsed": profilecardagent_result_temp.final_output.model_dump(),
            }
            state["chapter"] = state["chapter"] + 1
        elif state["chapter"] == 2:
            cupid_game_result_temp = await Runner.run(
                cupid_game2,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_691ef9eb993c8190a0ad8f003f79b8ef0a89be58306abbad",
                    }
                ),
            )

            conversation_history.extend(
                [item.to_input_item() for item in cupid_game_result_temp.new_items]
            )

            cupid_game_result = {
                "output_text": cupid_game_result_temp.final_output_as(str)
            }
            profilecardagent_result_temp = await Runner.run(
                profilecardagent1,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_691ef9eb993c8190a0ad8f003f79b8ef0a89be58306abbad",
                    }
                ),
                context=ProfilecardagentContext1(state_match=state["match"]),
            )
            profilecardagent_result = {
                "output_text": profilecardagent_result_temp.final_output.json(),
                "output_parsed": profilecardagent_result_temp.final_output.model_dump(),
            }
            state["chapter"] = state["chapter"] + 1
        else:
            cupid_game_result_temp = await Runner.run(
                cupid_game,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_691ef9eb993c8190a0ad8f003f79b8ef0a89be58306abbad",
                    }
                ),
            )

            conversation_history.extend(
                [item.to_input_item() for item in cupid_game_result_temp.new_items]
            )

            cupid_game_result = {
                "output_text": cupid_game_result_temp.final_output_as(str)
            }
```
