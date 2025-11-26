# News Guide Example

## Overview

News Guide is an editorial assistant that helps readers discover, search, and explore news articles. It demonstrates a content-driven ChatKit application where an intelligent agent reasons about an article library, makes recommendations, and delegates specialized tasks to other agents.

## Frontend Architecture

### Traditional Layout (No Specialized Visualization)

Unlike metro-map which uses Reactflow, News Guide uses a straightforward React-based layout with state-driven views.

**NewsroomPanel Component** (`NewsroomPanel.tsx`): A three-state UI system

#### 1. Landing Grid View (Default)
- **Featured article** (top): Large card with hero image, title, author, date
- **Secondary articles** (grid): 3 smaller cards below
- **Last updated** timestamp
- Fetches article metadata via `fetchArticles()`
- Responsive: single column on mobile, flexible layout on desktop

#### 2. Article Detail View
- **Full article content**: Rendered with custom Markdown styling
- **Back button** (top left): Semi-transparent pill to return to landing
- **Hero image**, title, author, date, tags
- **Markdown rendering** with custom components for headings, lists, quotes, images
- Fetches full article content via `fetchArticle(articleId)`

#### 3. Navigation
- **React Router**: URL-based article routing (`/article/{articleId}`)
- `useNavigate()` handles transitions between landing and detail views
- Article ID comes from URL params

### State Management

Uses Zustand store (`useAppStore`) to:
- Track currently selected article ID
- Manage ChatKit instance

Articles are fetched client-side:
- `fetchArticles()`: GET `/articles` → list of metadata
- `fetchArticle(id)`: GET `/articles/{id}` → full article content

### Key Libraries

- **React Markdown**: Renders article content with custom styling
- **Remark GFM**: GitHub-Flavored Markdown support
- **React Router**: URL-based navigation
- **Lucide React**: Icons
- **Zustand**: State management
- **Tailwind CSS**: Styling

## Backend Architecture

### Multi-Agent System

Four specialized agents working together:

#### 1. News Agent (Main)
**Purpose**: Editorial assistant for article discovery and recommendations

