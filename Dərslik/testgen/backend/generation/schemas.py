from pydantic import BaseModel


class GenerateRequest(BaseModel):
    subject: str
    grade: int
    topic: str
    difficulty: str  # easy, medium, hard
    question_type: str = "mcq"  # mcq, matching, open_ended


class GeneratedQuestion(BaseModel):
    question_text: str
    options: dict | None = None
    matching_pairs: dict | None = None
    correct_answer: str
    explanation: str
    bloom_level: str
    latex_content: str | None = None
    source_reference: str


class ValidationResult(BaseModel):
    answer_correct: bool
    textbook_aligned: bool
    original: bool
    bloom_accurate: bool
    grammar_quality: bool
    passed: bool
    feedback: str