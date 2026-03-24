from __future__ import annotations

import os
import smtplib
import time
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

try:
    from .config import (
        EMAIL_PASS,
        EMAIL_RECEIVERS,
        EMAIL_SENDER,
        MAIL_RETRY_COUNT,
        MAIL_RETRY_DELAY_SECONDS,
        REPORT_DRY_RUN,
        SMTP_PORT,
        SMTP_SERVER,
        SMTP_TIMEOUT,
    )
except ImportError:
    from config import (
        EMAIL_PASS,
        EMAIL_RECEIVERS,
        EMAIL_SENDER,
        MAIL_RETRY_COUNT,
        MAIL_RETRY_DELAY_SECONDS,
        REPORT_DRY_RUN,
        SMTP_PORT,
        SMTP_SERVER,
        SMTP_TIMEOUT,
    )


def parse_receivers(receivers_str: str | None = None) -> list[str]:
    raw = receivers_str if receivers_str is not None else EMAIL_RECEIVERS
    return [x.strip() for x in raw.split(",") if x.strip()]


def _build_message(subject: str, html: str, chart_path: str | None = None) -> MIMEMultipart:
    receivers = parse_receivers()
    if not EMAIL_SENDER or not EMAIL_PASS or not receivers:
        raise ValueError("邮件配置不完整：请检查 EMAIL_SENDER/EMAIL_PASS/EMAIL_RECEIVERS")

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(receivers)

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alt)

    if chart_path and Path(chart_path).exists():
        with open(chart_path, "rb") as f:
            img = MIMEBase("image", "png")
            img.set_payload(f.read())
        encoders.encode_base64(img)
        img.add_header("Content-ID", "<regime_chart>")
        img.add_header("Content-Disposition", "inline", filename=os.path.basename(chart_path))
        msg.attach(img)

    return msg


def _send_once(msg: MIMEMultipart) -> None:
    receivers = parse_receivers()
    use_ssl = SMTP_PORT == 465
    if use_ssl:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
        server.starttls()

    try:
        server.login(EMAIL_SENDER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, receivers, msg.as_string())
    finally:
        server.quit()


def _send_with_retry(msg: MIMEMultipart) -> None:
    last_error: Exception | None = None
    for attempt in range(1, MAIL_RETRY_COUNT + 1):
        try:
            _send_once(msg)
            return
        except Exception as exc:
            last_error = exc
            if attempt < MAIL_RETRY_COUNT:
                time.sleep(MAIL_RETRY_DELAY_SECONDS)
    if last_error:
        raise last_error


def send_main_report(subject: str, html: str, chart_path: str | None = None) -> None:
    if REPORT_DRY_RUN:
        print(f"[DRY-RUN] 跳过主日报真实发送: subject={subject}")
        return
    msg = _build_message(subject=subject, html=html, chart_path=chart_path)
    _send_with_retry(msg)


def send_failure_alert(stage: str, error_text: str) -> None:
    if REPORT_DRY_RUN:
        print(f"[DRY-RUN] 跳过失败告警真实发送: stage={stage}, error={error_text}")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[告警] regime 邮件生成失败 - {today}"
    html = f"""
    <html><body>
      <h3>Regime 日报失败告警</h3>
      <p><b>失败阶段：</b>{stage}</p>
      <p><b>错误信息：</b><pre>{error_text}</pre></p>
    </body></html>
    """
    msg = _build_message(subject=subject, html=html, chart_path=None)
    _send_with_retry(msg)
