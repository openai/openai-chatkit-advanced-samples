from chatkit.agents import ThreadItemConverter
from chatkit.types import HiddenContextItem
from openai.types.responses import ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message


class CustomerSupportThreadItemConverter(ThreadItemConverter):
    async def hidden_context_to_input(self, item: HiddenContextItem):
        return Message(
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=item.content,
                )
            ],
            role="user",
        )
