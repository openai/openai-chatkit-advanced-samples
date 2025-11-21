# ChatKit Development Environment

This repository is a development environment for building OpenAI-powered chat applications using **ChatKit**, **AgentKit**, and the **OpenAI Agents SDK**.

## What's Inside

- **`examples/`** - Battle-tested reference implementations from OpenAI (cat-lounge, customer-support, metro-map, news-guide). These are read-only templates.
- **`apps/`** - Your custom applications built using the patterns from examples.
- **`specs/`** - YAML specifications and plans for apps being developed.
- **`docs/`** - Documentation for using this development environment.

## Quick Links

- [Getting Started](./getting-started.md) - Prerequisites and first run
- [Creating Apps](./creating-apps.md) - How to build new ChatKit applications
- [Architecture](./architecture.md) - Understanding the backend/frontend patterns

## Philosophy

1. **Examples are templates** - Don't modify them; copy patterns into `apps/`
2. **Apps are portable** - Each app in `apps/` is self-contained and can be extracted
3. **Specs drive development** - Define your app in YAML with supporting workflow, instructions, and other specifications before building
4. **Claude Code assists** - Use `/create-chatkit-app` to scaffold new applications

## Repository Structure

```
chatkit-dev/
├── apps/                    # Your custom applications
│   └── simple-chat/         # Example: minimal chat app
├── examples/                # OpenAI reference implementations (read-only)
│   ├── cat-lounge/
│   ├── customer-support/
│   ├── metro-map/
│   └── news-guide/
├── specs/                   # App specifications and plans
│   └── simple-chat/
│       ├── simple-chat.yaml
│       └── simple-chat-plan.md
├── docs/                    # Documentation
├── .claude/                 # Claude Code commands
│   └── commands/
│       └── create-chatkit-app.md
├── package.json             # Root scripts to run apps
└── CLAUDE.md                # Instructions for Claude Code
```
