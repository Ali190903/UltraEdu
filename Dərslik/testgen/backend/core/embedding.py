import asyncio

from google import genai

EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 3072

MAX_RETRIES = 5
RETRY_BASE_DELAY = 5


class EmbeddingClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def embed(self, text: str) -> list[float]:
        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.aio.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=text,
                )
                return response.embeddings[0].values
            except Exception as e:
                err_str = str(e)
                if attempt < MAX_RETRIES - 1 and ("429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str):
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"      [Embed] Retry {attempt+1}/{MAX_RETRIES} after {delay}s: {err_str[:80]}")
                    await asyncio.sleep(delay)
                else:
                    raise

    async def embed_batch(self, texts: list[str], delay_between: float = 0.5) -> list[list[float]]:
        """Embed texts one by one (serial) to avoid rate limits."""
        results = []
        for i, text in enumerate(texts):
            vec = await self.embed(text)
            results.append(vec)
            if i < len(texts) - 1:
                await asyncio.sleep(delay_between)
        return results