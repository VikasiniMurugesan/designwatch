import json
import os
from datetime import datetime
from shared.config import REPORTS_DIR


def generate_html_report(scan_id: int, level: str, summary: str, findings_json: str, target: str = "") -> str:
    findings = json.loads(findings_json) if findings_json else []
    report_path = os.path.join(REPORTS_DIR, f"report_{scan_id}.html")

    severity_colors = {
        "critical": "#dc2626",
        "high": "#ea580c",
        "medium": "#d97706",
        "low": "#65a30d",
        "info": "#0891b2",
        "improvement": "#16a34a",
        "regression": "#dc2626",
        "neutral": "#6b7280",
    }

    findings_html = ""
    for f in findings:
        severity = f.get("severity", f.get("direction", "info")).lower()
        color = severity_colors.get(severity, "#6b7280")
        confidence = f.get("confidence_score", f.get("confidence", 0))
        findings_html += f"""
        <div class="finding">
            <div class="finding-header">
                <span class="badge" style="background:{color}">{severity.upper()}</span>
                <span class="principle">{f.get('principle', f.get('change_type', ''))}</span>
                <span class="confidence">Confidence: {confidence}%</span>
            </div>
            <p><strong>Location:</strong> {f.get('location', '')}</p>
            <p><strong>Issue:</strong> {f.get('issue', f.get('description', ''))}</p>
            <p><strong>User Impact:</strong> {f.get('user_impact', '')}</p>
            <p><strong>Recommendation:</strong> {f.get('recommendation', '')}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Designwatch Report — {level.upper()}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 24px; background: #f8fafc; color: #1e293b; }}
  .header {{ background: #1e293b; color: white; padding: 24px 32px; border-radius: 8px; margin-bottom: 24px; }}
  .header h1 {{ margin: 0 0 4px 0; font-size: 24px; }}
  .header p {{ margin: 0; opacity: 0.7; font-size: 14px; }}
  .summary-box {{ background: white; border-left: 4px solid #6366f1; padding: 16px 20px; border-radius: 4px; margin-bottom: 24px; }}
  .finding {{ background: white; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .finding-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
  .badge {{ color: white; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; }}
  .principle {{ font-weight: 600; font-size: 15px; }}
  .confidence {{ margin-left: auto; color: #64748b; font-size: 13px; }}
  p {{ margin: 6px 0; font-size: 14px; line-height: 1.6; }}
  strong {{ color: #374151; }}
  .meta {{ color: #64748b; font-size: 13px; margin-bottom: 16px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Designwatch — {level.upper()} Report</h1>
  <p>Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} {f'| Target: {target}' if target else ''}</p>
</div>
<div class="summary-box">
  <strong>Summary</strong>
  <p>{summary}</p>
</div>
<p class="meta">{len(findings)} finding(s) detected</p>
{findings_html}
</body>
</html>"""

    with open(report_path, "w") as f:
        f.write(html)

    return report_path
