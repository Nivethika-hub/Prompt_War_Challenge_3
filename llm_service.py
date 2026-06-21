"""LLM communication service for the multi-agent sustainability application."""

from __future__ import annotations

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq, GroqError


logger = logging.getLogger(__name__)


class LLMService:
    """Small service wrapper responsible only for talking to the Groq LLM API.

    The service is dependency-injection friendly: pass a preconfigured Groq
    client during tests or when wiring a larger application. If no client is
    provided, the service creates one using the GROQ_API_KEY environment value.
    """

    def __init__(
        self,
        client: Optional[Groq] = None,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> None:
        """Initialize the LLM service.

        Args:
            client: Optional preconfigured Groq client.
            api_key: Optional API key. If omitted, GROQ_API_KEY is used.
            model: Groq model name to use for completions.
            temperature: Sampling temperature for response creativity.
            max_tokens: Maximum number of tokens to generate.

        Raises:
            ValueError: If no API key is available when creating a client.
        """
        load_dotenv()

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if client is not None:
            self.client = client
            return

        resolved_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not resolved_api_key:
            raise ValueError("GROQ_API_KEY is not set. Add it to your environment or .env file.")

        self.client = Groq(api_key=resolved_api_key)

    def generate_response(self, prompt: str) -> str:
        """Generate a text response for the given prompt.

        Args:
            prompt: The user prompt to send to the Groq model.

        Returns:
            The generated text. Returns an empty string if the API call fails.
        """
        if not prompt.strip():
            logger.warning("Received an empty prompt.")
            return ""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            message = completion.choices[0].message.content
            return message.strip() if message else ""

        except GroqError as error:
            logger.exception("Groq API request failed: %s", error)
            return ""
        except Exception as error:
            logger.exception("Unexpected LLM service error: %s", error)
            return ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    llm_service = LLMService()
    response = llm_service.generate_response("Hello")
    print(response)
