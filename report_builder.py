from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

try:
    from .config import CHART_TRADING_DAYS
except ImportError:
    from config import CHART_TRADING_DAYS

# 配置中文字体
def _setup_matplotlib_fonts():
    """配置 matplotlib 支持中文显示"""
    # 优先使用开源中文字体（WenQuanYi Micro Hei）
    font_candidates = [
        'WenQuanYi Micro Hei',      # Linux 开源中文字体
        'WenQuanYi Zen Hei',        # Linux 开源中文字体
        'SimHei',                    # Windows 中文字体
        'DejaVu Sans',              # 备选字体
    ]
    
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font_name in font_candidates:
        if any(font_name.lower() in f.lower() for f in available_fonts):
            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            return
    
    # 如果都找不到，至少禁用负号问题
    plt.rcParams['axes.unicode_minus'] = False

_setup_matplotlib_fonts()


def _regime_label(value: int) -> str:
    return "小盘占优" if int(value) == 1 else "大盘占优"


def plot_last_month_lines(df: pd.DataFrame, output_path: str | Path) -> str:
    output_path = Path(output_path)
    data = df.dropna(subset=["ratio"]).copy().sort_values("trade_date")
    if data.empty:
        raise ValueError("无可用数据生成折线图")

    chart_data = data.tail(CHART_TRADING_DAYS)
    start_date = chart_data["trade_date"].iloc[0].strftime("%Y-%m-%d")
    end_date = chart_data["trade_date"].iloc[-1].strftime("%Y-%m-%d")

    plt.figure(figsize=(12, 5))
    plt.plot(chart_data["trade_date"], chart_data["ratio"], label="ratio", linewidth=1.8)
    plt.plot(chart_data["trade_date"], chart_data["ma20"], label="ma20", linewidth=1.5)
    plt.plot(chart_data["trade_date"], chart_data["ma60"], label="ma60", linewidth=1.5)
    plt.title(f"大小盘强弱近30交易日 ({start_date} ~ {end_date}) | 数据截至 {end_date}")
    plt.xlabel("日期")
    plt.ylabel("数值")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    return str(output_path)


def build_html_report(df: pd.DataFrame, chart_path: str | None, chart_error: str | None = None) -> str:
    data = df.sort_values("trade_date").copy()
    if data.empty:
        raise ValueError("无可用数据生成日报")

    latest_row = data.iloc[-1]
    latest_date = latest_row["trade_date"].strftime("%Y-%m-%d")
    latest_regime = int(latest_row["regime"])

    yesterday_text = "无昨日对比数据"
    if len(data) >= 2:
        prev_regime = int(data.iloc[-2]["regime"])
        if prev_regime == latest_regime:
            yesterday_text = f"与昨日一致（{_regime_label(latest_regime)}）"
        else:
            yesterday_text = f"发生切换：{_regime_label(prev_regime)} → {_regime_label(latest_regime)}"

    current_year = latest_row["trade_date"].year
    ytd = data[data["trade_date"].dt.year == current_year]
    small_days = int((ytd["regime"] == 1).sum())
    large_days = int((ytd["regime"] == 0).sum())
    total_days = max(1, len(ytd))
    small_ratio = small_days / total_days * 100
    large_ratio = large_days / total_days * 100

    chart_section = ""
    if chart_path and Path(chart_path).exists():
        chart_section = "<p><b>近一个月折线图</b></p><p><img src='cid:regime_chart' style='max-width:100%;'></p>"
    elif chart_error:
        chart_section = f"<p><b>图表降级提示：</b>{chart_error}</p>"
    else:
        chart_section = "<p><b>图表降级提示：</b>图表未生成，已降级为文本日报。</p>"

    html = f"""
    <html>
      <body style='font-family:Microsoft YaHei,Arial,sans-serif;'>
        <h2>大小盘 Regime 每日报告</h2>
        <p><b>数据截至交易日：</b>{latest_date}</p>
        <p><b>今日状态：</b>{_regime_label(latest_regime)}</p>
        <p><b>昨日对比：</b>{yesterday_text}</p>
        <hr>
        <p><b>{current_year}年内占比（交易日口径）</b></p>
        <ul>
          <li>小盘占优：{small_days} 天（{small_ratio:.2f}%）</li>
          <li>大盘占优：{large_days} 天（{large_ratio:.2f}%）</li>
        </ul>
        <hr>
        {chart_section}
        <p style='color:#666;font-size:12px;'>该邮件由自动任务生成。</p>
      </body>
    </html>
    """
    return html


def build_subject(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return f"Regime 日报 - {now.strftime('%Y-%m-%d')}"
