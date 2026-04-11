from pathlib import Path

from google import genai
from google.genai import types

from data_pipeline.json_utils import parse_llm_json

LLM_MODEL = "gemini-3-flash-preview"
INLINE_PDF_LIMIT = 50 * 1024 * 1024


class TocExtractor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _upload_if_needed(self, path: Path) -> types.Part | object:
        """Return an inline Part for small PDFs, or upload via Files API for large ones."""
        file_bytes = path.read_bytes()
        if len(file_bytes) <= INLINE_PDF_LIMIT:
            return types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        uploaded = await self.client.aio.files.upload(
            file=path, config=types.UploadFileConfig(mime_type="application/pdf")
        )
        return uploaded

    async def extract(self, pdf_path: str) -> list[dict]:
        """Extract table of contents from a textbook PDF."""
        path = Path(pdf_path)
        pdf_content = await self._upload_if_needed(path)

        prompt = """Analyze this textbook PDF and extract its table of contents.
Return a structured JSON array of chapters with their topics:
[{
  "chapter": "Chapter name",
  "chapter_order": 1,
  "topics": [
    {"topic": "Topic name", "subtopic": "Subtopic or null", "page_start": 5, "page_end": 20}
  ]
}]

Be thorough — include all chapters and topics visible in the TOC or inferable from headings."""

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[pdf_content, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text
        return parse_llm_json(text)