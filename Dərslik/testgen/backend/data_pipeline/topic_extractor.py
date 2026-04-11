import asyncio
from pathlib import Path

from google import genai
from google.genai import types
import fitz

from data_pipeline.json_utils import parse_llm_json

LLM_MODEL = "gemini-3-flash-preview"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 10


def extract_mini_pdf(pdf_path: str, pdf_page_start: int, pdf_page_end: int) -> bytes:
    """Extract specific pages from PDF into a new mini PDF. Returns bytes."""
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()  # empty PDF
    
    for pg in range(pdf_page_start - 1, pdf_page_end):
        if pg < len(doc):
            new_doc.insert_pdf(doc, from_page=pg, to_page=pg)
            
    pdf_bytes = new_doc.tobytes()
    new_doc.close()
    doc.close()
    
    return pdf_bytes


class TopicExtractor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def extract_topic(self, pdf_bytes: bytes, topic_name: str) -> dict:
        """Send mini PDF to Gemini and extract structured text content."""
        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        
        prompt = f"""Bu PDF Azərbaycan dərsliyindən kiçik bir hissədir. Mövzu: "{topic_name}"

Bu səhifələrdəki BÜTÜN mətni təfərrüatlı şəkildə çıxar ki, tələbələrə sual hazırlamaq üçün kontekst kimi istifadə oluna bilsin:
- Hər riyaziyyat formulunu LaTeX formatında ($...$ və ya $$...$$ içində) yaz
- Skan olunmuş və ya görünən bütün Şəkilləri/diaqramları [ŞƏKİL: təsvir] formatında qeyd et
- Cədvəlləri oxunaqlı və düzgün strukturla yaz
- İçindəki tapşırıqları/nümunələri (Öyrənmə tapşırıqları, Nümunə) mütləq saxla

JSON formatında qaytar:
{{
  "topic": "{topic_name}",
  "text_content": "Bütün fəsil mətni burda...",
  "formulas": ["$x^2$", ...],
  "has_images": true/false,
  "image_descriptions": ["1-ci şəkil diaqramdır...", ...],
  "key_concepts": ["açıq söz1", ...]
}}"""

        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.aio.models.generate_content(
                    model=LLM_MODEL,
                    contents=[pdf_part, prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                return parse_llm_json(response.text)
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"      Retry {attempt + 1}/{MAX_RETRIES} after {delay}s: {e}", flush=True)
                    await asyncio.sleep(delay)
                else:
                    print(f"      Failed to extract topic '{topic_name}': {e}")
                    # Return empty default so pipeline doesn't crash
                    return {"topic": topic_name, "text_content": "", "formulas": [], "has_images": False, "image_descriptions": [], "key_concepts": []}
