import anthropic
import base64
import json
import os
from shared.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

LEVEL1_PROMPT = """You are a professional UI/UX design auditor. Analyze the provided screenshot and identify design issues across exactly these five principles:

1. Visual Hierarchy — Are the most important elements clearly dominant? Is there a clear reading order?
2. Contrast (WCAG AA) — Do text and interactive elements meet minimum contrast ratios? Flag any that appear to fail.
3. Spacing — Is whitespace used consistently? Are elements cramped or unevenly spaced?
4. Alignment — Are elements aligned to a clear grid or axis? Flag misaligned elements.
5. Consistency — Are fonts, colors, button styles, and icon sizes consistent throughout?

For each issue found, provide:
- principle: which of the 5 principles is violated
- location: precise description of where on the page (e.g. "top navigation bar", "hero section CTA button", "footer link row")
- issue: what specifically is wrong — be precise, not vague
- user_impact: how this affects the user experience
- recommendation: a specific, actionable fix
- severity: one of critical / high / medium / low / info
- confidence_score: integer 0–100 representing your confidence this is a real issue visible in the image

Return ONLY valid JSON in this exact format:
{
  "findings": [
    {
      "principle": "string",
      "location": "string",
      "issue": "string",
      "user_impact": "string",
      "recommendation": "string",
      "severity": "critical|high|medium|low|info",
      "confidence_score": 0
    }
  ],
  "summary": "One paragraph overall assessment of the design quality"
}

Rules:
- Minimum 3 findings required
- Only report issues you can actually see in the image — no assumptions
- Be specific: 'primary CTA button has same visual weight as secondary action' not 'bad hierarchy'"""


def encode_image(image_path: str) -> tuple[str, str]:
    ext = os.path.splitext(image_path)[1].lower()
    media_type_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    media_type = media_type_map.get(ext, "image/png")
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def run_level1_analysis(image_path: str) -> dict:
    image_data, media_type = encode_image(image_path)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": LEVEL1_PROMPT},
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


LEVEL2_PROMPT = """You are a professional UI/UX design auditor performing a before/after regression analysis.

You will receive two screenshots:
- Image 1 (BEFORE): the baseline / original design
- Image 2 (AFTER): the current / updated design

Compare them carefully and identify every visual difference. For each difference provide:
- change_type: short label for the type of change (e.g. "Color change", "Font size", "Layout shift")
- location: where on the page
- description: what exactly changed
- direction: "improvement", "regression", or "neutral"
- reasoning: why you classified it as improvement/regression/neutral
- user_impact: how this change affects the user experience
- severity: critical / high / medium / low / info
- confidence_score: integer 0–100
- accessibility_regression: true if this change reduces contrast, font size, or touch target size

Return ONLY valid JSON:
{
  "findings": [
    {
      "change_type": "string",
      "location": "string",
      "description": "string",
      "direction": "improvement|regression|neutral",
      "reasoning": "string",
      "user_impact": "string",
      "severity": "critical|high|medium|low|info",
      "confidence_score": 0,
      "accessibility_regression": false
    }
  ],
  "improvements_count": 0,
  "regressions_count": 0,
  "neutral_count": 0,
  "overall_verdict": "improved|degraded|unchanged",
  "summary": "One paragraph overall assessment of what changed and the net impact"
}

Rules:
- Minimum 5 differences required
- Only report differences you can actually see between the two images
- Be specific about what changed"""


def run_level2_analysis(baseline_path: str, current_path: str) -> dict:
    baseline_data, baseline_media = encode_image(baseline_path)
    current_data, current_media = encode_image(current_path)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Image 1 (BEFORE — baseline):"},
                    {"type": "image", "source": {"type": "base64", "media_type": baseline_media, "data": baseline_data}},
                    {"type": "text", "text": "Image 2 (AFTER — current):"},
                    {"type": "image", "source": {"type": "base64", "media_type": current_media, "data": current_data}},
                    {"type": "text", "text": LEVEL2_PROMPT},
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

