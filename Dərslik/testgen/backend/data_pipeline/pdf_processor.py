"""
PDF text extraction using PyMuPDF (fitz) — completely FREE, no API calls.

PyMuPDF extracts text directly from PDF pages locally.
No Gemini API needed. Instant. Zero cost.

For math formulas: PyMuPDF extracts the unicode text representation.
The chunker preserves this as-is. Gemini can interpret math content
during question generation (Stage 2) where it has the textbook context.
"""
import fitz  # PyMuPDF
from pathlib import Path


class PdfProcessor:
    def __init__(self, api_key: str | None = None):
        # api_key kept for backward compatibility but NOT used
        pass

    def extract_text_sync(self, pdf_path: str, pages: tuple[int, int] | None = None) -> list[dict]:
        """Extract text from PDF using PyMuPDF. FREE, local, instant."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        doc = fitz.open(str(path))
        total_pages = len(doc)

        if pages:
            start, end = pages
        else:
            start, end = 1, total_pages

        all_pages = []
        for pg_num in range(start, end + 1):
            if pg_num > total_pages:
                break
            page = doc[pg_num - 1]  # fitz is 0-indexed
            text = page.get_text("text")

            # Check for images on the page
            images = page.get_images(full=True)
            has_image = len(images) > 0
            image_desc = f"[IMAGE: {len(images)} image(s) on page {pg_num}]" if has_image else None

            all_pages.append({
                "page": pg_num,
                "text": text.strip() if text else "",
                "has_image": has_image,
                "image_description": image_desc,
                "latex": None,  # PyMuPDF extracts unicode math symbols directly
            })

        doc.close()
        return all_pages

    async def extract_text(self, pdf_path: str, pages: tuple[int, int] | None = None) -> list[dict]:
        """Async wrapper — actual work is sync (local file I/O, instant)."""
        return self.extract_text_sync(pdf_path, pages)

    def get_page_count(self, pdf_path: str) -> int:
        """Get exact page count using PyMuPDF."""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count