"""Small UTF-8 file helpers and conservative LaTeX checks."""

import os
from pathlib import Path
import re
import tempfile


def read_input(path: Path, *, optional: bool = False) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        if optional:
            return ""
        raise ValueError(f"Missing input: {path}") from None
    if not optional and not content.strip():
        raise ValueError(f"Input is empty: {path}. Add your content before running.")
    return content


def clean_and_validate_latex(text: str) -> str:
    """Remove only an outer Markdown fence; reject obvious non-documents."""
    text = text.strip()
    fenced = re.fullmatch(r"```(?:latex|tex)?[ \t]*\r?\n(.*?)\r?\n```", text,
                          flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    if not text:
        raise ValueError("Claude returned empty content; previous output preserved.")
    # Ignore comments for checks only; never change the saved LaTeX this way.
    visible = re.sub(r"(?<!\\)%[^\n]*", "", text).strip()
    pattern = r"\\documentclass(?:\s*\[[^\]]*\])?\s*\{[^{}]+\}"
    if not re.match(pattern, visible):
        raise ValueError("Response looks like prose or incomplete LaTeX: expected \\documentclass.")
    begin = re.search(r"\\begin\s*\{document\}", visible)
    end = re.search(r"\\end\s*\{document\}\s*$", visible)
    if not begin or not end or begin.end() >= end.start():
        raise ValueError("Response lacks a complete, non-empty LaTeX document environment.")
    return text + "\n"


def save_latex(path: Path, text: str) -> None:
    """Validate, then atomically replace the destination on the same filesystem."""
    latex = clean_and_validate_latex(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(latex)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
