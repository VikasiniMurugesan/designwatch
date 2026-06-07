from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entities.models import Base, ScanReport, ScanStatus
from shared.config import DATABASE_URL
import datetime

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_scan(db, level, image_path=None, image_after_path=None, target_url=None):
    scan = ScanReport(
        level=level,
        image_path=image_path,
        image_after_path=image_after_path,
        target_url=target_url,
        status=ScanStatus.pending,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def update_scan(db, scan_id, findings_json, summary, report_path=None):
    scan = db.query(ScanReport).filter(ScanReport.id == scan_id).first()
    scan.findings_json = findings_json
    scan.summary = summary
    scan.report_path = report_path
    scan.status = ScanStatus.completed
    scan.completed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(scan)
    return scan


def get_all_scans(db):
    return db.query(ScanReport).order_by(ScanReport.created_at.desc()).all()


def get_scan_by_id(db, scan_id):
    return db.query(ScanReport).filter(ScanReport.id == scan_id).first()
