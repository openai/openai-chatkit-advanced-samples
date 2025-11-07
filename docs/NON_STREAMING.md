# Non-Streaming ChatKit Interface

This document describes the non-streaming interface for ChatKit, designed for integrations with platforms that don't support Server-Sent Events (SSE) streaming, such as WhatsApp, SMS, and other messaging platforms.

## Overview

The standard ChatKit endpoint (`POST /chatkit`) streams responses using Server-Sent Events, which is ideal for web applications but not suitable for platforms like WhatsApp that expect immediate, complete responses.

The non-streaming endpoint (`POST /chatkit/complete`) solves this by:
1. Accepting the same ChatKit protocol messages
2. Buffering all streaming events internally
3. Returning a complete JSON response with the full assistant message

## Endpoint

### `POST /chatkit/complete`

**Request Format:** Same as `/chatkit` endpoint (ChatKit protocol)

**Request Examples:**

Create a new thread:
```json
{
  "type": "threads.create",
  "params": {
    "input": {
      "content": [
        {
          "type": "text",
          "text": "Hello! What's the weather today?"
        }
      ]
    }
  }
}
```

Continue an existing thread:
```json
{
  "type": "threads.add_user_message",
  "params": {
    "thread_id": "thread_abc123",
    "input": {
      "content": [
        {
          "type": "text",
          "text": "Thanks! Tell me a joke."
        }
      ]
    }
  }
}
```

**Response Format:**

```json
{
  "text": "The complete assistant response text",
  "thread_id": "thread_abc123",
  "message_id": "msg_xyz789",
  "error": "Optional error message if something went wrong"
}
```

**Response Fields:**
- `text` (string): The complete assistant message text
- `thread_id` (string): The thread identifier (use this to continue the conversation)
- `message_id` (string): The unique message identifier
- `error` (string, optional): Error message if an error occurred during processing

## Use Cases

### 1. WhatsApp Integration with pywa

See the complete example in `backend/examples/whatsapp_integration.py`

```python
import httpx

async def send_to_chatkit(user_message: str, thread_id: str | None = None):
    chatkit_request = {
        "type": "threads.create" if not thread_id else "threads.add_user_message",
        "params": {
            "input": {"content": [{"type": "text", "text": user_message}]},
        }
    }

    if thread_id:
        chatkit_request["params"]["thread_id"] = thread_id

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chatkit/complete",
            json=chatkit_request,
            timeout=60.0,
        )
        return response.json()

# Usage
result = await send_to_chatkit("Hello!")
print(result["text"])  # Assistant's response
thread_id = result["thread_id"]  # Save for next message
```

### 2. SMS Integration

```python
from twilio.rest import Client

# Initialize Twilio
twilio_client = Client(account_sid, auth_token)

# Handle incoming SMS
def handle_sms(from_number: str, message_body: str):
    # Get thread_id for this phone number from database
    thread_id = get_thread_for_number(from_number)

    # Send to ChatKit
    result = send_to_chatkit(message_body, thread_id)

    # Save thread_id for future messages
    save_thread_for_number(from_number, result["thread_id"])

    # Send response via SMS
    twilio_client.messages.create(
        to=from_number,
        from_=your_twilio_number,
        body=result["text"]
    )
```

### 3. Slack Bot Integration

```python
from slack_bolt.async_app import AsyncApp

app = AsyncApp(token=slack_bot_token)

@app.message("")
async def handle_message(message, say):
    user_id = message["user"]
    text = message["text"]

    # Get thread_id for this Slack user
    thread_id = get_thread_for_user(user_id)

    # Send to ChatKit
    result = await send_to_chatkit(text, thread_id)

    # Save thread_id
    save_thread_for_user(user_id, result["thread_id"])

    # Reply in Slack
    await say(result["text"])
```

## Implementation Details

### How It Works

1. **Request Processing**: The endpoint receives ChatKit protocol messages
2. **Event Buffering**: All streaming events are collected internally
3. **Event Parsing**: Server-Sent Event (SSE) format is parsed
4. **Response Extraction**: The final `AssistantMessageItem` is extracted from `ThreadItemDoneEvent`
5. **Text Aggregation**: All content parts are combined into a single text string
6. **JSON Response**: Returns a simple JSON object with the complete message

