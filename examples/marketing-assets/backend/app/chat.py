"""ChatKit server integration for the boilerplate backend."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Annotated, Any, AsyncIterator, Final, Literal, cast
from uuid import uuid4

from agents import Agent, RunContextWrapper, Runner, function_tool
from chatkit.agents import (
    AgentContext,
    ClientToolCall,
    ThreadItemConverter,
    stream_agent_response,
)
from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageItem,
    Attachment,
    ClientToolCallItem,
    HiddenContextItem,
    ThreadItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)
from chatkit.widgets import Card
from chatkit.widgets import Image as WidgetImage
from chatkit.widgets import Text as WidgetText
from openai import AsyncOpenAI
from openai.types.responses import ResponseInputContentParam
from pydantic import ConfigDict, Field

from .ad_assets import AdAsset, ad_asset_store
from .constants import INSTRUCTIONS, MODEL
from .memory_store import MemoryStore

SUPPORTED_COLOR_SCHEMES: Final[frozenset[str]] = frozenset({"light", "dark"})
CLIENT_THEME_TOOL_NAME: Final[str] = "switch_theme"
OPENAI_IMAGE_MODEL: Final[str] = "gpt-image-1"
MAX_IMAGE_ATTEMPTS: Final[int] = 3


def _normalize_color_scheme(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized in SUPPORTED_COLOR_SCHEMES:
        return normalized
    if "dark" in normalized:
        return "dark"
    if "light" in normalized:
        return "light"
    raise ValueError("Theme must be either 'light' or 'dark'.")


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class AdAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: dict[str, Any]


async def _stream_asset_hidden(ctx: RunContextWrapper[AdAgentContext], asset: AdAsset) -> None:
    prompt_summary = " | ".join(asset.image_prompts[:2]) if asset.image_prompts else ""
    images_summary = f' count="{len(asset.images)}"' if asset.images else ""
    details = (
        f'<AD_ASSET id="{asset.id}" product="{asset.product}" style="{asset.style}" '
        f'tone="{asset.tone}" pitch="{asset.pitch}">'
        f"<HEADLINE>{asset.headline}</HEADLINE>"
        f"<COPY>{asset.primary_text}</COPY>"
        f"<CTA>{asset.call_to_action}</CTA>"
        f"<PROMPTS>{prompt_summary}</PROMPTS>"
        f"<IMAGES{images_summary}/ />"
        "</AD_ASSET>"
    )
    hidden_item = HiddenContextItem(
        id=_gen_id("msg"),
        thread_id=ctx.context.thread.id,
        created_at=datetime.now(),
        content=details,
    )
    await ctx.context.stream(ThreadItemDoneEvent(item=hidden_item))


@function_tool(
    description_override=(
        "Store a finalized ad concept including copy and image prompts so it can be shown in the campaign gallery."
    )
)
async def save_ad_asset(
    ctx: RunContextWrapper[AdAgentContext],
    product: str,
    style: str,
    tone: str,
    pitch: str,
    headline: str,
    primary_text: str,
    call_to_action: str,
    image_prompts: list[str],
    images: list[str] | None = None,
    asset_id: str | None = None,
) -> dict[str, str]:
    metadata = dict(getattr(ctx.context.thread, "metadata", {}) or {})
    sanitized_prompts = [prompt.strip() for prompt in image_prompts if prompt.strip()]
    if not sanitized_prompts:
        sanitized_prompts = ["Visual direction forthcoming"]
    sanitized_images = [img.strip() for img in (images or []) if img.strip()]
    pending_images = list(metadata.get("pending_images") or [])
    latest_asset_id = asset_id or metadata.get("latest_asset_id")
    merged_images = sanitized_images or []
    if pending_images:
        merged_images = list(dict.fromkeys(merged_images + pending_images))
    clean_product = product.strip()
    clean_style = style.strip()
    clean_tone = tone.strip()
    clean_pitch = pitch.strip()
    clean_headline = headline.strip()
    clean_primary = primary_text.strip()
    clean_cta = call_to_action.strip()
    if not all(
        [
            clean_product,
            clean_style,
            clean_tone,
            clean_pitch,
            clean_headline,
            clean_primary,
            clean_cta,
        ]
    ):
        raise ValueError("All ad fields must be provided before saving the asset.")

    asset = await ad_asset_store.create(
        product=clean_product,
        style=clean_style,
        tone=clean_tone,
        pitch=clean_pitch,
        headline=clean_headline,
        primary_text=clean_primary,
        call_to_action=clean_cta,
        image_prompts=sanitized_prompts,
        images=merged_images if merged_images else None,
        asset_id=latest_asset_id,
    )
    thread = ctx.context.thread
    metadata["latest_asset_id"] = asset.id
    if merged_images:
        metadata.pop("pending_images", None)
    thread.metadata = metadata
    await ctx.context.store.save_thread(thread, ctx.context.request_context)
    await _stream_asset_hidden(ctx, asset)
    asset_arguments: dict[str, Any] = {"asset": asset.as_dict()}
    ctx.context.client_tool_call = ClientToolCall(
        name="record_ad_asset",
        arguments=asset_arguments,
    )
    print(f"AD ASSET SAVED: {asset}")
    return {
        "asset_id": asset.id,
        "status": "saved",
        "image_count": str(len(asset.images or [])),
    }


@function_tool(
    description_override=(
        "Generate a marketing-ready image for the campaign using the image generation model."
    )
)
async def generate_ad_image(
    ctx: RunContextWrapper[AdAgentContext],
    prompt: str,
    size: Literal["256x256", "512x512", "1024x1024", "square", "portrait", "landscape"]
    | str = "1024x1024",
) -> dict[str, str | bool | None]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Image generation requires OPENAI_API_KEY to be configured on the server."
        )

    client = AsyncOpenAI(api_key=api_key)
    normalized_size = str(size).strip().lower()
    allowed_sizes = {"256x256", "512x512", "1024x1024"}
    if normalized_size in {"square", "default", "portrait", "landscape"}:
        normalized_size = "1024x1024"
    elif normalized_size not in allowed_sizes:
        normalized_size = "1024x1024"

    attempt = 0
    while attempt < MAX_IMAGE_ATTEMPTS:
        attempt += 1
        try:
            normalized_size_literal = cast(
                Literal["256x256", "512x512", "1024x1024"],
                normalized_size,
            )
            response = await client.images.generate(
                model=OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size=normalized_size_literal,
                quality="high",
            )
            data = getattr(response, "data", None)
            if not data:
                raise RuntimeError("Image generation returned no results.")
            first = data[0]
            image_b64 = getattr(first, "b64_json", None)
            if not image_b64:
                raise RuntimeError("Image generation produced an unexpected payload.")
            data_url = f"data:image/png;base64,{image_b64}"
            caption = f"Generated for prompt: {prompt}".strip()
            widget = Card(
                children=[
                    WidgetImage(
                        src=data_url,
                        alt=prompt,
                        radius="xl",
                        fit="contain",
                    ),
                    WidgetText(
                        value=caption,
                        size="sm",
                        color="secondary",
                    ),
                ]
            )
            await ctx.context.stream_widget(widget)

            thread = ctx.context.thread
            metadata = dict(getattr(thread, "metadata", {}) or {})
            latest_asset_id = metadata.get("latest_asset_id")
            pending_images = list(metadata.get("pending_images") or [])

            updated_asset: AdAsset | None = None
            if latest_asset_id:
                updated_asset = await ad_asset_store.append_image(latest_asset_id, data_url)
                if updated_asset is None:
                    latest_asset_id = None

            if not latest_asset_id:
                pending_images.append(data_url)
                metadata["pending_images"] = pending_images
            else:
                metadata.pop("pending_images", None)
                if updated_asset is not None:
                    updated_arguments: dict[str, Any] = {"asset": updated_asset.as_dict()}
                    ctx.context.client_tool_call = ClientToolCall(
                        name="record_ad_asset",
                        arguments=updated_arguments,
                    )
                else:
                    metadata.setdefault("pending_images", []).append(data_url)

            thread.metadata = metadata
            await ctx.context.store.save_thread(thread, ctx.context.request_context)

            return {
                "status": "generated",
                "image_available": True,
                "asset_id": metadata.get("latest_asset_id"),
            }
        except Exception as exc:  # noqa: BLE001
            if attempt >= MAX_IMAGE_ATTEMPTS:
                print(
                    "[generate_ad_image] failed",
                    {
                        "prompt": prompt,
                        "size": normalized_size,
                        "error": str(exc),
                    },
                )
                raise RuntimeError(f"Image generation failed repeatedly: {exc}") from exc
            await asyncio.sleep(attempt * 0.75)

    raise RuntimeError("Image generation failed unexpectedly.")


@function_tool(
    description_override=("Switch the chat interface between light and dark color schemes.")
)
async def switch_theme(
    ctx: RunContextWrapper[AdAgentContext],
    theme: str,
) -> dict[str, str]:
    requested = _normalize_color_scheme(theme)
    ctx.context.client_tool_call = ClientToolCall(
        name=CLIENT_THEME_TOOL_NAME,
        arguments={"theme": requested},
    )
    return {"theme": requested}


def _user_message_text(item: UserMessageItem) -> str:
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


class AdCreativeServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the ad generation workflow."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)
        tools = [save_ad_asset, switch_theme, generate_ad_image]
        self.assistant = Agent[AdAgentContext](
            model=MODEL,
            name="Ad Generation Helper",
            instructions=INSTRUCTIONS,
            tools=tools,  # type: ignore[arg-type]
        )
        self._thread_item_converter = self._init_thread_item_converter()

    async def respond(
        self,
        thread: ThreadMetadata,
        input: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if input is None:
            return

        if isinstance(input, ClientToolCallItem):
            return

        if not isinstance(input, UserMessageItem):
            return

        agent_context = AdAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        agent_input = await self._to_agent_input(thread, input, context)
        if agent_input is None:
            return

        metadata = dict(getattr(thread, "metadata", {}) or {})
        previous_response_id = metadata.get("previous_response_id")
        agent_context.previous_response_id = previous_response_id

        result = Runner.run_streamed(
            self.assistant,
            agent_input,
            context=agent_context,
            previous_response_id=previous_response_id,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

        if result.last_response_id is not None:
            metadata["previous_response_id"] = result.last_response_id
            thread.metadata = metadata
            await self.store.save_thread(thread, context)

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported by the ChatKit demo backend.")

    def _init_thread_item_converter(self) -> Any | None:
        converter_cls = ThreadItemConverter
        if converter_cls is None or not callable(converter_cls):
            return None

        attempts: tuple[dict[str, Any], ...] = (
            {"to_message_content": self.to_message_content},
            {"message_content_converter": self.to_message_content},
            {},
        )

        for kwargs in attempts:
            try:
                return converter_cls(**kwargs)
            except TypeError:
                continue
        return None

    async def _to_agent_input(
        self,
        thread: ThreadMetadata,
        item: ThreadItem,
        context: dict[str, Any],
    ) -> Any | None:
        converter = getattr(self, "_thread_item_converter", None)
        history: list[ThreadItem] = []
        try:
            loaded = await self.store.load_thread_items(
                thread.id,
                after=None,
                limit=50,
                order="desc",
                context=context,
            )
            history = list(reversed(loaded.data))
        except Exception:  # noqa: BLE001
            history = []

        latest_id = getattr(item, "id", None)
        if latest_id is None or not any(
            getattr(existing, "id", None) == latest_id for existing in history
        ):
            history.append(item)

        relevant: list[ThreadItem] = [
            entry
            for entry in history
            if isinstance(
                entry,
                (
                    UserMessageItem,
                    AssistantMessageItem,
                    ClientToolCallItem,
                ),
            )
        ]

        if len(relevant) > 12:
            relevant = relevant[-12:]

        if converter is not None and relevant:
            to_agent = getattr(converter, "to_agent_input", None)
            if callable(to_agent):
                try:
                    return await to_agent(relevant)
                except TypeError:
                    pass

        for entry in reversed(relevant):
            if isinstance(entry, UserMessageItem):
                return _user_message_text(entry)

        if isinstance(item, UserMessageItem):
            return _user_message_text(item)

        return None

    async def _add_hidden_item(
        self,
        thread: ThreadMetadata,
        context: dict[str, Any],
        content: str,
    ) -> None:
        await self.store.add_thread_item(
            thread.id,
            HiddenContextItem(
                id=_gen_id("msg"),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=content,
            ),
            context,
        )


def create_chatkit_server() -> AdCreativeServer:
    """Return a configured ChatKit server instance if dependencies are available."""
    return AdCreativeServer()
