"""Run with python main.py from your activated virtual environment."""

from pathlib import Path
import sys

from dotenv import load_dotenv

from claude_client import TailoringError, tailor_resume
from utils import read_input, save_latex

ROOT = Path(__file__).resolve().parent


def main() -> int:
    load_dotenv(ROOT / ".env")  # Existing shell environment takes precedence.
    try:
        resume = read_input(ROOT / "input/resume.tex")
        profile = read_input(ROOT / "input/master_profile.txt", optional=True)
        job = read_input(ROOT / "input/job_description.txt")
        print("Generating tailored resume...", flush=True)
        result = tailor_resume(resume, job, profile)
        print(f"Input tokens: {result.input_tokens}")
        print(f"Output tokens: {result.output_tokens}")
        print(f"Approximate API cost: ${result.estimated_cost_usd:.4f} USD")
        save_latex(ROOT / "output/tailored_resume.tex", result.latex)
    except (TailoringError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Saved to: output/tailored_resume.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
