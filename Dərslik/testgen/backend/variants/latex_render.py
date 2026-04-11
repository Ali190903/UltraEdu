"""Render LaTeX formulas to images for PDF/Word export."""
import io
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def latex_to_image(latex: str, fontsize: int = 14, dpi: int = 150) -> bytes:
    """Render a LaTeX expression to PNG bytes."""
    fig, ax = plt.subplots(figsize=(0.01, 0.01))
    ax.axis("off")
    text = ax.text(
        0, 0, f"${latex}$",
        fontsize=fontsize,
        verticalalignment="baseline",
    )
    fig.savefig(
        buf := io.BytesIO(),
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.02,
        transparent=True,
    )
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# Regex: match $$...$$ (display) or $...$ (inline)
_LATEX_RE = re.compile(r"(\$\$[\s\S]+?\$\$|\$[^$]+?\$)")


def split_text_and_latex(text: str) -> list[dict]:
    """Split text into plain text and LaTeX segments.

    Returns list of dicts: {"type": "text"|"latex", "content": str, "display": bool}
    """
    parts = []
    last = 0
    for m in _LATEX_RE.finditer(text):
        if m.start() > last:
            parts.append({"type": "text", "content": text[last:m.start()]})
        raw = m.group()
        if raw.startswith("$$"):
            parts.append({"type": "latex", "content": raw[2:-2], "display": True})
        else:
            parts.append({"type": "latex", "content": raw[1:-1], "display": False})
        last = m.end()
    if last < len(text):
        parts.append({"type": "text", "content": text[last:]})
    return parts
