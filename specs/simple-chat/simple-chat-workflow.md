This is the workflow code output from Agent Builder.

> **Note:** The original workflow used `gpt-5.1` with reasoning parameters, but these are not
> supported in the current API. The implementation uses `gpt-4.1` without reasoning settings.

```python
from agents import Agent

simplechat = Agent(
  name="SimpleChat",
  instructions="You are a helpful assistant.",
  model="gpt-4.1",
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("SimpleChat"):
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    simplechat_result_temp = await Runner.run(
      simplechat,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_69206528d6788190917f6d44fee9fa1b0ea4b76302f3c578"
      })
    )

    conversation_history.extend([item.to_input_item() for item in simplechat_result_temp.new_items])

    simplechat_result = {
      "output_text": simplechat_result_temp.final_output_as(str)
    }
```
