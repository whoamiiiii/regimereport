from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pandas as pd
import tushare as ts

from .config import (
    BACKFILL_TRADING_DAYS,
    CSV_PATH,
    INDEX_CODES,
    INIT_START_DATE,
    TS_TOKEN,
)


def _validate_token() -> None:
    if not TS_TOKEN:
        raise ValueError("缺少 TS_TOKEN，请在环境变量中配置后重试")


def _load_existing(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame(columns=["ts_code", "trade_date", "close"])
    existing = pd.read_csv(csv_path, dtype={"ts_code": str, "trade_date": str})
    required = ["ts_code", "trade_date", "close"]
    missing = [col for col in required if col not in existing.columns]
    if missing:
        raise ValueError(f"历史CSV缺少必要列: {missing}")
    return existing[required].copy()


def _to_date_str(date_like: datetime) -> str:
    return date_like.strftime("%Y%m%d")


def _compute_start_date_with_backfill(pro, latest_trade_date: str) -> str:
    latest_dt = datetime.strptime(latest_trade_date, "%Y%m%d")
    window_start = latest_dt - timedelta(days=45)
    cal = pro.trade_cal(
        exchange="SSE",
        start_date=_to_date_str(window_start),
        end_date=latest_trade_date,
    )
    if cal is None or cal.empty:
        return latest_trade_date
    open_days = cal[cal["is_open"] == 1]["cal_date"].sort_values().tolist()
    if not open_days:
        return latest_trade_date
    idx = max(0, len(open_days) - BACKFILL_TRADING_DAYS)
    return open_days[idx]


def _fetch_index_daily(pro, ts_code: str, start_date: str) -> pd.DataFrame:
    fetched = pro.index_daily(ts_code=ts_code, start_date=start_date)
    if fetched is None or fetched.empty:
        return pd.DataFrame(columns=["ts_code", "trade_date", "close"])
    cols = ["ts_code", "trade_date", "close"]
    return fetched[cols].copy()


def update_index_csv(csv_path: str | Path = CSV_PATH) -> Dict[str, object]:
    _validate_token()
    csv_path = Path(csv_path)

    existing = _load_existing(csv_path)
    pro = ts.pro_api(TS_TOKEN)

    if existing.empty:
        start_date = INIT_START_DATE
    else:
        latest_trade_date = existing["trade_date"].max()
        start_date = _compute_start_date_with_backfill(pro, latest_trade_date)

    new_data_list = []
    for code in INDEX_CODES:
        data = _fetch_index_daily(pro, code, start_date)
        if not data.empty:
            new_data_list.append(data)

    if new_data_list:
        fetched_all = pd.concat(new_data_list, ignore_index=True)
    else:
        fetched_all = pd.DataFrame(columns=["ts_code", "trade_date", "close"])

    merged = pd.concat([existing, fetched_all], ignore_index=True)
    merged = merged.drop_duplicates(subset=["ts_code", "trade_date"], keep="last")
    merged = merged.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

    rows_added = len(merged) - len(existing)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(csv_path, index=False, encoding="utf-8-sig")

    latest = merged["trade_date"].max() if not merged.empty else ""
    latest_fmt = ""
    if latest:
        latest_fmt = datetime.strptime(latest, "%Y%m%d").strftime("%Y-%m-%d")

    return {
        "success": True,
        "rows_added": int(rows_added),
        "latest_trade_date": latest_fmt,
        "message": f"更新完成，新增 {rows_added} 行",
    }
