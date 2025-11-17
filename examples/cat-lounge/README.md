# Cat Lounge

Virtual cat caretaker demo built with ChatKit (FastAPI backend + Vite/React frontend).

## Quickstart

1. Export `OPENAI_API_KEY`.
2. From the repo root run `npm run cat-lounge` (or `cd examples/cat-lounge && npm install && npm run start`).
3. Go to http://localhost:5170

## Example prompts

- "Feed the cat a tuna treat."
- "The cat looks a little messy—give them a bath."
- "What should I name the cat?"
- "Can I see the cat's profile card?"
- "Hello, cat! How are you feeling?"

## Features

- Server tools to read and mutate per-thread cat state: `get_cat_status`, `feed_cat`, `play_with_cat`, `clean_cat`, `set_cat_name`, `speak_as_cat`.
- Name suggestion workflow with a selectable widget and client-handled actions (`cats.select_name`, `cats.more_names`) plus server reconciliation for chosen names.
- Profile card widget (`show_cat_profile`) streamed from the server with presentation-only content.
- Client tool call `update_cat_status` keeps the UI stats in sync after each server tool invocation.
- Hidden context tags track recent actions (<FED_CAT>, <PLAYED_WITH_CAT>, <CLEANED_CAT>, <CAT_NAME_SELECTED>) so the agent remembers what already happened.
- Quick actions call `chatkit.sendUserMessage` to send canned requests without typing ([App.tsx](frontend/src/App.tsx)).
