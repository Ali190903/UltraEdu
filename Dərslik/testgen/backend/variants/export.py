import asyncio
import html as _html
import json


def export_json(variant_data: dict) -> bytes:
    questions = []
    for item in variant_data["questions"]:
        q = item["question"]
        questions.append({
            "order": item["order"],
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "topic": q.topic,
        })

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
        lines.append(f"**{item['order']}.** {q.question_text}")
        if q.options:
            for key, val in q.options.items():
                lines.append(f"   {key}) {val}")
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

    question_blocks = []
    for item in variant_data["questions"]:
        q = item["question"]
        order = item["order"]
        qtext = _esc(q.question_text)
        opts_html = ""
        if q.options:
            rows = "".join(
                f'<div class="opt"><span class="opt-key">{_esc(k)})</span> '
                f'<span class="opt-val">{_esc(val)}</span></div>'
                for k, val in q.options.items()
            )
            opts_html = f'<div class="opts">{rows}</div>'
        question_blocks.append(
            f'<div class="q">'
            f'<div class="q-head"><span class="q-num">{order}.</span> '
            f'<span class="q-text">{qtext}</span></div>'
            f'{opts_html}'
            f'</div>'
        )

    answer_items = "".join(
        f'<li><span class="a-num">{item["order"]}.</span> '
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
  .answers li {{ break-inside: avoid; margin: 2px 0; font-size: 10pt; }}
  .a-num {{ color: #64748b; margin-right: 4px; }}
  .a-val {{ font-weight: 600; }}
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
        lines.append(f"**{item['order']}.** {q.question_text}")
        lines.append("")
        if q.options:
            for k, val in q.options.items():
                lines.append(f"- **{k})** {val}")
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
