import asyncio
import html as _html
import json
import re as _re

_SVG_SCRIPT_RE = _re.compile(r"<script[\s\S]*?</script>", _re.IGNORECASE)
_SVG_HANDLER_RE = _re.compile(r'\s+on\w+="[^"]*"', _re.IGNORECASE)


def _sanitize_svg(svg: str) -> str:
    """Strip <script> blocks and inline event handlers from LLM-generated SVG."""
    svg = _SVG_SCRIPT_RE.sub("", svg)
    svg = _SVG_HANDLER_RE.sub("", svg)
    return svg


def export_json(variant_data: dict) -> bytes:
    questions = []
    for item in variant_data["questions"]:
        q = item["question"]
        entry = {
            "order": item["order"],
            "question_type": q.question_type,
            "question_text": q.question_text,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "topic": q.topic,
        }
        if q.options:
            entry["options"] = q.options
        if q.rubric:
            entry["rubric"] = q.rubric
        questions.append(entry)

    result = {
        "title": variant_data["variant"].title,
        "subject": variant_data["variant"].subject,
        "total_questions": variant_data["variant"].total_questions,
        "questions": questions,
    }
    return json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")


def export_text(variant_data: dict) -> str:
    lines = [
        f"# {variant_data['variant'].title}",
        f"Fənn: {variant_data['variant'].subject}",
        f"Sual sayı: {variant_data['variant'].total_questions}",
        "",
    ]
    for item in variant_data["questions"]:
        q = item["question"]
        q_type = getattr(q, 'question_type', 'mcq') or 'mcq'
        lines.append(f"**{item['order']}.** {q.question_text}")
        if q.options and q_type == 'mcq':
            for key, val in q.options.items():
                lines.append(f"   {key}) {val}")
        elif q_type == 'numeric_open':
            lines.append("   [Cavab: ________]")
        elif q_type == 'written_solution':
            lines.append("   [Həlli yazın]")
        lines.append("")

    lines.append("\n--- Cavablar ---\n")
    for item in variant_data["questions"]:
        q = item["question"]
        lines.append(f"{item['order']}. {q.correct_answer}")

    return "\n".join(lines)


_SUBJECT_LABELS = {
    "az_dili": "Azərbaycan dili",
    "riyaziyyat": "Riyaziyyat",
    "ingilis": "İngilis dili",
}


def _esc(s: str) -> str:
    """HTML-escape plain text while preserving `$...$` math delimiters.

    KaTeX auto-render needs the dollar signs intact, but all other special
    characters must be escaped to prevent HTML injection from question text.
    """
    return _html.escape(s or "", quote=False)


