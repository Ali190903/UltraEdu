import uuid


class Chunker:
    def __init__(self, max_tokens: int = 1000):
        self.max_tokens = max_tokens

    def chunk_topic(
        self,
        extracted_data: dict,
        chapter: str,
        subject: str,
        grade: int,
        pages: str,
        subtopic: str | None = None
    ) -> list[dict]:
        """Convert a deeply extracted topic JSON into well-sized chunks."""
        chunks = []
        
        full_text = extracted_data.get("text_content", "")
        if not full_text:
            return chunks
        
        has_images = extracted_data.get("has_images", False)
        
        # Combine image descriptions into a single block
        img_descs = extracted_data.get("image_descriptions", [])
        image_desc_str = " ".join(img_descs) if img_descs else None
        
        # Combine formulas as a reference block
        formulas = extracted_data.get("formulas", [])
        latex_str = " ".join(formulas) if formulas else None

        sub_chunks = self._split_text(full_text, self.max_tokens)

        for i, text in enumerate(sub_chunks):
            # Only put the extra rich metadata on the first chunk of the topic
            # so we don't duplicate tokens excessively in Qdrant
            chunks.append({
                "id": str(uuid.uuid4()),
                "subject": subject,
                "grade": grade,
                "chapter": chapter,
                "topic": extracted_data.get("topic", "Unknown"),
                "subtopic": subtopic,
                "pages": pages,
                "text_content": text,
                "has_image": has_images if i == 0 else False,
                "image_description": image_desc_str if i == 0 else None,
                "latex": latex_str if i == 0 else None,
            })

        return chunks

    def _split_text(self, text: str, max_tokens: int) -> list[str]:
        """Split text into chunks of approximately max_tokens (word-based estimate)."""
        words = text.split()
        if len(words) <= max_tokens:
            return [text]

        result = []
        current = []
        count = 0

        for word in words:
            current.append(word)
            count += 1
            if count >= max_tokens:
                result.append(" ".join(current))
                current = []
                count = 0

        if current:
            result.append(" ".join(current))

        return result