from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import CHART_PATH, CSV_PATH, LOG_DIR, REPORT_DRY_RUN, ensure_dirs
from .data_updater import update_index_csv
from .mailer import send_failure_alert, send_main_report
from .regime_calculator import build_regime_from_csv
from .report_builder import build_html_report, build_subject, plot_last_month_lines


def _setup_logging() -> Path:
    ensure_dirs()
    log_file = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def run() -> int:
    log_file = _setup_logging()
    logging.info("开始执行 Regime 每日报告任务")
    if REPORT_DRY_RUN:
        logging.info("当前为 DRY-RUN 模式：将跳过真实邮件发送")

    try:
        update_result = update_index_csv(CSV_PATH)
        logging.info("数据更新完成: %s", update_result)

        regime_df = build_regime_from_csv(CSV_PATH)
        chart_path = None
        chart_error = None

        try:
            chart_path = plot_last_month_lines(regime_df, CHART_PATH)
            logging.info("图表生成成功: %s", chart_path)
        except Exception as chart_exc:
            chart_error = f"图表生成失败，已降级为文本日报：{chart_exc}"
            logging.exception("图表生成失败，走降级流程")

        subject = build_subject()
        html = build_html_report(regime_df, chart_path=chart_path, chart_error=chart_error)

        try:
            send_main_report(subject=subject, html=html, chart_path=chart_path)
            logging.info("主日报发送成功")
            return 0
        except Exception as mail_exc:
            logging.exception("主日报发送失败")
            try:
                send_failure_alert(stage="send_main_report", error_text=str(mail_exc))
                logging.info("失败告警邮件发送成功")
            except Exception:
                logging.exception("失败告警邮件发送失败")
            return 1

    except Exception as exc:
        logging.exception("主流程执行失败")
        try:
            send_failure_alert(stage="pipeline", error_text=f"{exc}\n日志: {log_file}")
            logging.info("主流程失败告警发送成功")
        except Exception:
            logging.exception("主流程失败告警发送失败")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
