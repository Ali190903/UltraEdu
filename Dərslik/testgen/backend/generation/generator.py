from core.gemini_client import GeminiClient
from generation.prompts import SYSTEM_PROMPT, build_generation_prompt
from data_pipeline.json_utils import parse_llm_json, sanitize_question


class GenerationStage:
    """Stage 2: Generate a question using Gemini with structured JSON output."""

    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini

    async def generate(
        self,
        subject: str,
        grade: int,
        topic: str,
        difficulty: str,
        question_type: str,
        textbook_context: list[dict],
        dim_examples: list[dict],
    ) -> dict:
        prompt = build_generation_prompt(
            subject=subject,
            grade=grade,
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            textbook_context=textbook_context,
            dim_examples=dim_examples,
        )

        response = await self.gemini.generate_json(
            prompt, system_instruction=SYSTEM_PROMPT
        )
        parsed = parse_llm_json(response)
        if isinstance(parsed, list):
            if not parsed:
                raise ValueError("Gemini returned empty JSON array — no question generated")
            parsed = parsed[0]
        if not isinstance(parsed, dict):
            raise ValueError(f"Gemini returned non-dict JSON: {type(parsed).__name__}")
        return sanitize_question(parsed)