### Supported Request Types

All conversational request types are supported:
- `threads.create` - Create a new conversation
- `threads.add_user_message` - Continue an existing conversation
- `threads.retry_after_item` - Retry generation after a specific item
- `threads.add_client_tool_output` - Add tool output and continue
- `threads.custom_action` - Handle custom widget actions

### Error Handling

Errors are captured and included in the response:

```json
{
  "text": "",
  "thread_id": "thread_abc123",
  "message_id": "error",
  "error": "Rate limit exceeded. Please try again later."
}
```

### Timeouts

The endpoint may take longer than the streaming version since it waits for the complete response. Configure your HTTP client with appropriate timeouts (recommended: 60+ seconds).

```python
# Example with httpx
response = await client.post(
    url,
    json=request,
    timeout=60.0  # 60 second timeout
)
```

## Performance Considerations

### Latency
- **Streaming endpoint**: First tokens arrive within ~500ms
- **Non-streaming endpoint**: Complete response after ~2-5 seconds

For WhatsApp and SMS, this latency is acceptable since users expect slight delays in chatbot responses.

### Memory Usage
Events are buffered in memory until the complete response is available. For typical conversations, this adds negligible memory overhead (< 1MB per request).

## Thread Management

Thread IDs must be persisted to maintain conversation context:

### In-Memory (Development)
```python
user_threads = {}  # user_id -> thread_id
```

### Database (Production)
```python
# PostgreSQL example
CREATE TABLE user_threads (
    user_id VARCHAR PRIMARY KEY,
    thread_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Redis (High-Performance)
```python
import redis
redis_client = redis.Redis()
redis_client.set(f"thread:{user_id}", thread_id, ex=86400)  # 24h expiry
```

## Comparison: Streaming vs Non-Streaming

| Feature | `/chatkit` (Streaming) | `/chatkit/complete` (Non-Streaming) |
|---------|------------------------|-------------------------------------|
| Response Type | Server-Sent Events | JSON |
| Latency | ~500ms to first token | ~2-5s for complete response |
| Use Case | Web applications | WhatsApp, SMS, Slack, etc. |
| Protocol | SSE (text/event-stream) | JSON (application/json) |
| Browser Support | Modern browsers | Universal |
| Complexity | Requires SSE client | Simple HTTP request |

## Testing

Test the endpoint using curl:

```bash
# Create new thread
curl -X POST http://localhost:8000/chatkit/complete \
  -H "Content-Type: application/json" \
  -d '{
    "type": "threads.create",
    "params": {
      "input": {
        "content": [{"type": "text", "text": "Hello!"}]
      }
    }
  }'

# Continue conversation (use thread_id from previous response)
curl -X POST http://localhost:8000/chatkit/complete \
  -H "Content-Type: application/json" \
  -d '{
    "type": "threads.add_user_message",
    "params": {
      "thread_id": "THREAD_ID_HERE",
      "input": {
        "content": [{"type": "text", "text": "Tell me more"}]
      }
    }
  }'
```

Or use the Python test script:

```bash
cd backend
python examples/whatsapp_integration.py --test
```

## Troubleshooting

### "No assistant message found" Error
This indicates the agent didn't produce an assistant message. Check:
- Agent configuration is correct
- Tools are functioning properly
- No guardrails blocked the response

### Timeout Errors
If requests timeout:
- Increase client timeout (recommended: 60+ seconds)
- Check agent performance and tool execution time
- Consider optimizing agent prompts for faster responses

### Thread Not Found
If continuing a conversation fails:
- Verify the thread_id is valid and persisted correctly
- Check that the thread hasn't been deleted
- Ensure proper thread_id storage/retrieval

## Future Enhancements

Potential improvements:
- [ ] Add streaming progress callbacks for long-running operations
- [ ] Support for media/attachment responses
- [ ] Webhook-based async processing for very long operations
- [ ] Rate limiting per user/phone number
- [ ] Thread cleanup/archival utilities

## Related Documentation

- [ChatKit Protocol Specification](https://github.com/openai/chatkit-python)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [pywa Documentation](https://pywa.readthedocs.io/)
