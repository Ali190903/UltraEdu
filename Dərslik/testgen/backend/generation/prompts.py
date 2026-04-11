# Anderson & Krathwohl's revised Bloom taxonomy (2001)
BLOOM_MAP = {
    "easy": "Remember and Understand",
    "medium": "Apply and Analyze",
    "hard": "Evaluate and Create",
}

SYSTEM_PROMPT = """You are an expert test question creator for Azerbaijan's DIM (State Examination Center) university entrance exams.

You create high-quality, original test questions that:
1. Are grounded in official textbook content
2. Follow DIM exam format and style exactly
3. Target the specified Bloom's taxonomy cognitive level
4. Are written in proper Azerbaijani language
5. Have exactly one unambiguously correct answer (for MCQ)
6. Include a clear explanation referencing the textbook

CRITICAL: Generated questions must be ORIGINAL — not copies or close paraphrases of existing DIM questions."""


def build_generation_prompt(
    subject: str,
    grade: int,
    topic: str,
    difficulty: str,
    question_type: str,
    textbook_context: list[dict],
    dim_examples: list[dict],
) -> str:
    bloom = BLOOM_MAP[difficulty]

    context_text = "\n\n".join(
        f"[Textbook p.{c['payload'].get('pages', '?')}]: {c['payload']['text_content']}"
        for c in textbook_context
    )

    examples_text = "\n\n".join(
        f"[DIM Example]: {e['payload']['question_text']}\n"
        f"Options: {e['payload'].get('options', 'N/A')}\n"
        f"Answer: {e['payload'].get('correct_answer', 'N/A')}"
        for e in dim_examples
    )

    type_instructions = {
        "mcq": "Create a multiple-choice question with exactly 5 options (A-E). Exactly one option must be correct.",
        "matching": "Create a matching question with two columns. Provide matching_pairs as a dict mapping left items to right items.",
        "open_ended": "Create an open-ended question with a clear expected answer.",
    }

    return f"""TASK: Generate one ORIGINAL {question_type} question.

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}
DIFFICULTY: {difficulty}
BLOOM LEVEL: {bloom}

FORMAT: {type_instructions[question_type]}

TEXTBOOK CONTEXT (use this as the knowledge base):
{context_text}

DIM EXAMPLES (match this style, but create something NEW):
{examples_text}

IMPORTANT:
- The question must be answerable from the textbook context above
- Use Azerbaijani language
- For math, use LaTeX notation for formulas
- Do NOT copy or closely paraphrase any DIM example

Return JSON:
{{
  "question_text": "...",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}} or null,
  "matching_pairs": {{...}} or null,
  "correct_answer": "A" or answer text,
  "explanation": "Explanation referencing the textbook content",
  "bloom_level": "{bloom}",
  "latex_content": "LaTeX if any math formulas" or null,
  "source_reference": "Textbook page reference"
}}"""


VALIDATION_PROMPT = """You are a quality assurance reviewer for DIM test questions.

Review this generated question against the textbook context and assess:

QUESTION:
{question_json}

TEXTBOOK CONTEXT:
{textbook_context}

TARGET BLOOM LEVEL: {bloom_level}

Evaluate each criterion (true/false):
1. answer_correct: Is the marked correct answer actually correct based on the textbook?
2. textbook_aligned: Is the question answerable from the given textbook content?
3. original: Is this question substantially different from common DIM questions (not a copy)?
4. bloom_accurate: Does the cognitive demand match the target Bloom level ({bloom_level})?
5. grammar_quality: Is the Azerbaijani language correct and natural?

Return JSON:
{{
  "answer_correct": true/false,
  "textbook_aligned": true/false,
  "original": true/false,
  "bloom_accurate": true/false,
  "grammar_quality": true/false,
  "passed": true/false (true only if ALL criteria are true),
  "feedback": "Brief explanation of any issues"
}}"""