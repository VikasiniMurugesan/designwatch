import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
REPORT_RECIPIENTS = os.getenv("REPORT_RECIPIENTS", "").split(",")
TARGET_WEBSITE_URL = os.getenv("TARGET_WEBSITE_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./designwatch.db")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SCREENSHOTS_DIR = os.path.join(DATA_DIR, "screenshots")
BASELINES_DIR = os.path.join(DATA_DIR, "baselines")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

for _dir in [DATA_DIR, SCREENSHOTS_DIR, BASELINES_DIR, REPORTS_DIR]:
    os.makedirs(_dir, exist_ok=True)
