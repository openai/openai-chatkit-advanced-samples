from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated, Any, Callable

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ClientEffectEvent,
    HiddenContextItem,
    ThreadItemDoneEvent,
)
from pydantic import ConfigDict, Field, ValidationError

from .cat_state import CatState
from .cat_store import CatStore
from .memory_store import MemoryStore
from .widgets.name_suggestions_widget import CatNameSuggestion, build_name_suggestions_widget
from .widgets.profile_card_widget import build_profile_card_widget, profile_widget_copy_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INSTRUCTIONS: str = """
    You are Cozy Cat Companion, a playful caretaker helping the user look after a virtual cat.
    Keep interactions light, imaginative, and focused on the cat's wellbeing. Provide concise
    status updates and narrate what happens after each action.

    Let the user know that the cat's color pattern will stay a mystery until they officially name it.

    Always keep the per-thread cat stats (energy, happiness, cleanliness, name, age)
    in sync with the tools provided. When you need the latest numbers, call `get_cat_status` before making a plan.

    Tools:
    - When the user asks you to feed, play with, or clean the cat, immediately call the respective tool
      (`feed_cat`, `play_with_cat`, or `clean_cat`). Describe the outcome afterwards using the updated stats.
      - When feeding, mention specific snacks or cat treats that was used to feed that cat if the user did not specify any food.
      - When playing, mention specific toys or objects that cats usually like that was used to play with the cat if the user did not specify any item.
      - When cleaning, mention specific items or methods that were used to clean the cat if the user did not specify any method.
      - If the user asks to "freshen up" the cat, call the `clean_cat` tool.
      - Once an action has been performed, it will be reflected as a <FED_CAT>, <PLAYED_WITH_CAT>, or <CLEANED_CAT> tag in the thread content.
      - Do not fire off multiple tool calls for the same action unless the user explicitly asks for it.
      - When the user interacts with an unnamed cat, prompt the user to name the cat.
    - When you call `suggest_cat_names`, pass a `suggestions` array containing at least three creative options.
      Each suggestion must include `name` (short and unique) and `reason` (why it fits the cat's current personality or stats).
      Prefer single word names, but if the suggested name is multiple words, use a space to separate them. For example: "Mr. Whiskers" or "Fluffy Paws".
      The user's choice will be reflected as a <CAT_NAME_SELECTED> tag in the thread content. Use that name in all future
      responses.
    - When the user explicitly asks for a profile card, call `show_cat_profile` with the age of the cat (for example: 1, 2, 3, etc.) and the name of a favorite toy (for example: "Ball of yarn", "Stuffed mouse", be creative but keep it two words or less!)
    - When the user's message is addressed directly to the cat, call `speak_as_cat` with the desired line so the dashboard bubbles it.
      When speaking as the cat, use "meow" or "purr" with a parenthesis at the end to translate it into English. For example: meow (I'm low on energy)
    - Never call `set_cat_name` if the cat already has a name that is not "Unnamed Cat".
    - If the cat currently does not have a name and the user explicitly names the cat, call `set_cat_name` with the exact name.
      Use that name in all future responses.

    Stay in character: talk about caring for the cat, suggest next steps if the stats look unbalanced, and avoid unrelated topics.

    Notes:
    - If the user has not yet named the cat, ask if they'd like to name it.
    - The cat's color pattern is only revealed once it has been named; encourage the user to name the cat to discover it.
    - Once a cat is named, it cannot be renamed. Do not invoke the `set_cat_name` tool if the cat has already been named.
    - If a user addresses an unnamed cat by a name for the first time, ask the user whether they'd like to name the cat.
    - If a user indicates they want to name the cat but does not provide a name, call the `suggest_cat_names` tool to give some options.
    - After naming the cat, let the user know that the cat's profile card has been issued and ask them whether they'd like to see it.
"""

MODEL = "gpt-4.1-mini"


class CatAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    cats: Annotated[CatStore, Field(exclude=True)]
    request_context: dict[str, Any]


async def _get_state(ctx: RunContextWrapper[CatAgentContext]) -> CatState:
    thread_id = ctx.context.thread.id
    return await ctx.context.cats.load(thread_id)


async def _update_state(
    ctx: RunContextWrapper[CatAgentContext],
    mutator: Callable[[CatState], None],
) -> CatState:
    thread_id = ctx.context.thread.id
    return await ctx.context.cats.mutate(thread_id, mutator)


