# ChatKit Chat Component Structure & Customization Guide

## Overview

This guide explains how ChatKit's chat component works and how to customize it with your own styling and functionality. Based on analysis of all four ChatKit examples (news-guide, cat-lounge, customer-support, metro-map).

## Table of Contents

1. [Core Integration Pattern](#1-chatkit-component-integration)
2. [Theme Customization](#2-theme-customization)
3. [Start Screen Configuration](#3-start-screen-configuration)
4. [Composer (Input Area)](#4-composer-input-area-configuration)
5. [Header Customization](#5-header-customization)
6. [Widget Rendering](#6-widget-rendering)
7. [Layout Structure](#7-layout-structure)
8. [State Management](#8-state-management-zustand-pattern)
9. [Global CSS Setup](#9-global-css-setup)
10. [HTML vs React Comparison](#10-key-differences-your-html-vs-chatkit-react)
11. [Per-Agent Theming](#11-per-agent-accent-colors)
12. [What You Can & Cannot Customize](#12-customization-capabilities)

---

## 1. ChatKit Component Integration

### Core Pattern
ChatKit uses a React hook (`useChatKit`) that provides a `control` object which you pass to the `<ChatKit>` component:

```typescript
// ChatKitPanel.tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

export function ChatKitPanel({ onChatKitReady, className }: ChatKitPanelProps) {
  const chatkit = useChatKit({
    api: { url, domainKey, fetch },
    theme: { /* customization */ },
    startScreen: { /* welcome screen */ },
    composer: { /* input area */ },
    // ... more config
  });

  return (
    <div className={clsx("relative h-full w-full overflow-hidden", className)}>
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
```

**Key Point**: The `<ChatKit>` component is a complete, self-contained chat interface. You **cannot** directly customize its internal HTML structure, but you can:
1. Style it via theme configuration
2. Control its container sizing/positioning
3. Add custom header actions
4. Handle widget rendering and interactions

---

## 2. Theme Customization

ChatKit's theme system allows you to customize colors, typography, spacing, and more through the `useChatKit` configuration.

### Available Theme Options

```typescript
theme: {
  // Density: Controls spacing throughout the component
  density: "spacious",  // Options: "spacious" | "compact"

  // Color scheme: Sync with your app's light/dark mode
  colorScheme: scheme,  // "light" | "dark"

  // Color customization
  color: {
    // Grayscale: Controls neutral colors throughout
    grayscale: {
      hue: 40,        // 0-360 degrees (40 = warm tan/cream, 220 = cool blue)
      tint: 4,        // Light background tint levels
      shade: scheme === "dark" ? -2 : -4,  // Dark text shade levels
    },

    // Accent: Primary brand color for interactive elements
    accent: {
      primary: "#9B85B7",  // Hex color for buttons, links, etc.
      level: 1,            // Intensity level
    },

    // Surface: Optional explicit background colors (overrides grayscale)
    surface: {
      background: scheme === "dark" ? "#1a1a1a" : "#FDF6E3",
      foreground: scheme === "dark" ? "#2d2d2d" : "#F5EFE0",
    }
  },

  // Typography: Custom fonts
  typography: {
    fontFamily: "Lexend, sans-serif",
    fontSources: [
      {
        family: "Lexend",
        src: "url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500&display=swap')",
      },
      {
        family: "Lexend Giga",
        src: "url('https://fonts.googleapis.com/css2?family=Lexend+Giga:wght@400;600;900&display=swap')",
      }
    ],
  },

  // Border radius: Affects roundness of UI elements
  radius: "round",  // Options: "sharp" (4px) | "round" (12px) | "pill" (9999px)
}
```

### Theme Properties Explained

**`density`**
- `"spacious"`: More padding, larger touch targets (default in most examples)
- `"compact"`: Tighter spacing, smaller elements

**`colorScheme`**
- Should sync with your app's theme state
- Typically stored in Zustand/context and localStorage

**`color.grayscale.hue`**
- Controls the color temperature of neutral UI elements
- `0-60`: Warm (browns, tans, creams)
- `180-240`: Cool (blues, grays)
- Examples: News Guide uses warm tones (40), Metro Map uses cool blues (220)

**`color.accent.primary`**
- Used for buttons, links, focused inputs, active states
- Should match your brand color

**`color.surface`**
- Optional: Explicitly set background colors
- If omitted, ChatKit generates from `grayscale.hue`

**`typography.fontSources`**
- Array of font definitions
- Supports Google Fonts URLs or local font files

**`radius`**
- `"sharp"`: Minimal rounding (~4px), modern/technical feel
- `"round"`: Moderate rounding (~12px), friendly/approachable
- `"pill"`: Maximum rounding (9999px), playful/casual

---

## 3. Start Screen Configuration

The welcome screen that appears before conversation starts:

```typescript
startScreen: {
  greeting: "Welcome to GPTChing",
  prompts: [
    {
      label: "Cast a hexagram",
      prompt: "Cast a hexagram for me",
      icon: "sparkles",  // Built-in ChatKit icon
    },
    {
      label: "Ask about love",
      prompt: "What does the I Ching say about love?",
      icon: "heart",
    },
    {
      label: "Seek wisdom",
      prompt: "I need guidance on a difficult decision",
      icon: "lightbulb",
    },
  ]
}
```

---

## 4. Composer (Input Area) Configuration

```typescript
composer: {
  placeholder: "Ask for deeper guidance...",
  tools: [
    // Optional: Add tool buttons to composer
    {
      id: "cast_hexagram",
      label: "Cast Hexagram",
      icon: "wand",
      persistent: true,  // Keep visible in composer
    }
  ]
}
```

---

## 5. Header Customization

```typescript
header: {
  title: { enabled: false },  // Hide default title
  rightAction: {
    icon: scheme === "dark" ? "light-mode" : "dark-mode",
    onClick: () => setScheme(scheme === "dark" ? "light" : "dark")
  }
}
```

**Note**: If you have a custom navbar, you might want to disable ChatKit's header entirely and handle theme toggle in your navbar.

---

## 6. Widget Rendering

Widgets are custom UI components that appear inline with chat messages. They're defined in the backend and streamed to the frontend.

### How Widgets Work

**Backend**: You create a `.widget` file (JSON with Jinja2 template)
```python
# backend/app/widgets/hexagram.widget (JSON file with Jinja2 template)
{
  "type": "widget",
  "template": """
    <div style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 28px 20px; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 12px;">
      <div style="font-size: 72px; line-height: 1;">{{ symbol }}</div>
      <div style="font-family: var(--font-display); font-weight: 600; font-size: 20px;">{{ number }} · {{ english_name }}</div>
      <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: center;">
        <span style="font-size: 12px; padding: 4px 10px; border-radius: 9999px; background: rgba(155, 133, 183, 0.2); color: var(--purple);">{{ chinese }}</span>
        <span style="font-size: 12px; padding: 4px 10px; border-radius: 9999px; background: var(--border-color); color: var(--text-secondary);">Pinyin: {{ pinyin }}</span>
      </div>
      <p style="font-size: 15px; color: var(--text-muted); line-height: 1.5; max-width: 400px;">{{ description }}</p>
    </div>
  """
}
```

Then stream it from your backend:
```python
ctx.context.stream_widget(widget)
```

ChatKit will render this HTML inside the chat messages.

---

## 7. Layout Structure

### Example HTML Structure
```html
<body>
  <nav class="navbar">...</nav>
  <main class="app-page">
    <div class="chat-container">
      <div class="chat-card">
        <!-- Chat messages go here -->
      </div>
    </div>
  </main>
</body>
```

### Equivalent React/ChatKit Structure
```typescript
// App.tsx
<div className="flex flex-col h-screen">
  {/* Your custom navbar */}
  <nav className="navbar">
    <NavbarLeft />
    <NavbarRight>
      <ThemeToggle />
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
    </NavbarRight>
  </nav>

  {/* Main content */}
  <main className="app-page">
    <div className="chat-container">
      {/* ChatKit fills this container */}
      <ChatKitPanel
        className="chat-card"
        onChatKitReady={(chatkit) => chatkitRef.current = chatkit}
      />
    </div>
  </main>
</div>
```

### Styling the Container
```css
/* Your Tailwind/CSS */
.app-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-md);
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.chat-container {
  width: 100%;
  max-width: 720px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-card {
  flex: 1;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  min-height: 500px;
  max-height: calc(100vh - 100px);
  box-shadow: var(--shadow-medium);
}
```

---

## 8. State Management (Zustand Pattern)

All ChatKit examples use Zustand for state:

```typescript
// store/useAppStore.ts
import { create } from "zustand";

type ColorScheme = "light" | "dark";

interface AppState {
  scheme: ColorScheme;
  setScheme: (scheme: ColorScheme) => void;
  threadId: string | null;
  setThreadId: (threadId: string | null) => void;
}

export const useAppStore = create<AppState>((set) => {
  const initialScheme = getInitialScheme(); // Check localStorage + system pref
  syncSchemeWithDocument(initialScheme);

  return {
    scheme: initialScheme,
    setScheme: (scheme) => {
      syncSchemeWithDocument(scheme);
      set({ scheme });
    },
    threadId: null,
    setThreadId: (threadId) => set({ threadId }),
  };
});

function syncSchemeWithDocument(scheme: ColorScheme) {
  const root = document.documentElement;
  if (scheme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
  localStorage.setItem("theme", scheme);
}

function getInitialScheme(): ColorScheme {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
```

---

## 9. Global CSS Setup

```css
/* index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@font-face {
  font-family: "Lexend";
  src: url("https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500&display=swap");
  font-weight: 300 500;
  font-display: swap;
}

@font-face {
  font-family: "Lexend Giga";
  src: url("https://fonts.googleapis.com/css2?family=Lexend+Giga:wght@400;600;900&display=swap");
  font-weight: 400 900;
  font-display: swap;
}

:root {
  /* Color variables */
  --bg-primary: #FDF6E3;
  --bg-surface: #F5EFE0;
  --text-primary: #464646;
  --text-secondary: #657B83;
  --text-muted: #93A1A1;
  --border-color: rgba(101, 123, 131, 0.1);
  --purple: #9B85B7;
  --font-display: 'Lexend Giga', sans-serif;
  --font-body: 'Lexend', sans-serif;
  /* ... other colors */
}

html.dark {
  --bg-primary: #1a1a1a;
  --bg-surface: #2d2d2d;
  --text-primary: #E8E8E8;
  --text-secondary: #A8A8A8;
  --text-muted: #6B6B6B;
  --border-color: rgba(168, 168, 168, 0.1);
}

html, body, #root {
  height: 100%;
  margin: 0;
}

body {
  font-family: var(--font-body);
  font-weight: 300;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 200ms ease, color 200ms ease;
}
```

---

## 10. Key Differences: HTML vs ChatKit React

| Aspect | Static HTML | ChatKit React Equivalent |
|--------|-------------|--------------------------|
| **Structure** | Static HTML with `.chat-messages` div | `<ChatKit>` component renders messages internally |
| **Message Bubbles** | `.chat-message-bubble` styled manually | ChatKit handles bubble styling via theme config |
| **Input Area** | `.chat-input-area` with custom input | ChatKit `composer` config controls placeholder/tools |
| **Widgets** | Hardcoded HTML | Backend streams widget templates, ChatKit renders |
| **Theme Toggle** | Vanilla JS `classList.toggle('dark')` | Zustand state + `syncSchemeWithDocument()` |
| **Scrolling** | `.chat-messages { overflow-y: auto }` | ChatKit handles scroll internally |

---

## 11. Per-Agent Accent Colors

For different agents, you can dynamically change the accent color:

```typescript
// In ChatKitPanel or App.tsx
const AGENT_COLORS = {
  gptching: "#9B85B7",   // purple
  cupid: "#E7B5A0",      // pink
  metro: "#DA6800",      // orange
  news: "#D74E39",       // red
  cat: "#FFC922",        // yellow
  support: "#8AA47D",    // green
};

const currentAgent = "gptching"; // From route or context

const chatkit = useChatKit({
  theme: {
    color: {
      accent: {
        primary: AGENT_COLORS[currentAgent],
        level: 1,
      }
    }
  }
});
```

---

## 12. Customization Capabilities

### ✅ What You CAN Customize
- **Colors**: Full control via `theme.color` (grayscale hue, accent, surface colors)
- **Typography**: Custom fonts via `theme.typography`
- **Density**: Spacing via `theme.density`
- **Border Radius**: `theme.radius` (sharp/round/pill)
- **Container Styling**: ChatKit fills its parent, so you control size/position via wrapper divs
- **Widgets**: Full HTML/CSS control via backend widget templates
- **Start Screen**: Welcome message and prompt suggestions
- **Composer**: Placeholder text and tool buttons
- **Header**: Optional custom right action button

### ❌ What You CANNOT Customize Directly
- **Internal message bubble HTML structure**: ChatKit renders these, but you can style them via theme
- **Scroll behavior**: ChatKit handles this internally
- **Message ordering/layout**: Controlled by ChatKit

---

## Real-World Examples from ChatKit Repo

### News Guide
- **Theme**: Warm serif feel with Lora font
- **Accent**: Coral (`#ff5f42`)
- **Radius**: Sharp
- **Layout**: Two-panel (chat left, article right)
- **Unique Feature**: Custom fetch interceptor passes article-id header

### Cat Lounge
- **Theme**: Cool blues with round borders
- **Accent**: Theme-aware (light/dark specific colors)
- **Radius**: Round
- **Layout**: Centered modal/card style with backdrop
- **Unique Feature**: Entity tag search for cat breeds

### Metro Map
- **Theme**: Custom dark mode with OpenAI Sans font
- **Accent**: Sky blue (`#0ea5e9`)
- **Radius**: Pill
- **Layout**: Full-screen with custom header action
- **Unique Feature**: Theme toggle in ChatKit header (not external navbar)

### Customer Support
- **Theme**: Minimal customization, relies on defaults
- **Accent**: Theme-aware colors
- **Radius**: Round
- **Layout**: Two-panel (chat left, order details right)
- **Unique Feature**: useColorScheme hook pattern

---

## Quick Reference: Common Patterns

### Dark Mode Implementation
```typescript
// 1. Store in Zustand
const [scheme, setScheme] = useState<"light" | "dark">("light");

// 2. Sync with DOM
useEffect(() => {
  document.documentElement.classList.toggle("dark", scheme === "dark");
  localStorage.setItem("theme", scheme);
}, [scheme]);

// 3. Pass to ChatKit
theme: { colorScheme: scheme }
```

### Per-Route Theming
```typescript
// Different accent colors per agent/route
const AGENT_THEMES = {
  "/gptching": { accent: "#9B85B7", hue: 40 },
  "/cupid": { accent: "#E7B5A0", hue: 10 },
  "/metro": { accent: "#DA6800", hue: 30 },
};

const route = useLocation().pathname;
const themeConfig = AGENT_THEMES[route] || AGENT_THEMES["/gptching"];
```

### Custom Container Sizing
```css
/* Full screen minus navbar */
.chat-container {
  height: calc(100vh - 64px);
  max-width: 720px;
  margin: 0 auto;
}

/* Modal/card style */
.chat-card {
  width: 45%;
  height: 80vh;
  border-radius: 24px;
  box-shadow: 0 45px 90px -45px rgba(0,0,0,0.3);
}
```

---

## Troubleshooting

**Problem**: Theme colors don't apply
**Solution**: Ensure `colorScheme` matches your DOM's `html.dark` class

**Problem**: Fonts don't load
**Solution**: Check `fontSources` array format and verify URLs are accessible

**Problem**: Widgets don't render
**Solution**: Verify `.widget` file syntax (valid JSON with Jinja2 template)

**Problem**: Dark mode flickers on page load
**Solution**: Initialize theme in `<head>` script before React renders

---

## Additional Resources

- **ChatKit SDK**: `@openai/chatkit-react` package
- **Widget Templates**: See `backend/app/widgets/*.widget` in examples
- **Agent Patterns**: See `backend/app/agents/*_agent.py` for tool implementations
- **State Management**: Zustand patterns in `frontend/src/store/`
