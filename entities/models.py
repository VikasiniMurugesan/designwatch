from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum
from sqlalchemy.orm import declarative_base
import datetime
import enum

Base = declarative_base()


class ScanLevel(str, enum.Enum):
    level1 = "level1"
    level2 = "level2"
    level3 = "level3"


class ScanStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class ScanReport(Base):
    __tablename__ = "scan_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Enum(ScanLevel), nullable=False)
    status = Column(Enum(ScanStatus), default=ScanStatus.pending)
    # For level 1: path to the uploaded screenshot
    # For level 2: path to baseline screenshot
    image_path = Column(String, nullable=True)
    # For level 2: path to current/after screenshot
    image_after_path = Column(String, nullable=True)
    # For level 3: URL that was scanned
    target_url = Column(String, nullable=True)
    # JSON string of findings
    findings_json = Column(Text, nullable=True)
    # Overall verdict / summary
    summary = Column(Text, nullable=True)
    # Path to generated HTML report
    report_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
