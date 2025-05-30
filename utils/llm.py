from typing import Optional, List
import openai
from openai import AsyncOpenAI

class OpenAIClient:
    """A class to handle OpenAI API requests."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", max_tokens: int = 4096):
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model to use for completions
            max_tokens: Maximum number of tokens in response
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.auto_max_tokens = False

    async def aask(self, prompt: str, system_msgs: Optional[List[str]] = None) -> str:
        """Ask a question to the OpenAI model.

        Args:
            prompt: The prompt to send to the model
            system_msgs: Optional list of system messages

        Returns:
            The model's response
        """
        messages = []
        
        # Add system messages if provided
        if system_msgs:
            for msg in system_msgs:
                messages.append({"role": "system", "content": msg})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=None if self.auto_max_tokens else self.max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "" 