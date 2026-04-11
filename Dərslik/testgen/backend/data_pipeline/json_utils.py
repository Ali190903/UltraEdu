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


def parse_llm_json(text: str) -> list | dict:
    """Parse JSON from Gemini, iteratively fixing invalid backslash escapes."""
    if text is None:
        return []
    MAX_FIXES = 500
    # Strip markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
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
