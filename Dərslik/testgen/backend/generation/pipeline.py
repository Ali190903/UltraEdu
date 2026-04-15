import logging
import re
import time

from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.prompts import BLOOM_MAP

logger = logging.getLogger("testgen.pipeline")

_VALID_MCQ_KEYS = {"A", "B", "C", "D", "E"}
# Forbidden calculus keywords for grade-11 buraxılış math. Detected in question
# text + explanation; if hit, reject the question as out-of-scope.
_CALCULUS_RE = re.compile(
    r"(törəmə|diferensial|inteqral|ibtidai funksiya|"
    r"maksimum həcm|minimum həcm|ekstremum|əyrinin toxunanı|"
    r"artım sürəti|törəmənin tətbiqi|optimallaşdırma|"
    r"V'\(|S'\(|f'\(|y'\(|\\int|\\frac\{d[A-Za-z]\}\{d[A-Za-z]\})",
    re.IGNORECASE,
)


def _structural_check(question: dict, subject: str, grade: int, question_type: str = "mcq") -> tuple[bool, str]:
    """Fast programmatic validation before the expensive LLM validator.
    Returns (ok, reason). Catches Gemini output defects the model can't spot.
    """
    if not isinstance(question, dict):
        return False, "question is not a dict"

    qtext = question.get("question_text")
    if not isinstance(qtext, str) or not qtext.strip():
        return False, "empty question_text"

    opts = question.get("options")
    if question_type == "mcq":
        if opts is None or not isinstance(opts, dict) or not opts:
            return False, "options must be a non-empty dict for MCQ"
        keys = set(opts.keys())
        if keys != _VALID_MCQ_KEYS:
            return False, f"options keys must be exactly A-E, got {sorted(keys)}"
        for k, v in opts.items():
            if not isinstance(v, str) or not v.strip():
                return False, f"option {k} is empty"
        ca = question.get("correct_answer")
        if not (isinstance(ca, str) and ca.strip().upper() in _VALID_MCQ_KEYS):
            return False, f"correct_answer must be one of A-E, got {ca!r}"
    elif question_type in ("numeric_open", "written_solution"):
        if opts is not None:
            return False, f"options must be null for {question_type}"
        ca = question.get("correct_answer")
        if not (isinstance(ca, str) and ca.strip()):
            return False, "correct_answer must be a non-empty string"
        if question_type == "written_solution":
            rubric = question.get("rubric")
            if rubric is None or not isinstance(rubric, dict) or not rubric:
                return False, "rubric must be a non-empty dict for written_solution"
            if "1 bal" not in rubric or "0 bal" not in rubric:
                return False, "rubric must contain '1 bal' and '0 bal' keys"

    if subject == "riyaziyyat" and grade == 11:
        blob = f"{qtext}\n{question.get('explanation', '')}"
        if _CALCULUS_RE.search(blob):
            return False, "uses calculus/optimization (out of buraxılış scope)"

    return True, ""


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

        textbook_count = len(context["textbook_context"])
        dim_count = len(context["dim_examples"])
        logger.info(
            "[retrieval] subject=%s grade=%s topic=%r textbook_chunks=%d dim_examples=%d took=%.2fs",
            subject, grade, topic, textbook_count, dim_count, retrieval_time,
        )
        if textbook_count == 0:
            logger.warning(
                "[retrieval] NO textbook chunks for subject=%s grade=%s topic=%r — RAG context is empty",
                subject, grade, topic,
            )

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

            # Stage 3A (fast): structural validation — reject malformed output
            # immediately to avoid burning an LLM validation call on garbage.
            struct_ok, struct_reason = _structural_check(question, subject, grade, question_type)
            if not struct_ok:
                logger.info(
                    "[attempt %d/%d] topic=%r STRUCTURAL FAIL: %s — retrying",
                    attempt, self.max_attempts, topic, struct_reason,
                )
                validation = {
                    "answer_correct": False,
                    "textbook_aligned": False,
                    "original": False,
                    "bloom_accurate": False,
                    "grammar_quality": False,
                    "passed": False,
                    "feedback": f"Structural defect: {struct_reason}",
                    "similarity_score": 0.0,
                }
                validation_time = 0.0
                if attempt < self.max_attempts:
                    continue
            else:
                # Stage 3B: Validation (similarity + LLM review)
                val_start = time.time()
                validation = await self.validator.validate(
                    question=question,
                    textbook_context=context["textbook_context"],
                    bloom_level=bloom_level,
                )
                validation_time = time.time() - val_start

            logger.info(
                "[attempt %d/%d] topic=%r passed=%s similarity=%.3f feedback=%r",
                attempt, self.max_attempts, topic,
                validation.get("passed"),
                validation.get("similarity_score", 0.0),
                validation.get("feedback", "")[:120],
            )

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
        logger.warning(
            "[pipeline] ALL %d attempts failed for topic=%r difficulty=%s — question will be dropped by caller",
            self.max_attempts, topic, difficulty,
        )
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