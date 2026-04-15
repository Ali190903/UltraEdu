import asyncio
import random
from google import genai
from google.genai import types

LLM_MODEL = "gemini-3-flash-preview"

MAX_RETRIES = 10

RETRYABLE = ("429", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "high demand", "overloaded", "No capacity")


class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _call(self, contents, config: types.GenerateContentConfig, timeout: int = 60) -> str:
        """API call with retry for 503/429 errors."""
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=LLM_MODEL,
                        contents=contents,
                        config=config,
                    ),
                    timeout=timeout,
                )
                if response.text is None:
                    attempt += 1
                    await asyncio.sleep(min(5 * attempt, 20))
                    continue
                return response.text
            except asyncio.TimeoutError:
                attempt += 1
                delay = int(10 * (0.8 + 0.4 * random.random()))
                await asyncio.sleep(delay)
            except Exception as e:
                err = str(e)
                if any(x in err for x in RETRYABLE):
                    attempt += 1
                    base = min(5 * attempt, 30)
                    delay = int(base * (0.8 + 0.4 * random.random()))
                    await asyncio.sleep(delay)
                else:
                    raise
        raise RuntimeError(f"Gemini API failed after {MAX_RETRIES} retries")

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        ) if system_instruction else types.GenerateContentConfig()
        return await self._call(prompt, config)

    async def generate_json(self, prompt: str, system_instruction: str | None = None) -> str:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=system_instruction,
        )
        return await self._call(prompt, config)
