"""Claude API"""

import os
from dataclasses import dataclass

import anthropic

from prompts import SYSTEM_PROMPT, build_user_message

#Update model and prices together. Standard USD per million tokens, checked
# https://platform.claude.com/docs/en/about-claude/pricing
MODEL = "claude-sonnet-5-5"
MAX_OUTPUT_TOKENS = 16384  # Includes the model's thinking and final text.
INPUT_PRICE_PER_MILLION = 2.00
OUTPUT_PRICE_PER_MILLION = 10.00


class TailoringError(RuntimeError):
    pass


@dataclass(frozen=True)
class TailoringResult:
    latex: str
    input_tokens: int
    output_tokens: int

    def estimated_cost_usd(self) -> float:
        return (self.input_tokens * INPUT_PRICE_PER_MILLION
                + self.output_tokens * OUTPUT_PRICE_PER_MILLION) / 1_000_000


def tailor_resume(
    resume: str, job_description: str, master_profile: str = "",
) -> TailoringResult:
    """Generate LaTeX and usage. Caller handles validation and persistence."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key or api_key == "your_key_here":
        raise TailoringError(
            "ANTHROPIC_API_KEY is missing or still set to your_key_here. "
            "Save your real key in the .env file next to main.py (not .env.example)."
        )
    if not resume.strip() or not job_description.strip():
        raise TailoringError("The base resume and job description must not be empty.")

    try:
        with anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=2) as client:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                output_config={"effort": "medium"},
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_message(
                    resume, master_profile, job_description,
                )}],
            )
    except anthropic.AuthenticationError as exc:
        raise TailoringError("Anthropic rejected the API key. Check ANTHROPIC_API_KEY.") from exc
    except anthropic.RateLimitError as exc:
        raise TailoringError("Anthropic rate limit reached. Try again later.") from exc
    except anthropic.APIConnectionError as exc:
        raise TailoringError("Could not reach Anthropic (connection or timeout). Try again.") from exc
    except anthropic.APIStatusError as exc:
        raise TailoringError(
            f"Anthropic returned HTTP {exc.status_code}. Check model access, billing, "
            "and request limits in the Anthropic console."
        ) from exc
    except anthropic.APIError as exc:
        raise TailoringError("Anthropic SDK request failed. Check your SDK and configuration.") from exc

    if response.stop_reason != "end_turn":
        raise TailoringError(
            f"Claude did not finish normally ({response.stop_reason}). "
            "No output saved. If truncated, increase MAX_OUTPUT_TOKENS."
        )
    latex = "\n".join(block.text for block in response.content if block.type == "text")
    return TailoringResult(latex, response.usage.input_tokens, response.usage.output_tokens)
