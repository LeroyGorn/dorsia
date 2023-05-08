from typing import Any, Dict, List

from langchain.memory import ChatMessageHistory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import get_buffer_string


class ConversationBufferMemory(BaseChatMemory):
    """Buffer for storing conversation memory."""

    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    memory_key: str = "history"  #: :meta private:

    def __init__(self, memory_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if memory_data is not None:
            self.chat_memory = ChatMessageHistory(
                messages=memory_data,
                output_key=self.output_key,
                input_key=self.input_key,
                return_messages=self.return_messages,
                human_prefix=self.human_prefix,
                ai_prefix=self.ai_prefix,
                memory_key=self.memory_key
            )

    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        if self.return_messages:
            return self.chat_memory.messages
        else:
            return get_buffer_string(
                self.chat_memory.messages,
                human_prefix=self.human_prefix,
                ai_prefix=self.ai_prefix,
            )

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        return {self.memory_key: self.buffer}
