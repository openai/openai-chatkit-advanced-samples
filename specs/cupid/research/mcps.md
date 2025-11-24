Official OpenAI Documentation

The OpenAI Agents SDK has built-in MCP support through several integration methods:

1. Hosted MCP Tools - Connect to remote MCP servers:
   agent = Agent(
   name="Assistant",
   tools=[
   HostedMCPTool(
   tool_config={
   "type": "mcp",
   "server_label": "gitmcp",
   "server_url": "https://gitmcp.io/openai/codex",
   "require_approval": "never",
   }
   )
   ],
   )

2. Local MCP Servers - Run MCP servers as subprocesses using MCPServerStdio, which spawns the process and manages pipes automatically
3. HTTP/SSE Servers - Connect to servers using MCPServerStreamableHttp with custom headers and timeouts
4. Multiple MCP Servers - Specify multiple servers via the mcp_servers parameter on the Agent

Community Examples & Extensions

- openai-agents-mcp - A GitHub package specifically designed as an MCP extension for the OpenAI Agents SDK
- Composio's MCP Integration - Examples of building agents with GitHub, Google Workspace, and other integrations
- Agent Builder UI - OpenAI's visual builder supports MCP by clicking "MCP" in the sidebar and adding server URLs

Practical Use Cases

- Tinybird MCP for real-time data-driven agents
- GitHub MCP for automation workflows
- Google Suite MCP for Sheets, Calendar, Docs integration
- Rube MCP for access to 500+ apps

Sources:

- https://openai.github.io/openai-agents-python/mcp/
- https://github.com/lastmile-ai/openai-agents-mcp
- https://composio.dev/blog/building-mcp-agents-with-openai-agents-sdk
- https://composio.dev/blog/openai-agent-builder-step-by-step-guide-to-building-ai-agents-with-mcp
- https://apidog.com/blog/mcp-servers-openai-agents/
