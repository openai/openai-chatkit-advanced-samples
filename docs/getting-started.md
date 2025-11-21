# Getting Started

## Prerequisites

Before you begin, ensure you have:

- **Node.js** >= 18.18 and **npm** >= 9
- **Python** >= 3.11
- **uv** - Fast Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **OpenAI API Key** - Get one at [platform.openai.com](https://platform.openai.com/api-keys)

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd chatkit-dev
   ```

2. **Set your OpenAI API key**

   Option A: Export in your shell (recommended for development)
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

   Option B: Create a `.env` file in the app's backend directory
   ```bash
   # apps/simple-chat/backend/.env
   OPENAI_API_KEY=sk-your-key-here
   ```

## Running an Example

The examples are pre-built reference implementations:

```bash
# Run the cat lounge example
npm run cat-lounge

# Run the news guide example
npm run news-guide

# Other examples
npm run metro-map
npm run customer-support
```

Each example runs both frontend and backend concurrently. Check the console for URLs (typically `http://localhost:517X`).

## Running Your Apps

Apps you create go in the `apps/` directory:

```bash
# Run the simple-chat app
npm run simple-chat
```

## Stopping an App

Press `Ctrl+C` in the terminal to stop both frontend and backend.

## Common Issues

### "OPENAI_API_KEY is not set"

Make sure you've exported your API key in the same terminal session:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

Or add it to the app's `backend/.env` file.

### "Port XXXX is in use"

Another process is using the port. Either:
- Stop the other process: `lsof -i :PORT` then `kill PID`
- Vite will automatically try the next available port

### Python/uv errors

Ensure uv is installed and in your PATH:
```bash
which uv  # Should show the path
uv --version  # Should show version
```

## Next Steps

- [Creating Apps](./creating-apps.md) - Build your own ChatKit application
- [Architecture](./architecture.md) - Understand the patterns used