**Key Instructions**:
- Search articles by keywords, tags, or exact text phrases
- Fetch current article content when user asks about "this page"
- Provide concise summaries (2-4 sentences, don't mention the word "summary")
- Recommend 2 articles by default unless user asks for more
- Delegate to specialized agents for events, puzzles, and other tasks
- Cite article titles (italicized) and use blockquotes for direct excerpts

**Tools Available**:
- `list_available_tags_and_keywords`: Get all searchable tags
- `get_current_page`: Fetch full article currently viewed by user
- `search_articles_by_keywords`: Search article metadata (title, subtitle, tags)
- `search_articles_by_tags`: Filter articles by section/category
- `search_articles_by_exact_text`: Quote matching within article content
- `get_article_by_id`: Fetch specific article by ID
- `search_articles_by_author`: Find all articles by an author
- `show_article_list_widget`: Display clickable list of articles
- `delegate_to_event_finder`: Hand off event queries to Event Finder Agent
- `delegate_to_puzzle_keeper`: Hand off puzzle requests to Puzzle Agent

#### 2. Event Finder Agent
**Purpose**: Handles queries about "events," "happenings," "things to do"

Delegated from News Agent when user asks about local events.

#### 3. Puzzle Agent
**Purpose**: Provides puzzles, brain teasers, crosswords

Includes "Two Truths and a Lie" puzzle format.

#### 4. Title Agent
**Purpose**: Generates thread titles

Creates readable titles for chat threads based on conversation.

### Data Layer

#### ArticleStore
- In-memory store of all articles
- Loads from `backend/app/data/articles.json`
- Each article has: `id`, `title`, `subtitle`, `author`, `date`, `tags`, `keywords`, `heroImage`, `content` (markdown)

#### EventStore
- Stores events/happenings data
- Loaded from `backend/app/data/events.json`

#### MemoryStore
- Thread persistence for chat history
- Stores messages between user and agent

#### RequestContext
- Per-request context passed to agents
- Contains user info, stores, and other request-scoped data

### Server Implementation

`server.py` extends `ChatKitServer[RequestContext]`:

**respond()**:
- Loads thread history
- Converts thread items to agent input format
- Selects appropriate agent (uses News Agent by default)
- Streams agent response back to client

**action()**:
- Handles widget interactions
- `open_article` action: Navigates to article in frontend
- `view_event_details` action: Shows event details

**Thread Title Generation**:
- Runs asynchronously using Title Agent
- Updates thread metadata with AI-generated title

### Widget System

#### ArticleListWidget
- Displays clickable list of articles
- When user clicks an article, it sends `open_article` action
- Frontend receives action and navigates to `/article/{articleId}`

#### EventListWidget
- Similar to article widget but for events
- Shows events with times, locations, descriptions

## Agent-Frontend Interaction

**Frontend → Agent** (user sends messages):

```
User: "Tell me about climate change"
  → ChatKit sends message to backend
  → News Agent calls search_articles_by_keywords("climate change")
  → Agent calls show_article_list_widget(results)
  → Widget displays recommended articles

---

User: "What's this about?" (while viewing an article)
  → ChatKit sends message
  → News Agent calls get_current_page()
  → Agent fetches full article content
  → Agent summarizes and responds with details
```

**Agent → Frontend** (widget interactions):

```
User clicks article in ArticleListWidget
  → Frontend receives "open_article" action
  → Calls navigate("/article/{id}")
  → NewsroomPanel loads article via fetchArticle()
  → Article Detail view renders
```

## Data Flow

```
User lands on news-guide
        ↓
NewsroomPanel loads fetchArticles()
        ↓
Landing grid displays featured + 3 secondary
        ↓
User clicks article
        ↓
URL changes to /article/{id}
        ↓
fetchArticle(id) loads full content
        ↓
Article Detail view renders with Markdown
        ↓
User asks question in chat
        ↓
ChatKit → News Agent (with get_current_page context)
        ↓
Agent analyzes article and responds
        ↓
Agent may call show_article_list_widget
        ↓
Widget displays recommended articles
        ↓
User clicks recommendation
        ↓
open_article action triggers navigation
        ↓
New article loads in detail view
```

## Custom Markdown Rendering

The `markdownComponents` object defines styling for article content:

- `h1`, `h2`: Sized headings with margin and dark mode support
- `p`: Leading-relaxed paragraphs
- `ul`, `ol`: Styled lists with custom bullets/numbers
- `blockquote`: Indented quotes (if GFM provides)
- `img`: Full-width images with borders
- `strong`, `em`: Bold and italic styling

This allows articles to be displayed with consistent typography.

## Files Structure

```
examples/news-guide/
├── frontend/
│   └── src/components/
│       ├── NewsroomPanel.tsx      # Landing grid + article detail view
│       ├── ChatKitPanel.tsx       # Chat interface
│       └── ThemeToggle.tsx        # Dark mode toggle
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── server.py             # ChatKitServer implementation
│   │   ├── agents/
│   │   │   ├── news_agent.py      # Main editorial assistant
│   │   │   ├── event_finder_agent.py
│   │   │   ├── puzzle_agent.py
│   │   │   └── title_agent.py
│   │   ├── data/
│   │   │   ├── article_store.py   # Article storage
│   │   │   ├── event_store.py     # Event storage
│   │   │   └── articles.json      # Article content
│   │   └── widgets/
│   │       ├── article_list_widget.py
│   │       ├── event_list_widget.py
│   │       └── preview_widgets.py
│   └── pyproject.toml
└── package.json
```

## How to Run

```bash
export OPENAI_API_KEY=sk-...
npm run news-guide
# Frontend: http://localhost:5172
# Backend: http://127.0.0.1:8002
```

## Key Differences from Metro Map

| Aspect | Metro Map | News Guide |
|--------|-----------|-----------|
| **Visualization** | Reactflow (graph/diagram) | Traditional layout (landing + detail) |
| **Agents** | Single agent (metro expert) | Multi-agent (news, events, puzzles) |
| **Interaction** | Interactive map manipulation | Content search and exploration |
| **Delegation** | Direct map updates | Widget-based article recommendations |
| **State** | Map structure (stations/lines) | Article library metadata |
| **User Flow** | Click station → chat about it | Search articles → read → chat about content |
