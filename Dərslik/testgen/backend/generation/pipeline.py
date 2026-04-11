import time

from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.prompts import BLOOM_MAP


class GenerationPipeline:
    """Orchestrates the 3-stage generation pipeline with retry logic.

    Spec §7.1: Retrieval → Generation → Validation.
    If validation fails, retry Stage 2+3 up to max_attempts.
    """

    def __init__(
        self,
        retrieval: RetrievalStage,
        generator: GenerationStage,
        validator: ValidationStage,
        max_attempts: int = 3,
    ):
        self.retrieval = retrieval
        self.generator = generator
        self.validator = validator
        self.max_attempts = max_attempts

    async def run(
        self,
        subject: str,
        grade: int,
        topic: str,
        difficulty: str,
        question_type: str = "mcq",
    ) -> dict:
        total_start = time.time()

        # Stage 1: Context Retrieval (runs once)
        retrieval_start = time.time()
        context = await self.retrieval.retrieve(
            subject=subject,
            grade=grade,
            topic=topic,
        )
        retrieval_time = time.time() - retrieval_start

        bloom_level = BLOOM_MAP[difficulty]

        for attempt in range(1, self.max_attempts + 1):
            # Stage 2: Generation
            gen_start = time.time()
            question = await self.generator.generate(
                subject=subject,
                grade=grade,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                textbook_context=context["textbook_context"],
                dim_examples=context["dim_examples"],
            )
            generation_time = time.time() - gen_start

            # Stage 3: Validation
            val_start = time.time()
            validation = await self.validator.validate(
                question=question,
                textbook_context=context["textbook_context"],
                bloom_level=bloom_level,
            )
            validation_time = time.time() - val_start

            if validation["passed"]:
                return {
                    "question": question,
                    "validation": validation,
                    "attempts": attempt,
                    "timing": {
                        "retrieval": retrieval_time,
                        "generation": generation_time,
                        "validation": validation_time,
                        "total": time.time() - total_start,
                    },
                }

        # All attempts failed — return last result
        return {
            "question": question,
            "validation": validation,
            "attempts": self.max_attempts,
            "timing": {
                "retrieval": retrieval_time,
                "generation": generation_time,
                "validation": validation_time,
                "total": time.time() - total_start,
            },
        }