"""
Example: Integrating ChatKit with WhatsApp using pywa

This example demonstrates how to use the non-streaming /chatkit/complete endpoint
with WhatsApp Business API via the pywa library.

Installation:
    pip install pywa

Usage:
    1. Set up your WhatsApp Business API credentials
    2. Configure the environment variables (WHATSAPP_TOKEN, etc.)
    3. Run this script to start the WhatsApp bot
"""

import json
import os
from typing import Any

import httpx
from pywa import WhatsApp
from pywa.types import Message

# Configuration
CHATKIT_BACKEND_URL = os.getenv(
    "CHATKIT_BACKEND_URL", "http://localhost:8000"
)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "your-whatsapp-token")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "your-phone-id")

# Initialize WhatsApp client
wa = WhatsApp(
    phone_id=WHATSAPP_PHONE_NUMBER_ID,
    token=WHATSAPP_TOKEN,
)


async def send_to_chatkit(user_message: str, thread_id: str | None = None) -> dict[str, Any]:
    """
    Send a message to the ChatKit backend and get the complete response.

    Args:
        user_message: The user's message text
        thread_id: Optional thread ID for continuing a conversation

    Returns:
        dict with 'text', 'thread_id', 'message_id', and optional 'error'
    """
    # Build the ChatKit protocol request
    if thread_id:
        # Continue existing thread
        chatkit_request = {
            "type": "threads.add_user_message",
            "params": {
                "thread_id": thread_id,
                "input": {
                    "content": [{"type": "text", "text": user_message}],
                },
            },
        }
    else:
        # Create new thread
        chatkit_request = {
            "type": "threads.create",
            "params": {
                "input": {
                    "content": [{"type": "text", "text": user_message}],
                },
            },
        }

    # Send to the non-streaming endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CHATKIT_BACKEND_URL}/chatkit/complete",
            json=chatkit_request,
            headers={"Content-Type": "application/json"},
            timeout=60.0,  # Allow up to 60 seconds for response
        )
        response.raise_for_status()
        return response.json()


# Store thread IDs per WhatsApp user (in production, use a database)
user_threads: dict[str, str] = {}


@wa.on_message()
async def handle_message(client: WhatsApp, msg: Message):
    """Handle incoming WhatsApp messages."""
    user_id = msg.from_user.wa_id
    user_message = msg.text

    # Get or create thread for this user
    thread_id = user_threads.get(user_id)

    try:
        # Send to ChatKit and get complete response
        result = await send_to_chatkit(user_message, thread_id)

        # Store thread ID for future messages
        user_threads[user_id] = result["thread_id"]

        # Send response back to user
        response_text = result["text"]

        if result.get("error"):
            response_text = f"Error: {result['error']}\n\n{response_text}"

        msg.reply(text=response_text)

    except Exception as e:
        msg.reply(text=f"Sorry, I encountered an error: {str(e)}")


# For testing without pywa
async def test_chatkit_complete():
    """Simple test function to verify the endpoint works."""
    print("Testing /chatkit/complete endpoint...")

    # Test creating a new thread
    result1 = await send_to_chatkit("Hello! What's the weather?", None)
    print(f"\nResponse 1:")
    print(f"  Thread ID: {result1['thread_id']}")
    print(f"  Message ID: {result1['message_id']}")
    print(f"  Text: {result1['text']}")

    # Test continuing the conversation
    result2 = await send_to_chatkit(
        "Thanks! Tell me a joke.", result1["thread_id"]
    )
    print(f"\nResponse 2:")
    print(f"  Thread ID: {result2['thread_id']}")
    print(f"  Message ID: {result2['message_id']}")
    print(f"  Text: {result2['text']}")


if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        # Run test mode
        import asyncio

        asyncio.run(test_chatkit_complete())
    else:
        # Run WhatsApp bot
        wa.run()
