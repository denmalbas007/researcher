from abc import ABC
from typing import Any, Optional

from pydantic import BaseModel, Field

class Action(BaseModel, ABC):
    """Base class for all actions."""
    name: str = ""
    i_context: Optional[str] = None
    desc: str = ""
    llm: Any = Field(default=None, exclude=True)
    config: Any = Field(default=None, exclude=True)
    system_text: Optional[str] = None

    async def _aask(self, prompt: str, system_msgs: list[str] = None) -> str:
        """Ask the LLM a question."""
        if not self.llm:
            raise ValueError("LLM not set")
        return await self.llm.aask(prompt, system_msgs)

    async def run(self, *args, **kwargs) -> Any:
        """Run the action."""
        raise NotImplementedError 