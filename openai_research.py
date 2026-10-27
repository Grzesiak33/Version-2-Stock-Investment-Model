"""Optional OpenAI research commentary. No order permissions, no credentials in output."""
from __future__ import annotations
import json
import os
from urllib.request import Request, urlopen

def analyze(rows: list[dict], errors: list[tuple[str, str]]) -> str:
    """Ground a concise research note ONLY in supplied scanner observations.

    An absent API key skips analysis without breaking the stock scanner.
    """
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return "OpenAI commentary not enabled: add OPENAI_API_KEY as a GitHub Actions secret. Quantitative scanner remains operational."
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {
        "model": model,
        "max_output_tokens": 600,
        "instructions": (
            "You are a cautious equity research assistant. Use ONLY the supplied JSON observations. "
            "Never invent headlines, earnings, market prices, news, catalysts, sentiment, analyst targets, "
            "probabilities or predictions. Distinguish past returns from forecasts. "
            "Mention that observations are historical and data may be delayed. "
            "Identify 2-3 research candidates with specific metric-based reasons and downside risks. "
            "A screen score is not a probability or buy signal. "
            "Do not recommend order execution, trade size, leverage, or guaranteed returns. "
            "Limit to 250 words."
        ),
        "input": "Provide a grounded watchlist research note for these observations: " + json.dumps(
            {"observations": rows, "data_errors": errors}, allow_nan=False
        ),
        "store": False,
    }
    req = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=25) as response:
        result = json.load(response)
    parts = []
    for item in result.get("output", []):
        if item.get("type") == "message":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    parts.append(block.get("text", ""))
    note = "\n".join(parts).strip()
    if not note:
        raise RuntimeError("OpenAI returned no commentary")
    return note
