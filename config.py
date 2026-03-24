from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

CSV_PATH = DATA_DIR / "regime_index_daily.csv"
CHART_PATH = OUTPUT_DIR / "regime_last_month.png"

CSI300_CODE = "000300.SH"
CSI1000_CODE = "000852.SH"
INDEX_CODES = [CSI300_CODE, CSI1000_CODE]

INIT_START_DATE = "20150101"
BACKFILL_TRADING_DAYS = 5

MA_SHORT = 20
MA_LONG = 60
CHART_TRADING_DAYS = 30

SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT") or "30")
MAIL_RETRY_COUNT = int(os.getenv("MAIL_RETRY_COUNT") or "3")
MAIL_RETRY_DELAY_SECONDS = int(os.getenv("MAIL_RETRY_DELAY_SECONDS") or "5")
REPORT_DRY_RUN = os.getenv("REPORT_DRY_RUN", "false").strip().lower() in {"1", "true", "yes", "y", "on"}

TS_TOKEN = os.getenv("TS_TOKEN", "")

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
EMAIL_RECEIVERS = os.getenv("EMAIL_RECEIVERS", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
