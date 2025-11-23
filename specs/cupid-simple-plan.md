# Cupid-Simple Implementation Plan

## Project Overview
Cupid-Simple is a romantic matchmaking game built with OpenAI's ChatKit and Agent SDK. The application presents character profiles via interactive widgets and guides users through an astrologically-themed narrative matchmaking experience.

## Architecture

### Backend (Python/FastAPI)
```
apps/cupid-simple/backend/
├── app/
│   ├── main.py                    # FastAPI entrypoint with /chatkit endpoint
│   ├── server.py                  # CupidServer - chapter-based orchestration
│   ├── memory_store.py            # Thread/message persistence (in-memory)
│   ├── thread_item_converter.py   # Convert thread items to agent format
│   ├── request_context.py         # Chapter tracking & character data context
│   ├── agents/
│   │   ├── cupid_agent.py         # Main game agent (1847-line instructions)
│   │   └── profilecard_agent.py   # Widget generator with structured output
│   └── data/
│       ├── mortal.yaml            # Zara Patel character data
│       ├── match.yaml             # Sam Martinez character data
│       └── instructions.md        # Full game instructions (cupid-simple-instructions.md)
├── scripts/run-backend.sh
└── pyproject.toml                 # Dependencies: FastAPI, ChatKit, PyYAML
```

### Frontend (React/TypeScript/Vite)
```
apps/cupid-simple/frontend/
├── src/
│   ├── App.tsx                    # Main app with CUPID branding
│   ├── main.tsx
│   ├── components/
│   │   ├── ChatKitPanel.tsx       # ChatKit SDK integration
│   │   └── ThemeToggle.tsx
│   ├── lib/
│   │   └── config.ts              # Greeting: "Cupid v0.1", Prompt: "Play"
│   └── store/
│       └── useAppStore.ts         # Zustand state management
└── vite.config.ts
```

## Implementation Details

### 1. Chapter-Based Conversation Flow

**CupidServer** (`server.py`) implements stateful chapter progression:

- **Chapter 1**:
  - Run `cupid_agent` to introduce Zara (mortal character)
  - Run `profilecard_agent` with mortal.yaml data
  - Stream ProfileCard widget to frontend
  - Increment to Chapter 2

- **Chapter 2**:
  - Run `cupid_agent` to introduce Sam (match character)
  - Run `profilecard_agent` with match.yaml data
  - Stream ProfileCard widget to frontend
  - Increment to Chapter 3

- **Chapter 3+**:
  - Normal conversation with `cupid_agent`
  - Agent follows 1847-line game instructions for story scenes
  - Handles user decisions, provides astrological insights
  - Guides through Meet-Cute → Date → Evaluation flow

### 2. Agent Implementations

#### Cupid Agent (`cupid_agent.py`)
- **Model**: `gpt-4.1`
- **Instructions**: Loaded from `data/instructions.md` (1847 lines)
- **Behavior**:
  - Literary interactive fiction with astrology as "physics"
  - Story structure: THE MATCH → Scene 1 → Scene 2 → Scene 3 → THE DATE ENDS → Evaluation
  - Prose style: "Upper West Side intellectual" with New Yorker humor
  - Sacred pacing rules: 2-3 paragraphs, 8-12 dialogue exchanges, approval gates
  - Target length: 2500-3000 words (15-25 minutes)

#### ProfileCard Agent (`profilecard_agent.py`)
- **Model**: `gpt-4o`
- **Output Type**: `ProfileCardOutput` (structured Pydantic model)
- **Schema**: 8 required fields matching ProfileCard00.widget JSON schema
  - name, age, occupation, location, birthdate
  - origin (city, state, country)
  - astrological_notes (sun_sign, moon_sign, venus_sign, mars_sign)
  - short_bio

### 3. Widget System

**ProfileCard Widget** (`specs/cupid-simple/widgets/ProfileCard00.widget`):
- Renders character profile with avatar, bio, location, birthdate
- Displays four astrological badges (Sun, Moon, Venus, Mars)
- MATCH button with `onClickAction` sending "yes" to server
- Button interaction advances conversation (agent handles flow)

### 4. Data Loading

**Character Data** (YAML format):
- `mortal.yaml`: Zara Patel - 28, Personal Trainer, Aries Sun/Virgo Moon/Taurus Venus/Aries Mars
- `match.yaml`: Sam Martinez - 31, Architect, Gemini Sun/Aquarius Moon/Gemini Venus/Taurus Mars
- Both files include: personality traits, interests, dating history, relationship style, astrological notes

**Server Initialization**:
- Load both YAML files on startup
- Make data available via `RequestContext`
- Pass to agent context for ProfileCard generation

### 5. Frontend Customization

**Greeting**: "Cupid v0.1"

**Starter Prompt**: Single "Play" button with play icon

**Header**: "CUPID" title with subtitle "Divine matchmaking powered by the stars"

**Theme**: Gradient background (slate colors), theme toggle, rounded chat panel

## Key Technical Decisions

1. **Separate ProfileCard Agent**: Dedicated agent for widget generation (not inline)
2. **MATCH Button Flow**: Sends "yes" message, agent instructions handle progression
3. **Natural Conversation**: Starter prompts use natural language, agent determines response
4. **Chapter State**: Tracked in `RequestContext`, persists across conversation turns
5. **In-Memory Storage**: No database - suitable for demo/prototype
6. **Flat File Data**: YAML files for character data (plan to evolve later)
7. **Simple-Chat Pattern**: Follows proven architecture from examples/simple-chat

## Running the Application

```bash
# From repo root
export OPENAI_API_KEY=sk-...
npm run cupid-simple

# Frontend: http://localhost:5173 (or next available port)
# Backend: http://127.0.0.1:8000
```

## Success Criteria

- ✅ App runs via `npm run cupid-simple`
- ✅ ProfileCard widgets render with all 8 fields (name, age, etc.)
- ✅ Chapter progression: mortal profile → match profile → game scenes
- ✅ Agent follows 1847-line instructions for story flow
- ✅ MATCH button interactions work correctly
- ✅ Conversation history persists within thread
- ✅ Frontend matches visual style and branding

## Future Enhancements

- Replace flat files with database/state management
- Add more robust error handling
- Implement conversation history export
- Add analytics/telemetry for game completion
- Support multiple mortal/match pairs
- Add save/resume game state across sessions
- Implement compatibility scoring system
- Add more interactive widgets (compatibility chart, decision tree)
