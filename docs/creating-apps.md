# Creating Apps

This guide walks through creating a new ChatKit application using Claude Code.

## Overview

The workflow for creating apps:

1. **Design in Agent Builder** - Prototype your agent at [platform.openai.com](https://platform.openai.com/playground)
2. **Create a spec** - Define your app in a YAML file
3. **Run the command** - Use `/create-chatkit-app` with Claude Code
4. **Iterate** - Refine the implementation

## Step 1: Create a Specification

Create a YAML file in `specs/<app-name>/`:

```yaml
# specs/my-app/my-app.yaml

name: my-app
description: Brief description of what the app does

agent:
  workflow_id: wf_xxxxx  # From Agent Builder (optional)
  workflow_source: ./my-app-workflow.md  # Exported agent code

backend:
  tools: none  # Or list of tools needed
  state: in-memory  # Session state type

frontend:
  type: chat-only  # Or chat-with-panel, etc.
  features:
    - markdown rendering
    - conversation history
```

### Workflow Source File

Create a markdown file with your agent definition exported from Agent Builder:

```markdown
`specs/my-app/my-app-workflow.md`

This is the workflow code from Agent Builder.

\`\`\`python
from agents import Agent

my_agent = Agent(
  name="MyAgent",
  instructions="Your system prompt here.",
  model="gpt-4.1",
)
\`\`\`
```

## Step 2: Run the Command

In Claude Code, run:

```
/create-chatkit-app specs/my-app/my-app.yaml
```

Claude will:
1. Read your spec and workflow
2. Ask clarifying questions if needed
3. Present an implementation plan
4. Create the app in `apps/<app-name>/`

## Step 3: Configure and Run

1. **Add your API key** (if not already exported):
   ```bash
   echo "OPENAI_API_KEY=sk-your-key" > apps/my-app/backend/.env
   ```

2. **Add the run script** to root `package.json`:
   ```json
   "scripts": {
     "my-app": "npm --prefix apps/my-app install && npm --prefix apps/my-app start"
   }
   ```

3. **Run it**:
   ```bash
   npm run my-app
   ```

## App Structure

Every app follows this structure:

```
apps/my-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── server.py         # ChatKitServer implementation
│   │   ├── memory_store.py   # Thread/message storage
│   │   ├── thread_item_converter.py
│   │   └── agents/
│   │       └── my_agent.py   # Your agent definition
│   ├── scripts/
│   │   └── run-backend.sh
│   ├── pyproject.toml
│   └── .env                  # API key (git-ignored)
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   └── ChatKitPanel.tsx
│   │   ├── store/
│   │   │   └── useAppStore.ts
│   │   └── lib/
│   │       └── config.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
└── package.json              # Runs both with concurrently
```

## Adding Tools to Your Agent

To add tools, modify your agent file:

```python
# apps/my-app/backend/app/agents/my_agent.py

from agents import Agent, function_tool, RunContextWrapper
from ..server import MyAgentContext

@function_tool(description_override="Describe what this tool does")
async def my_tool(ctx: RunContextWrapper[MyAgentContext], param: str) -> dict:
    # Tool implementation
    return {"result": "value"}

my_agent = Agent(
    name="MyAgent",
    instructions="...",
    model="gpt-4.1",
    tools=[my_tool],
)
```

## Adding Widgets

For interactive UI elements, see the `cat-lounge` and `metro-map` examples which demonstrate:
- Building widgets with templates
- Streaming widgets to the client
- Handling widget actions

## Tips

- **Start simple** - Begin with a chat-only app, then add complexity
- **Copy from examples** - The examples are your best reference
- **Test incrementally** - Run after each significant change
- **Check logs** - Backend logs show agent execution details
