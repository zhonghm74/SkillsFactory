#!/usr/bin/env python3
"""
Generate Coffee Sales board-level one-page V2 assets (PNG + PDF).

Key safeguards:
- Normalize and validate literal escape sequences in text annotations.
- Export through scientific-visualization helper, which sanitizes all Text objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager, rcParams
from matplotlib.gridspec import GridSpec


SCIVIZ_SCRIPTS = Path("/workspace/.cursor/skills/scientific-visualization/scripts")
if str(SCIVIZ_SCRIPTS) not in sys.path:
    sys.path.append(str(SCIVIZ_SCRIPTS))

from figure_export import save_publication_figure  # noqa: E402
from validate_text_escaping import sanitize_and_validate  # noqa: E402


@dataclass
class Metrics:
    total_revenue: float
    total_orders: int
    avg_order_value: float
    top3_share: float
    monthly_series: pd.Series
    weekday_series: pd.Series
    hourly_series: pd.Series
    product_series: pd.Series


def pick_chinese_font() -> str:
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            return font_manager.FontProperties(fname=path).get_name()
    raise RuntimeError("No Chinese font found. Please install WenQuanYi or Droid fallback font.")


def load_and_prepare(source: Path) -> pd.DataFrame:
    df = pd.read_csv(source)
    df["money"] = pd.to_numeric(df["money"], errors="coerce")
    df["hour_of_day"] = pd.to_numeric(df["hour_of_day"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["money", "hour_of_day", "Date", "coffee_name", "Weekday"])
    df = df[df["money"] > 0].copy()
    df["hour_of_day"] = df["hour_of_day"].astype(int)
    df["month"] = df["Date"].dt.to_period("M").astype(str)
    return df


def calc_metrics(df: pd.DataFrame) -> Metrics:
    monthly = df.groupby("month")["money"].sum().sort_index()
    weekday = (
        df.groupby("Weekday")["money"]
        .sum()
        .reindex(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    )
    hourly = df.groupby("hour_of_day")["money"].sum().sort_index()
    product = df.groupby("coffee_name")["money"].sum().sort_values(ascending=False)
    return Metrics(
        total_revenue=float(df["money"].sum()),
        total_orders=int(len(df)),
        avg_order_value=float(df["money"].mean()),
        top3_share=float(product.head(3).sum() / product.sum()),
        monthly_series=monthly,
        weekday_series=weekday,
        hourly_series=hourly,
        product_series=product,
    )


def build_summary_text(m: Metrics) -> str:
    peak_month = m.monthly_series.idxmax()
    peak_month_value = float(m.monthly_series.max())
    low_month = m.monthly_series.idxmin()
    low_month_value = float(m.monthly_series.min())
    best_day = m.weekday_series.idxmax()
    worst_day = m.weekday_series.idxmin()
    best_hour = int(m.hourly_series.idxmax())

    lines = [
        f"关键结论：收入总规模为 {m.total_revenue/10000:.2f} 万，订单 {m.total_orders:,} 笔，客单价 {m.avg_order_value:.2f}。",
        f"月度峰值在 {peak_month}（{peak_month_value:,.0f}），低点在 {low_month}（{low_month_value:,.0f}）。",
        f"周内表现优于周末（最佳 {best_day}，最弱 {worst_day}），核心高峰小时为 {best_hour}:00。",
        f"产品结构存在头部效应：Top3 产品贡献 {m.top3_share*100:.1f}% 收入。",
        "",
        "建议动作：",
        "1) 高峰前 1 小时完成备货与陈列，保障 10:00/16:00 两个窗口转化；",
        "2) 周末（尤其周日）设置限定组合与加价购，缩小与周内差距；",
        "3) 围绕 Top3 产品设计跨品类连带，提升客单价与复购。",
    ]
    return sanitize_and_validate("\n".join(lines), field_name="right_panel_summary")


def render_figure(metrics: Metrics, source: Path, output_base: Path, font_name: str) -> None:
    # Convert missing glyph warning into hard failure to avoid silent rendering issues.
    warnings.filterwarnings("error", message=".*Glyph.*missing from font.*", category=UserWarning)

    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = [
        font_name,
        "WenQuanYi Micro Hei",
        "Droid Sans Fallback",
        "Noto Sans CJK SC",
        "SimHei",
        "DejaVu Sans",
    ]
    rcParams["axes.unicode_minus"] = False

    bg = "#FFFDF8"
    panel_bg = "#FFFFFF"
    text = "#1F2933"
    muted = "#8A94A6"
    accent = "#3B82F6"
    accent_2 = "#F97316"
    accent_3 = "#0EA5A4"
    border = "#E5E7EB"
    grid = "#E9EEF5"

    fig = plt.figure(figsize=(16, 6.2), dpi=160)
    fig.patch.set_facecolor(bg)
    gs = GridSpec(
        2,
        3,
        figure=fig,
        width_ratios=[0.62, 2.3, 1.48],
        height_ratios=[1.0, 1.0],
        wspace=0.08,
        hspace=0.16,
    )

    # Left KPI panel
    ax_left = fig.add_subplot(gs[:, 0])
    ax_left.set_facecolor(panel_bg)
    ax_left.axis("off")
    ax_left.text(0.08, 0.95, "董事会一页总览", fontsize=12, weight="bold", color=text, va="top")
    ax_left.text(0.08, 0.91, "Coffee Sales 经营纪要", fontsize=8.5, color=muted, va="top")

    y = 0.80
    kpis = [
        ("总收入", f"{metrics.total_revenue/10000:.2f} 万"),
        ("总订单", f"{metrics.total_orders:,}"),
        ("平均客单价", f"{metrics.avg_order_value:.2f}"),
        ("Top3 产品收入占比", f"{metrics.top3_share*100:.1f}%"),
    ]
    for label, value in kpis:
        ax_left.text(0.08, y, label, fontsize=8, color=muted, va="bottom")
        ax_left.text(0.08, y - 0.07, value, fontsize=20, weight="bold", color=text, va="bottom")
        y -= 0.19
    ax_left.text(0.08, 0.02, f"生成时间：{datetime.now():%Y-%m-%d %H:%M}", fontsize=7.5, color=muted)

    # Middle area: 4 small charts
    inner = gs[:, 1].subgridspec(2, 2, wspace=0.18, hspace=0.22)

    def style(ax, title: str) -> None:
        ax.set_facecolor(panel_bg)
        ax.set_title(title, loc="left", fontsize=10.5, weight="bold", color=text)
        for s in ax.spines.values():
            s.set_color(border)
        ax.tick_params(colors=text, labelsize=8)
        ax.grid(True, axis="y", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)

    ax1 = fig.add_subplot(inner[0, 0])
    style(ax1, "01 | 月度收入趋势")
    monthly_x = np.arange(len(metrics.monthly_series.index))
    monthly_y = metrics.monthly_series.values
    ax1.plot(monthly_x, monthly_y, color=accent, lw=2.2, marker="o", ms=3.5)
    ax1.fill_between(monthly_x, monthly_y, color=accent, alpha=0.1)
    ax1.set_xticks(monthly_x[::2])
    ax1.set_xticklabels([str(v) for v in metrics.monthly_series.index[::2]], rotation=0)
    peak_idx = int(np.argmax(monthly_y))
    ax1.annotate(
        f"峰值 {metrics.monthly_series.index[peak_idx]}\n{monthly_y[peak_idx]:,.0f}",
        xy=(peak_idx, monthly_y[peak_idx]),
        xytext=(peak_idx - 2.2, monthly_y[peak_idx] * 0.87),
        fontsize=7.5,
        color=text,
        arrowprops=dict(arrowstyle="->", color=accent, lw=1.0),
    )

    ax2 = fig.add_subplot(inner[0, 1])
    style(ax2, "02 | 产品结构贡献")
    top_products = metrics.product_series.head(6).sort_values(ascending=True)
    ax2.barh(top_products.index, top_products.values, color=accent_2, alpha=0.9)
    ax2.tick_params(axis="y", labelsize=7.5)
    ax2.grid(True, axis="x", color=grid, linewidth=0.8)
    ax2.grid(False, axis="y")

    ax3 = fig.add_subplot(inner[1, 0])
    style(ax3, "03 | 星期收入结构")
    wd = metrics.weekday_series
    ax3.bar(np.arange(len(wd.index)), wd.values, color=accent_3, alpha=0.9)
    ax3.set_xticks(np.arange(len(wd.index)))
    ax3.set_xticklabels(wd.index)
    ax3.text(
        0.02,
        0.92,
        f"最佳: {wd.idxmax()} / 最弱: {wd.idxmin()}",
        transform=ax3.transAxes,
        fontsize=7.5,
        color=text,
        va="top",
    )

    ax4 = fig.add_subplot(inner[1, 1])
    style(ax4, "04 | 小时收入曲线")
    hrs = metrics.hourly_series
    ax4.plot(hrs.index, hrs.values, color=accent_2, lw=2.0, marker="o", ms=3)
    best_hour = int(hrs.idxmax())
    ax4.annotate(
        f"{best_hour}:00 高峰",
        xy=(best_hour, float(hrs.max())),
        xytext=(best_hour + 1, float(hrs.max()) * 0.85),
        fontsize=7.5,
        color=text,
        arrowprops=dict(arrowstyle="->", color=accent_2, lw=1.0),
    )

    # Right narrative panel
    ax_right = fig.add_subplot(gs[:, 2])
    ax_right.set_facecolor(panel_bg)
    ax_right.axis("off")
    ax_right.set_title("05 | 关键结论与动作", loc="left", fontsize=10.5, weight="bold", color=text)

    summary = build_summary_text(metrics)
    ax_right.text(
        0.02,
        0.96,
        summary,
        va="top",
        ha="left",
        fontsize=9,
        color=text,
        linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFFEFC", edgecolor=border),
    )

    fig.suptitle("Coffee Sales 董事会一页版（重设·高冲击）", fontsize=16, weight="bold", color=text, y=0.995)
    fig.text(0.01, 0.01, f"数据源：{source}", fontsize=8, color=muted)

    save_publication_figure(
        fig=fig,
        filename=output_base,
        formats=["png", "pdf"],
        dpi=300,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def main() -> None:
    source = Path("/workspace/data/Coffe_sales.csv")
    output_base = Path("/workspace/reports/coffee-sales/assets/coffee-sales-board-one-page-v2")
    source.parent.mkdir(parents=True, exist_ok=True)
    output_base.parent.mkdir(parents=True, exist_ok=True)

    font_name = pick_chinese_font()
    df = load_and_prepare(source)
    metrics = calc_metrics(df)
    render_figure(metrics, source=source, output_base=output_base, font_name=font_name)

    # Keep legacy pdf path used by markdown.
    legacy_pdf = Path("/workspace/reports/coffee-sales/coffee-sales-board-one-page-v2.pdf")
    generated_pdf = output_base.with_suffix(".pdf")
    legacy_pdf.write_bytes(generated_pdf.read_bytes())
    print(f"font={font_name}")
    print(f"png={output_base.with_suffix('.png')}")
    print(f"pdf={generated_pdf}")
    print(f"legacy_pdf={legacy_pdf}")


if __name__ == "__main__":
    main()
