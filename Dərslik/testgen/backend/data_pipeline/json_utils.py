"""Shared JSON parsing utility for Gemini LLM responses."""
import json
import re


def _recover_truncated_array(text: str) -> list:
    """
    Recover as many complete JSON objects as possible from a truncated array.
    Finds the last complete {...} block and closes the array there.
    """
    # Find the last position of a complete object ending with }
    last_good = -1
    depth = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_str:
            escape = True
            continue
        if ch == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                last_good = i
    if last_good == -1:
        return []
    truncated = text[:last_good + 1]
    # Remove any trailing comma after last object
    truncated = truncated.rstrip().rstrip(',')
    # Wrap in array if needed
    truncated = truncated.strip()
    if not truncated.startswith('['):
        truncated = '[' + truncated
    truncated += ']'
    return json.loads(truncated)


_LATEX_BACKSLASH_RE = re.compile(r'(?<!\\)\\(?=[a-zA-Z])')
# Matches 2+ consecutive backslashes followed by a letter — post-parse, this is
# an over-escaped LaTeX command (e.g. "\\frac" should be "\frac" in KaTeX).
_OVEREXCAPED_LATEX_RE = re.compile(r'\\{2,}(?=[a-zA-Z])')
_MATH_LOOSE_RE = re.compile(r'\\(?:frac|sqrt|pi|sum|int|lim|cdot|times|leq|geq|neq|infty|alpha|beta|gamma|theta|text)')
_VALID_MCQ_KEYS = {"A", "B", "C", "D", "E"}


def _protect_latex_backslashes(text: str) -> str:
    """Gemini often emits LaTeX commands with a single backslash ("\\frac").
    JSON treats \\f \\b \\n \\t \\r \\v as control-char escapes, silently
    corrupting LaTeX (\\frac → FF + "rac"). Double every single backslash that
    directly precedes an ASCII letter so LaTeX commands survive JSON parsing.
    """
    return _LATEX_BACKSLASH_RE.sub(r'\\\\', text)


def _fix_latex_string(s: str) -> str:
    """Normalize LaTeX in a parsed string: collapse 2+ backslashes to 1 before letters,
    and wrap bare LaTeX commands (no $ delimiters) in inline math delimiters.
    """
    if not isinstance(s, str):
        return s
    s = _OVEREXCAPED_LATEX_RE.sub(r'\\', s)
    # If string contains LaTeX commands but no $ delimiters anywhere, wrap whole thing
    if _MATH_LOOSE_RE.search(s) and '$' not in s:
        s = f"${s}$"
    return s


def _walk_and_fix(obj):
    if isinstance(obj, str):
        return _fix_latex_string(obj)
    if isinstance(obj, dict):
        return {k: _walk_and_fix(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk_and_fix(v) for v in obj]
    return obj


def sanitize_question(q: dict) -> dict:
    """Post-parse repair of common Gemini output defects:
    - Over-escaped LaTeX (\\\\frac → \\frac in parsed string)
    - Missing math delimiters in MCQ option values
    - Swapped key/value in options dict (Gemini occasionally inverts one entry)
    - Options keys that aren't A-E
    """
    if not isinstance(q, dict):
        return q

    q = _walk_and_fix(q)

    opts = q.get("options")
    if isinstance(opts, dict) and opts:
        keys = set(opts.keys())

        # Repair swapped entries: find any {text: "X"} pair where X is a single
        # valid letter — that entry is inverted.
        if not keys.issubset(_VALID_MCQ_KEYS):
            repaired: dict[str, str] = {}
            for k, v in opts.items():
                if k in _VALID_MCQ_KEYS:
                    repaired[k] = v if isinstance(v, str) else str(v)
                elif isinstance(v, str) and v.strip().upper() in _VALID_MCQ_KEYS and v.strip().upper() not in repaired:
                    # Swapped pair: value is the letter, key is the text
                    repaired[v.strip().upper()] = k
                # else: silently drop malformed entry
            if repaired:
                opts = repaired
                q["options"] = opts
                keys = set(opts.keys())

        # After repair, correct_answer must reference a valid key
        ca = q.get("correct_answer")
        if isinstance(ca, str) and ca.strip().upper() in _VALID_MCQ_KEYS:
            q["correct_answer"] = ca.strip().upper()

    return q


def parse_llm_json(text: str) -> list | dict:
    """Parse JSON from Gemini, iteratively fixing invalid backslash escapes."""
    if text is None:
        return []
    MAX_FIXES = 500
    # Strip markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    text = _protect_latex_backslashes(text)
    for _ in range(MAX_FIXES):
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            msg = str(e)
            if "Invalid \\escape" in msg:
                pos = e.pos
                text = text[:pos] + "\\" + text[pos:]
            elif "Extra data" in msg:
                text = text[:e.pos]
            elif "Unterminated string" in msg or "Expecting" in msg:
                # Try to recover complete objects from truncated response
                try:
                    return _recover_truncated_array(text)
                except Exception:
                    pass
                # Fallback: simple close
                text = text.rstrip().rstrip(",")
                opens = text.count("[") - text.count("]")
                text += "}" * max(0, text.count("{") - text.count("}"))
                text += "]" * max(0, opens)
                return json.loads(text)
            else:
                raise
    raise json.JSONDecodeError("Too many escape fixes needed", text, 0)
