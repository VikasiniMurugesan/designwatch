import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shared.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, REPORT_RECIPIENTS


SEVERITY_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#d97706",
    "low": "#65a30d",
    "info": "#0891b2",
}

DIRECTION_COLORS = {
    "regression": "#dc2626",
    "improvement": "#16a34a",
    "neutral": "#6b7280",
}


def build_email_html(level: str, summary: str, findings: list, target: str = "", scan_id: int = None) -> str:
    level_labels = {
        "level1": "Level 1 — Design Audit",
        "level2": "Level 2 — Before/After Regression",
        "level3": "Level 3 — Autonomous Regression Scan",
    }
    label = level_labels.get(level, level)

    findings_html = ""
    for f in findings:
        severity = f.get("severity", f.get("direction", "info")).lower()
        color = SEVERITY_COLORS.get(severity) or DIRECTION_COLORS.get(severity, "#6b7280")
        confidence = f.get("confidence_score", f.get("confidence", 0))
        principle = f.get("principle", f.get("change_type", f.get("issue", "")))
        location = f.get("location", "")
        issue = f.get("issue", f.get("description", ""))
        impact = f.get("user_impact", f.get("evidence", ""))
        recommendation = f.get("recommendation", "")

        findings_html += f"""
        <tr>
          <td style="padding:0 0 16px 0;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;border-left:4px solid {color};box-shadow:0 1px 4px rgba(0,0,0,0.08);">
              <tr>
                <td style="padding:14px 18px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                        <span style="background:{color};color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;text-transform:uppercase;">{severity}</span>
                        &nbsp;
                        <span style="font-size:15px;font-weight:600;color:#1e293b;">{principle}</span>
                      </td>
                      <td align="right" style="font-size:12px;color:#64748b;">Confidence: {confidence}%</td>
                    </tr>
                  </table>
                  <p style="margin:8px 0 4px;font-size:13px;color:#374151;"><strong>Location:</strong> {location}</p>
                  <p style="margin:4px 0;font-size:13px;color:#374151;"><strong>Issue:</strong> {issue}</p>
                  {"<p style='margin:4px 0;font-size:13px;color:#374151;'><strong>Impact:</strong> " + impact + "</p>" if impact else ""}
                  {"<p style='margin:4px 0;font-size:13px;color:#374151;'><strong>Recommendation:</strong> " + recommendation + "</p>" if recommendation else ""}
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    target_row = f"<tr><td style='padding:4px 0;font-size:13px;color:#94a3b8;'><strong>Target:</strong> {target}</td></tr>" if target else ""
    scan_row = f"<tr><td style='padding:4px 0;font-size:13px;color:#94a3b8;'><strong>Scan ID:</strong> #{scan_id}</td></tr>" if scan_id else ""
    count = len(findings)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1e293b 0%,#334155 100%);padding:32px 36px;border-radius:12px 12px 0 0;">
            <p style="margin:0 0 4px;font-size:13px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Designwatch Report</p>
            <h1 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#ffffff;">{label}</h1>
            <table cellpadding="0" cellspacing="0">
              {target_row}
              {scan_row}
            </table>
          </td>
        </tr>

        <!-- Summary -->
        <tr>
          <td style="background:#6366f1;padding:16px 36px;">
            <p style="margin:0;font-size:14px;color:#ffffff;line-height:1.6;">{summary}</p>
          </td>
        </tr>

        <!-- Findings count -->
        <tr>
          <td style="background:#ffffff;padding:16px 36px 8px;border-top:1px solid #e2e8f0;">
            <p style="margin:0;font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">{count} Finding{"s" if count != 1 else ""} Detected</p>
          </td>
        </tr>

        <!-- Findings -->
        <tr>
          <td style="background:#ffffff;padding:8px 36px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {findings_html if findings_html else '<tr><td style="padding:16px 0;font-size:14px;color:#16a34a;">✓ No issues detected</td></tr>'}
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:16px 36px;border-radius:0 0 12px 12px;border-top:1px solid #e2e8f0;">
            <p style="margin:0;font-size:12px;color:#94a3b8;text-align:center;">Sent by Designwatch — AI-powered UI/UX audit agent</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_report_email(subject: str, summary: str, findings_json: str, level: str, target: str = "", scan_id: int = None):
    findings = json.loads(findings_json) if findings_json else []
    body_html = build_email_html(level, summary, findings, target, scan_id)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = ", ".join(REPORT_RECIPIENTS)
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, REPORT_RECIPIENTS, msg.as_string())
