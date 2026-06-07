import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from repositories.scan_repository import get_db, create_scan, update_scan
from agents.browser_agent import run_level3_scan, refresh_baseline
from services.report_service import generate_html_report
from services.email_service import send_report_email
from entities.models import ScanLevel
from shared.config import TARGET_WEBSITE_URL

router = APIRouter()


class ScanRequest(BaseModel):
    url: str = TARGET_WEBSITE_URL


@router.post("/scan")
def trigger_scan(request: ScanRequest, db: Session = Depends(get_db)):
    if not request.url:
        raise HTTPException(status_code=400, detail="Target URL is required.")

    scan = create_scan(db, level=ScanLevel.level3, target_url=request.url)

    try:
        result = run_level3_scan(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

    # Convert regressions to findings format for the report
    findings = [
        {
            "principle": "Regression",
            "location": r.get("location", ""),
            "issue": r.get("issue", ""),
            "user_impact": r.get("evidence", ""),
            "recommendation": "Review and fix the regression before merging.",
            "severity": r.get("severity", "medium"),
            "confidence_score": r.get("confidence_score", 0),
        }
        for r in result.get("regressions", [])
    ]

    findings_json = json.dumps(findings)
    summary = result.get("summary", "")
    report_path = generate_html_report(scan.id, "level3", summary, findings_json, target=request.url)
    update_scan(db, scan.id, findings_json, summary, report_path)

    if not result.get("baseline_created") and result.get("regressions"):
        try:
            send_report_email(
                subject=f"Designwatch Level 3 — {len(result['regressions'])} regression(s) detected",
                body_html=f"<p>{summary}</p><p>See attached report for details.</p>",
                report_path=report_path,
            )
        except Exception:
            pass

    return {
        "scan_id": scan.id,
        "baseline_created": result.get("baseline_created", False),
        "pages_scanned": result.get("pages_scanned", []),
        "regressions": result.get("regressions", []),
        "total_regressions": result.get("total_regressions", 0),
        "summary": summary,
        "report_path": report_path,
    }


@router.post("/refresh-baseline")
def reset_baseline():
    try:
        refresh_baseline()
        return {"message": "Baseline cleared. Next scan will create a fresh baseline."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
