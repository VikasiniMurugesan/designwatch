import os
import json
import base64
import shutil
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from shared.config import ANTHROPIC_API_KEY, BASELINES_DIR, SCREENSHOTS_DIR

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Pages to scan on the target website
PAGES_TO_SCAN = [
    {"name": "home", "path": "/"},
    {"name": "about", "path": "#whatgpt3"},
    {"name": "features", "path": "#features"},
]

LEVEL3_PROMPT = """You are a UI/UX regression analyst. You are given two screenshots of the same page:
- Image 1 (BEFORE): the stored baseline screenshot
- Image 2 (AFTER): the freshly captured screenshot

Your task is to identify genuine visual regressions — things that broke or degraded.

Ignore dynamic content that is expected to change: timestamps, user session data, loading indicators, animated elements, or any counters.

For each real regression found:
- issue: what broke or degraded
- location: where on the page
- severity: critical / high / medium / low
- confidence_score: 0–100
- evidence: describe specific visual evidence you see in both images

Return ONLY valid JSON:
{
  "regressions": [
    {
      "issue": "string",
      "location": "string",
      "severity": "critical|high|medium|low",
      "confidence_score": 0,
      "evidence": "string"
    }
  ],
  "has_regressions": false,
  "summary": "One paragraph summary of the scan findings"
}

If no regressions found, return an empty regressions list and has_regressions: false."""


def capture_screenshot(url: str, page_name: str, output_dir: str) -> str:
    path = os.path.join(output_dir, f"{page_name}.png")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=path, full_page=False)
        browser.close()
    return path


def encode_image_base64(image_path: str) -> tuple[str, str]:
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, "image/png"


def compare_with_claude(baseline_path: str, current_path: str) -> dict:
    baseline_data, _ = encode_image_base64(baseline_path)
    current_data, _ = encode_image_base64(current_path)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Image 1 (BEFORE — baseline):"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": baseline_data}},
                    {"type": "text", "text": "Image 2 (AFTER — current):"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": current_data}},
                    {"type": "text", "text": LEVEL3_PROMPT},
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


def scan_single_page(page_cfg: dict, target_url: str) -> dict:
    page_name = page_cfg["name"]
    page_path = page_cfg["path"]

    full_url = f"{target_url.rstrip('/')}{page_path}" if not page_path.startswith("#") else f"{target_url.rstrip('/')}/{page_path}"
    baseline_path = os.path.join(BASELINES_DIR, f"{page_name}.png")
    current_path = os.path.join(SCREENSHOTS_DIR, f"level3_{page_name}_current.png")

    capture_screenshot(full_url, page_name, SCREENSHOTS_DIR)
    captured = os.path.join(SCREENSHOTS_DIR, f"{page_name}.png")
    if os.path.exists(captured):
        os.replace(captured, current_path)

    if not os.path.exists(baseline_path):
        shutil.copy(current_path, baseline_path)
        return {"page": page_name, "status": "baseline_created", "regressions": []}

    result = compare_with_claude(baseline_path, current_path)
    regressions = result.get("regressions", [])
    for r in regressions:
        r["page"] = page_name

    return {
        "page": page_name,
        "status": "compared",
        "has_regressions": result.get("has_regressions", False),
        "summary": result.get("summary", ""),
        "regressions": regressions,
    }


def run_level3_scan(target_url: str) -> dict:
    """
    Scans all pages in parallel using threads.
    First run: captures and stores baselines.
    Subsequent runs: compares against baselines and reports regressions.
    """
    results = {}

    with ThreadPoolExecutor(max_workers=len(PAGES_TO_SCAN)) as executor:
        futures = {executor.submit(scan_single_page, page_cfg, target_url): page_cfg["name"] for page_cfg in PAGES_TO_SCAN}
        for future in as_completed(futures):
            page_name = futures[future]
            results[page_name] = future.result()

    # Preserve original page order
    ordered = [results[p["name"]] for p in PAGES_TO_SCAN]

    baseline_created = any(r["status"] == "baseline_created" for r in ordered)

    if baseline_created:
        return {
            "baseline_created": True,
            "pages_scanned": ordered,
            "regressions": [],
            "summary": "Baseline captured for all pages. Run the scan again to detect regressions.",
        }

    all_findings = [r for page in ordered for r in page.get("regressions", [])]
    summary_parts = [p.get("summary", "") for p in ordered if p.get("summary")]
    overall_summary = f"Scanned {len(ordered)} pages in parallel. Found {len(all_findings)} regression(s). " + " | ".join(summary_parts)

    return {
        "baseline_created": False,
        "pages_scanned": ordered,
        "regressions": all_findings,
        "total_regressions": len(all_findings),
        "summary": overall_summary,
    }


def refresh_baseline():
    """Delete all stored baselines so the next scan creates fresh ones."""
    for page_cfg in PAGES_TO_SCAN:
        path = os.path.join(BASELINES_DIR, f"{page_cfg['name']}.png")
        if os.path.exists(path):
            os.remove(path)
