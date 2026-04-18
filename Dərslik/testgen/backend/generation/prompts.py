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

    # Grade-11 buraxılış math scope: no calculus, no optimization.
    grade_scope_rules = ""
    if subject == "riyaziyyat" and grade == 11:
        grade_scope_rules = (
            "\nCURRICULUM SCOPE (MANDATORY — grade 11 buraxılış imtahanı):\n"
            "- FORBIDDEN topics: derivatives (törəmə), integrals (inteqral), "
            "function extrema/optimization (maksimum/minimum tapma), limits of functions "
            "(f(x) limiti — only numeric sequence limits $\\lim_{n\\to\\infty}$ are allowed), "
            "differential equations. These are NOT in the buraxılış syllabus.\n"
            "- ALLOWED: algebra (polynomials, rational expressions, equations/inequalities), "
            "sequences & series (numeric limits), trigonometry, geometry (triangles, circles, "
            "solids — surface area & volume by direct formulas only), probability, "
            "percentages/ratios, functions (domain/range/composition — NOT derivatives).\n"
            "- STRICT NO PROOF RULE: Buraxılış questions MUST NOT ask the student to prove a formula or theorem ('isbat edin'). "
            "All questions must ask for a final numerical or algebraic calculation/result.\n"
            "- ALWAYS wrap ANY and ALL math variables, angles, degrees, numbers, and formulas inside $...$. "
            "Never leave mathematically meaningful letters or expressions naked. Write '$\\angle BAC$' instead of '\\angle BAC'.\n"
            "- VISUALLY INTENSIVE (SVG RULE): If the question involves geometry, coordinates, sets, or charts, "
            "you MUST generate high-quality, professional SVG code showing the figure in the `image_svg` field. "
            "STRICT SVG REQUIREMENTS: "
            "1. MUST define a clear `viewBox` (e.g., viewBox=\"0 0 300 250\"). "
            "2. Use thick, distinct black lines (stroke=\"black\" stroke-width=\"2.5\" fill=\"transparent\"). "
            "3. Add min 15px padding inside the viewBox so shapes/lines never clip. "
            "4. Add precise `<text>` elements for labels (A, B, r=5, 1.5m) with font-family=\"sans-serif\" font-size=\"16\" font-weight=\"bold\", nicely offset from lines. "
            "5. Ensure paths close perfectly (use 'Z' or exact coordinates) and figures look mathematically proportional.\n"
            "- STRICT NO HALLUCINATIONS: Do NOT write the word 'Situasiya:' or '(şəkildəki kimi)' in the question text! Also, NEVER divide a question into sub-parts like a), b), c). DİM questions are single, direct queries.\n"
            "- If the textbook context contains calculus material, IGNORE it and pick "
            "an allowed concept from the same topic.\n"
        )

    type_instructions = {
        "mcq": (
            "Create a multiple-choice question with exactly 5 options keyed A, B, C, D, E "
            "(exactly these five uppercase letters as JSON keys — never text as key). "
            "Exactly one option must be correct. "
            "Every option value that contains ANY mathematical symbol, variable, or LaTeX "
            "command MUST be wrapped in $...$ delimiters (e.g. \"$x^2$\", \"$4\\\\pi$ m$^3$\"). "
            "Plain numeric-only values like \"10\" or \"6500\" do NOT need delimiters."
        ),
        "matching": (
            "Create a matching question (DIM 'uyğunluğu müəyyən edin' format) with TWO sets of items. "
            "Set 1 (Numbered: 1, 2, 3...): Put these directly INSIDE the `question_text` separated by \\\\n. "
            "Set 2 (Lettered: A, B, C, D, E): Put exactly 5 choices into the `options` object. "
            "Example question_text: 'Uyğunluğu müəyyən edin:\\\\n1. Cüt funksiya\\\\n2. Tək funksiya\\\\n3. Dövrü funksiya'. "
            "Example options: {\"A\": \"y=x^2\", \"B\": \"y=x^3\", \"C\": \"y=sin(x)\", \"D\": \"y=cos(x)\", \"E\": \"y=2^x\"}. "
            "matching_pairs MUST BE null. "
            "correct_answer must map numbers to letters using semicolons (multi-select is allowed). "
            "Example correct_answer: '1-A,D; 2-B; 3-C'."
        ),
        "numeric_open": (
            "Create an open-ended mathematical question where the final answer is a pure numeric value "
            "(integer or decimal/fraction). Important: The correct_answer MUST be just the digits (e.g. '15' or '3/4'). "
            "Do NOT include units or variable names in the correct_answer field. "
            "options MUST be null. matching_pairs MUST be null. rubric MUST be null."
        ),
        "written_solution": (
            "Create a DIM-style open-ended written task. "
            "It may be a single direct calculation (e.g. 'Find the volume of a sphere with radius 3') "
            "OR a multi-step problem — both formats appear in real DIM exams. "
            "The key requirement: the student must SHOW their work/solution steps in writing. "
            "options MUST be null. matching_pairs MUST be null. "
            "You MUST provide a 'rubric' JSON object with at minimum '1 bal' and '0 bal' keys. "
            "Optionally include '1/2 bal' for partial credit. "
            "Example: {{\"1 bal\": \"Tam doğru həll və cavab\", \"1/2 bal\": \"Düzgün metod, hesab səhvi\", \"0 bal\": \"Səhv metod və ya boş\"}}. "
            "The correct_answer field must hold the final numeric or algebraic answer."
        ),
    }

    return f"""TASK: Generate one ORIGINAL {question_type} question.

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}
DIFFICULTY: {difficulty}
BLOOM LEVEL: {bloom}

FORMAT: {type_instructions.get(question_type, "Create an open-ended question.")}
{grade_scope_rules}
TEXTBOOK CONTEXT (use this as the knowledge base):
{context_text}

DIM EXAMPLES (match this style, but create something NEW):
{examples_text}

IMPORTANT:
- The question must be answerable from the textbook context above
- Use Azerbaijani language
- For math formulas, use proper LaTeX notation wrapped in $...$ (inline) or $$...$$ (display)
- Use correct LaTeX commands: \\frac{{a}}{{b}} (NOT rac), \\sqrt{{x}}, \\pi, \\lim, \\sum, \\int, \\infty, \\cdot, \\times, \\leq, \\geq, \\neq
- Example: "$S(t) = \\pi r^2$" or "$$\\frac{{4n-1}}{{n}}$$"

JSON ESCAPING RULES (CRITICAL — read carefully):
- You MUST produce valid JSON. Inside any JSON string value, every literal backslash MUST be written as TWO backslashes (\\\\).
- Therefore every LaTeX command like \\frac, \\pi, \\sqrt MUST be written as \\\\frac, \\\\pi, \\\\sqrt in the JSON output.
- CORRECT: "question_text": "Limiti tapın: $\\\\lim_{{n\\\\to\\\\infty}} \\\\frac{{4n-1}}{{n}}$"
- WRONG (loses \\f, \\n, \\t as control chars): "question_text": "$\\lim \\frac{{4n-1}}{{n}}$"
- Never output a bare single backslash followed by a letter — always double it.

- Do NOT copy or closely paraphrase any DIM example

Return JSON:
{{
  "question_text": "...",
  "image_svg": "<svg>...</svg>" or null,
  "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}} or null,
  "matching_pairs": {{...}} or null,
  "rubric": {{"1 bal": "...", "1/2 bal": "...", "0 bal": "..."}} or null,
  "correct_answer": "...",
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