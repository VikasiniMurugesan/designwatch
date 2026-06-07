import os
import shutil
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from repositories.scan_repository import get_db, create_scan, update_scan
from agents.design_audit_agent import run_level1_analysis
from services.report_service import generate_html_report
from entities.models import ScanLevel
from shared.config import SCREENSHOTS_DIR

router = APIRouter()


@router.post("/analyze")
async def analyze_screenshot(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, and WebP images are supported.")

    ext = os.path.splitext(file.filename)[1]
    scan = create_scan(db, level=ScanLevel.level1)
    image_path = os.path.join(SCREENSHOTS_DIR, f"scan_{scan.id}{ext}")

    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    db.refresh(scan)
    scan.image_path = image_path
    db.commit()

    try:
        result = run_level1_analysis(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    findings_json = json.dumps(result.get("findings", []))
    summary = result.get("summary", "")
    report_path = generate_html_report(scan.id, "level1", summary, findings_json)
    update_scan(db, scan.id, findings_json, summary, report_path)

    return {
        "scan_id": scan.id,
        "summary": summary,
        "findings": result.get("findings", []),
        "report_path": report_path,
    }