async def _sync_status(
    ctx: RunContextWrapper[CatAgentContext],
    state: CatState,
    flash: str | None = None,
) -> None:
    await ctx.context.stream(
        ClientEffectEvent(
            name="update_cat_status",
            data={
                "state": state.to_payload(ctx.context.thread.id),
                "flash": flash,
            },
        )
    )


async def _add_hidden_context(ctx: RunContextWrapper[CatAgentContext], content: str) -> None:
    # Add a hidden context item so that future agent input will know that an action has been performed.
    thread = ctx.context.thread
    request_context = ctx.context.request_context
    await ctx.context.store.add_thread_item(
        thread.id,
        HiddenContextItem(
            id=ctx.context.store.generate_item_id("message", thread, ctx.context.request_context),
            thread_id=thread.id,
            created_at=datetime.now(),
            content=content,
        ),
        context=request_context,
    )


@function_tool(
    description_override=(
        "Read the cat's current stats before deciding what to do next. No parameters."
    )
)
async def get_cat_status(
    ctx: RunContextWrapper[CatAgentContext],
) -> dict[str, Any]:
    logger.info("[TOOL CALL] get_cat_status")
    state = await _get_state(ctx)
    # Must return payload so that the assistant can use it to generate a natural language response.
    return state.to_payload(ctx.context.thread.id)


@function_tool(
    description_override=(
        "Feed the cat to replenish energy and keep moods stable.\n"
        "- `meal`: Meal or snack description to include in the update."
    )
)
async def feed_cat(
    ctx: RunContextWrapper[CatAgentContext],
    meal: str | None = None,
):
    logger.info("[TOOL CALL] feed_cat")
    state = await _update_state(ctx, lambda s: s.feed())
    flash = f"Fed {state.name} {meal}" if meal else f"{state.name} enjoyed a snack"
    await _add_hidden_context(ctx, f"<FED_CAT>{flash}</FED_CAT>")
    await _sync_status(ctx, state, flash)
    # No need to return payload for a client tool call; agent must be configured to stop after this tool call.


@function_tool(
    description_override=(
        "Play with the cat to boost happiness and create fun moments.\n"
        "- `activity`: Toy or activity used during playtime."
    )
)
async def play_with_cat(
    ctx: RunContextWrapper[CatAgentContext],
    activity: str | None = None,
):
    logger.info("[TOOL CALL] play_with_cat")
    state = await _update_state(ctx, lambda s: s.play())
    flash = activity or "Playtime"
    await _add_hidden_context(ctx, f"<PLAYED_WITH_CAT>{flash}</PLAYED_WITH_CAT>")
    await _sync_status(ctx, state, f"{state.name} played: {flash}")
    # No need to return payload for a client tool call; agent must be configured to stop after this tool call.


@function_tool(
    description_override=(
        "Clean the cat to tidy up and improve cleanliness.\n"
        "- `method`: Cleaning method or item used."
    )
)
async def clean_cat(
    ctx: RunContextWrapper[CatAgentContext],
    method: str | None = None,
):
    logger.info("[TOOL CALL] clean_cat")
    state = await _update_state(ctx, lambda s: s.clean())
    flash = method or "Bath time"
    await _add_hidden_context(ctx, f"<CLEANED_CAT>{flash}</CLEANED_CAT>")
    await _sync_status(ctx, state, f"{state.name} is fresh: {flash}")
    # No need to return payload for a client tool call; agent must be configured to stop after this tool call.


@function_tool(
    description_override=(
        "Give the cat a permanent name and update the thread title to match.\n"
        "- `name`: Desired name for the cat."
    )
)
async def set_cat_name(
    ctx: RunContextWrapper[CatAgentContext],
    name: str,
):
    logger.info('[TOOL CALL] set_cat_name("%s")', name)

    try:
        state = await _get_state(ctx)
        if state.name != "Unnamed Cat":
            await ctx.context.stream(
                ThreadItemDoneEvent(
                    item=AssistantMessageItem(
                        thread_id=ctx.context.thread.id,
                        id=ctx.context.generate_id("message"),
                        created_at=datetime.now(),
                        content=[AssistantMessageContent(text=f"{state.name} is ready to play!")],
                    ),
                )
            )
            return

        cleaned = name.strip().title()
        if not cleaned:
            raise ValueError("A name is required to rename the cat.")

        state = await _update_state(ctx, lambda s: s.rename(cleaned))

        ctx.context.thread.title = f"{state.name}’s Lounge"
        await ctx.context.store.save_thread(ctx.context.thread, ctx.context.request_context)

        await _add_hidden_context(ctx, f"<CAT_NAME_SELECTED>{state.name}</CAT_NAME_SELECTED>")
        await _sync_status(ctx, state, f"Now called {state.name}")
    except Exception as exc:
        logger.error("Error setting cat name: %s", exc)
        raise

    # No need to return payload for a client tool call; agent must be configured to stop after this tool call.


