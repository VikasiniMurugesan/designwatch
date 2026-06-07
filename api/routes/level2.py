import os
import shutil
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from repositories.scan_repository import get_db, create_scan, update_scan
from agents.design_audit_agent import run_level2_analysis
from services.report_service import generate_html_report
from entities.models import ScanLevel
from shared.config import SCREENSHOTS_DIR

router = APIRouter()


@router.post("/analyze")
async def analyze_before_after(
    baseline: UploadFile = File(...),
    current: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    allowed = {"image/png", "image/jpeg", "image/webp"}
    for f in [baseline, current]:
        if f.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Only PNG, JPG, and WebP images are supported.")

    scan = create_scan(db, level=ScanLevel.level2)

    baseline_ext = os.path.splitext(baseline.filename)[1]
    current_ext = os.path.splitext(current.filename)[1]
    baseline_path = os.path.join(SCREENSHOTS_DIR, f"scan_{scan.id}_baseline{baseline_ext}")
    current_path = os.path.join(SCREENSHOTS_DIR, f"scan_{scan.id}_current{current_ext}")

    with open(baseline_path, "wb") as f:
        shutil.copyfileobj(baseline.file, f)
    with open(current_path, "wb") as f:
        shutil.copyfileobj(current.file, f)

    scan.image_path = baseline_path
    scan.image_after_path = current_path
    db.commit()

    try:
        result = run_level2_analysis(baseline_path, current_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    findings_json = json.dumps(result.get("findings", []))
    summary = result.get("summary", "")
    report_path = generate_html_report(scan.id, "level2", summary, findings_json)
    update_scan(db, scan.id, findings_json, summary, report_path)

    return {
        "scan_id": scan.id,
        "overall_verdict": result.get("overall_verdict", ""),
        "improvements_count": result.get("improvements_count", 0),
        "regressions_count": result.get("regressions_count", 0),
        "neutral_count": result.get("neutral_count", 0),
        "summary": summary,
        "findings": result.get("findings", []),
        "report_path": report_path,
    }
