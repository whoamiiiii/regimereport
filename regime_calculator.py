from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import CSI1000_CODE, CSI300_CODE, MA_LONG, MA_SHORT


def build_regime_from_csv(csv_path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(csv_path, dtype={"ts_code": str, "trade_date": str})
    required = {"ts_code", "trade_date", "close"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"CSV缺少必要列: {sorted(missing)}")

    data["trade_date"] = pd.to_datetime(data["trade_date"], format="%Y%m%d")
    pivot = data.pivot_table(index="trade_date", columns="ts_code", values="close")

    if CSI300_CODE not in pivot.columns or CSI1000_CODE not in pivot.columns:
        raise ValueError("CSV中缺少沪深300或中证1000数据")

    result = pd.DataFrame(index=pivot.index)
    result["csi300_close"] = pivot[CSI300_CODE]
    result["csi1000_close"] = pivot[CSI1000_CODE]
    result = result.dropna(subset=["csi300_close", "csi1000_close"]).sort_index()

    result["ratio"] = result["csi1000_close"] / result["csi300_close"]
    result["ma20"] = result["ratio"].shift(1).rolling(MA_SHORT).mean()
    result["ma60"] = result["ratio"].shift(1).rolling(MA_LONG).mean()
    result["regime"] = (result["ma20"] > result["ma60"]).astype(int)

    result = result.reset_index().rename(columns={"index": "trade_date"})
    return result