@function_tool(
    description_override=(
        "Show the cat's profile card with avatar and age.\n"
        "- `age`: Cat age (in years) to display and persist.\n"
        "- `favorite_toy`: Favorite toy label to include."
    )
)
async def show_cat_profile(
    ctx: RunContextWrapper[CatAgentContext],
    age: int | None = None,
    favorite_toy: str | None = None,
):
    def mutate(state: CatState) -> None:
        state.set_age(age)

    state = await _update_state(ctx, mutate)
    widget = build_profile_card_widget(state, favorite_toy)
    await ctx.context.stream_widget(widget, copy_text=profile_widget_copy_text(state))

    if state.name == "Unnamed Cat":
        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(text="Would you like to give your cat a name?")
                    ],
                ),
            )
        )

    else:
        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text=f"License checked! Would you like to feed, play with, or clean {state.name}?"
                        )
                    ],
                ),
            )
        )


@function_tool(
    description_override=(
        "Speak as the cat so a bubble appears in the dashboard.\n"
        "- `line`: The text the cat should say."
    )
)
async def speak_as_cat(
    ctx: RunContextWrapper[CatAgentContext],
    line: str,
):
    logger.info("[TOOL CALL] speak_as_cat(%s)", line)
    message = line.strip()
    if not message:
        raise ValueError("A line is required for the cat to speak.")
    state = await _get_state(ctx)
    await ctx.context.stream(
        ClientEffectEvent(
            name="cat_say",
            data={
                "state": state.to_payload(ctx.context.thread.id),
                "message": message,
            },
        )
    )
    # ctx.context.client_tool_call = ClientToolCall(
    #     name="cat_say",
    #     arguments={
    #         "state": state.to_payload(ctx.context.thread.id),
    #         "message": message,
    #     },
    # )


@function_tool(
    description_override=(
        "Render up to three creative cat name options provided in the `suggestions` argument.\n"
        "- `suggestions`: List of name suggestions with a `name` and `reason` for each."
    )
)
async def suggest_cat_names(
    ctx: RunContextWrapper[CatAgentContext],
    suggestions: list[CatNameSuggestion],
):
    logger.info("[TOOL CALL] suggest_cat_names")
    try:
        normalized: list[CatNameSuggestion] = []
        for entry in suggestions:
            try:
                normalized.append(
                    entry
                    if isinstance(entry, CatNameSuggestion)
                    else CatNameSuggestion.model_validate(entry)
                )
            except ValidationError as exc:
                logger.warning("Invalid name suggestion payload: %s", exc)
        if not normalized:
            raise ValueError("Provide at least one valid name suggestion before calling the tool.")

        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(text="Here are some name suggestions for your cat.")
                    ],
                ),
            )
        )

        widget = build_name_suggestions_widget(normalized)
        await ctx.context.stream_widget(
            widget, copy_text=", ".join(suggestion.name for suggestion in normalized)
        )
    except Exception as exc:
        logger.error("Error suggesting cat names: %s", exc)
        raise


cat_agent = Agent[CatAgentContext](
    model=MODEL,
    name="Cozy Cat Companion",
    instructions=INSTRUCTIONS,
    tools=[
        # Fetches data used by the agent to run inference.
        get_cat_status,
        # Produces a simple widget output.
        show_cat_profile,
        # Invokes a client effect to make the cat speak.
        speak_as_cat,
        # Mutates state then invokes a client effect to sync client state.
        feed_cat,
        play_with_cat,
        clean_cat,
        # Mutates both cat state and thread state then invokes a client effect
        # to sync client state.
        set_cat_name,
        # Outputs interactive widget output with partially agent-generated content.
        suggest_cat_names,
    ],
    # Stop inference after tool calls with widget outputs to prevent repetition.
    tool_use_behavior=StopAtTools(
        stop_at_tool_names=[
            suggest_cat_names.name,
            show_cat_profile.name,
        ]
    ),
)