def _build_html(variant_data: dict) -> str:
    v = variant_data["variant"]
    subject_label = _SUBJECT_LABELS.get(v.subject, v.subject)

    written_count = sum(
        1 for item in variant_data["questions"]
        if getattr(item["question"], "question_type", "") == "written_solution"
    )
    question_blocks = []
    written_header_shown = False
    for item in variant_data["questions"]:
        q = item["question"]
        order = item["order"]
        q_type = getattr(q, 'question_type', 'mcq') or 'mcq'
        # Fix missing \n bug -> HTML doesn't respect \n unless it's <br>
        # JSON loaders might give lit \n or literal slash-n, replacing both.
        qtext = _esc(q.question_text).replace("\\n", "<br>").replace("\n", "<br>")
        body_html = ""
        
        svg_html = ""
        image_svg = getattr(q, 'image_svg', None)
        if image_svg:
            svg_html = f'<div class="q-svg">{_sanitize_svg(image_svg)}</div>'

        if q.options and q_type == 'mcq':
            rows = "".join(
                f'<div class="opt"><span class="opt-key">{_esc(k)})</span> '
                f'<span class="opt-val">{_esc(val)}</span></div>'
                for k, val in q.options.items()
            )
            body_html = f'<div class="opts">{rows}</div>'
        elif q_type == 'numeric_open':
            body_html = '<div class="answer-box">Cavab: ____________</div>'
        elif q_type == 'written_solution':
            body_html = '<div class="answer-box written">Həlli yazın:</div>'

        # Section header before the first written_solution question
        if q_type == 'written_solution' and not written_header_shown:
            written_header_shown = True
            last_written = order + written_count - 1
            header_text = f'{order} - {last_written} sayl\u0131 tap\u015f\u0131r\u0131qlar\u0131 \u201cCavab v\u0259r\u0259ql\u0259ri\u201dnd\u0259 cavabland\u0131r\u0131n.'
            question_blocks.append(f'<div class=”section-header”>{header_text}</div>')

        question_blocks.append(
            f'<div class="q">'
            f'<div class="q-head"><span class="q-num">{order}.</span> '
            f'<span class="q-text">{qtext}</span></div>'
            f'{svg_html}'
            f'{body_html}'
            f'</div>'
        )

    answer_items = "".join(
        f'<li class="{"a-written" if getattr(item["question"], "question_type", "") == "written_solution" else ""}">'
        f'<span class="a-num">{item["order"]}.</span> '
        f'<span class="a-val">{_esc(item["question"].correct_answer)}</span></li>'
        for item in variant_data["questions"]
    )

    return f"""<!DOCTYPE html>
<html lang="az">
<head>
<meta charset="utf-8">
<title>{_esc(v.title)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1e293b;
    font-size: 11pt;
    line-height: 1.55;
    padding: 0 18mm;
  }}
  header {{ border-bottom: 2px solid #0f172a; padding: 18px 0 10px; margin-bottom: 18px; }}
  h1 {{ font-size: 18pt; margin: 0 0 4px; font-weight: 800; }}
  .meta {{ color: #64748b; font-size: 10pt; }}
  .q {{ margin-bottom: 14px; page-break-inside: avoid; }}
  .q-head {{ font-weight: 500; }}
  .q-num {{ font-weight: 700; color: #0f172a; margin-right: 4px; }}
  .opts {{ margin: 6px 0 0 22px; }}
  .opt {{ margin: 3px 0; }}
  .opt-key {{ font-weight: 600; color: #334155; margin-right: 4px; }}
  .answers {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #cbd5e1; page-break-before: auto; }}
  .answers h2 {{ font-size: 13pt; margin: 0 0 10px; font-weight: 700; }}
  .answers ol {{ list-style: none; margin: 0; padding: 0; columns: 3; column-gap: 24px; }}
  .answers li.a-written {{ column-span: all; break-inside: avoid; }}
  .answers li {{ break-inside: avoid; margin: 2px 0; font-size: 10pt; }}
  .a-num {{ color: #64748b; margin-right: 4px; }}
  .a-val {{ font-weight: 600; }}
  .answer-box {{ border: 1.5px dashed #94a3b8; border-radius: 6px; padding: 10px 14px; margin: 8px 0 0 22px; color: #64748b; font-size: 10pt; }}
  .answer-box.written {{ min-height: 100px; }}
  .section-header {{ text-align: center; font-weight: 800; font-size: 13pt; margin: 30px 0 20px; padding-bottom: 5px; border-bottom: 2px solid #0f172a; }}
  .q-svg {{ margin: 15px 0; text-align: center; }}
  .q-svg svg {{ max-width: 100%; max-height: 250px; width: auto; height: auto; }}
  /* KaTeX sizing — match site */
  .katex {{ font-size: 1.05em; }}
  @page {{ size: A4; margin: 16mm 0; }}
</style>
</head>
<body>
  <header>
    <h1>{_esc(v.title)}</h1>
    <div class="meta">{subject_label} · {v.total_questions} sual</div>
  </header>
  <div class="questions">
    {''.join(question_blocks)}
  </div>
  <div class="answers">
    <h2>Cavablar</h2>
    <ol>{answer_items}</ol>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{left: '$$', right: '$$', display: true}},
          {{left: '$', right: '$', display: false}}
        ],
        throwOnError: false,
        strict: false
      }});
      document.body.setAttribute('data-katex-ready', '1');
    }});
  </script>
</body>
</html>"""


async def export_pdf(variant_data: dict) -> bytes:
    from playwright.async_api import async_playwright

    html = _build_html(variant_data)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            # Wait for KaTeX auto-render to finish marking the body
            await page.wait_for_selector("body[data-katex-ready='1']", timeout=15000)
            # Ensure all webfonts (especially KaTeX math fonts) are fully loaded before rendering
            await page.evaluate("document.fonts.ready")
            pdf = await page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
            )
        finally:
            await browser.close()
    return pdf


def _build_markdown(variant_data: dict) -> str:
    v = variant_data["variant"]
    subject_label = _SUBJECT_LABELS.get(v.subject, v.subject)
    lines = [
        f"# {v.title}",
        "",
        f"**Fənn:** {subject_label} · **Sual sayı:** {v.total_questions}",
        "",
        "---",
        "",
    ]
    for item in variant_data["questions"]:
        q = item["question"]
        q_type = getattr(q, 'question_type', 'mcq') or 'mcq'
        lines.append(f"**{item['order']}.** {q.question_text}")
        lines.append("")
        if q.options and q_type == 'mcq':
            for k, val in q.options.items():
                lines.append(f"- **{k})** {val}")
            lines.append("")
        elif q_type == 'numeric_open':
            lines.append("*Cavab: ________*")
            lines.append("")
        elif q_type == 'written_solution':
            lines.append("*Həllini yazın:*")
            lines.append("")

    lines.append("")
    lines.append("## Cavablar")
    lines.append("")
    for item in variant_data["questions"]:
        q = item["question"]
        lines.append(f"{item['order']}\\. {q.correct_answer}  ")

    return "\n".join(lines)


async def export_word(variant_data: dict) -> bytes:
    """Pandoc converts markdown (with `$...$` LaTeX) to docx with native OMML equations."""
    markdown = _build_markdown(variant_data)
    proc = await asyncio.create_subprocess_exec(
        "pandoc",
        "-f", "markdown+tex_math_dollars",
        "-t", "docx",
        "-o", "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=markdown.encode("utf-8"))
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed: {stderr.decode('utf-8', errors='replace')}")
    return stdout
