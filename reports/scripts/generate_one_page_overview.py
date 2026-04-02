#!/usr/bin/env python3
"""
Generate business one-page overview images (light/dark) with robust Chinese font fallback.
Also validates glyph coverage by converting matplotlib missing-glyph warnings to hard errors.
"""

from __future__ import annotations

import argparse
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager, rcParams


@dataclass
class Metrics:
    revenue_2019: float
    revenue_2020: float
    clients_2019: int
    clients_2020: int
    orders_2019: int
    orders_2020: int
    orders_per_client_2019: float
    orders_per_client_2020: float
    products_per_client_2019: float
    products_per_client_2020: float
    top1_share_2020: float
    top10_share_2020: float


def pct_change(a: float, b: float) -> float:
    if a == 0:
        return float("nan")
    return (b - a) / a * 100


def select_chinese_font() -> str:
    """Pick the first available CJK-capable font."""
    candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            prop = font_manager.FontProperties(fname=path)
            return prop.get_name()
    raise RuntimeError('No Chinese font found. Install WenQuanYi or Droid fallback fonts.')


def load_data(src: Path) -> pd.DataFrame:
    frames = []
    for sheet in ['2019', '2020']:
        df = pd.read_excel(src, sheet_name=sheet)
        df = df.rename(
            columns={
                'Order number': 'order_number',
                'Client ID': 'client_id',
                'Product code': 'product_code',
                'Date of delivery': 'delivery_date',
                'Delivery amount': 'delivery_amount',
            }
        )
        df['delivery_amount'] = pd.to_numeric(df['delivery_amount'], errors='coerce')
        df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')
        df = df.dropna(subset=['delivery_date', 'delivery_amount'])
        df = df[df['delivery_amount'] > 0]
        df['year'] = df['delivery_date'].dt.year
        df['month'] = df['delivery_date'].dt.month
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def calc_metrics(df: pd.DataFrame) -> tuple[Metrics, pd.DataFrame]:
    yearly = (
        df.groupby('year')
        .agg(
            revenue=('delivery_amount', 'sum'),
            orders=('order_number', lambda s: s.nunique(dropna=True)),
            clients=('client_id', lambda s: s.nunique(dropna=True)),
        )
        .reset_index()
    )
    y19 = yearly[yearly['year'] == 2019].iloc[0]
    y20 = yearly[yearly['year'] == 2020].iloc[0]

    d19 = df[df['year'] == 2019]
    d20 = df[df['year'] == 2020]

    orders_per_client_19 = y19['orders'] / y19['clients']
    orders_per_client_20 = y20['orders'] / y20['clients']
    products_per_client_19 = d19.groupby('client_id')['product_code'].nunique().mean()
    products_per_client_20 = d20.groupby('client_id')['product_code'].nunique().mean()

    client_rev_20 = d20.groupby('client_id')['delivery_amount'].sum().sort_values(ascending=False)
    total_20 = float(client_rev_20.sum())
    top1_share = float(client_rev_20.head(1).sum() / total_20)
    top10_share = float(client_rev_20.head(10).sum() / total_20)

    monthly = (
        df.groupby(['year', 'month'])
        .agg(revenue=('delivery_amount', 'sum'))
        .reset_index()
    )

    return (
        Metrics(
            revenue_2019=float(y19['revenue']),
            revenue_2020=float(y20['revenue']),
            clients_2019=int(y19['clients']),
            clients_2020=int(y20['clients']),
            orders_2019=int(y19['orders']),
            orders_2020=int(y20['orders']),
            orders_per_client_2019=float(orders_per_client_19),
            orders_per_client_2020=float(orders_per_client_20),
            products_per_client_2019=float(products_per_client_19),
            products_per_client_2020=float(products_per_client_20),
            top1_share_2020=top1_share,
            top10_share_2020=top10_share,
        ),
        monthly,
    )


def render(kind: str, metrics: Metrics, monthly: pd.DataFrame, src: Path, out: Path, font_name: str) -> None:
    is_dark = kind == 'dark'

    if is_dark:
        bg = '#0B1220'
        panel_bg = '#111827'
        txt = '#E5E7EB'
        muted = '#9CA3AF'
        accent = '#38BDF8'
        edge = '#334155'
    else:
        bg = '#FFFFFF'
        panel_bg = '#FFFFFF'
        txt = '#111827'
        muted = '#9CA3AF'
        accent = '#2563EB'
        edge = '#D1D5DB'

    warn_color = '#EF4444'

    plt.style.use('dark_background' if is_dark else 'seaborn-v0_8-whitegrid')
    # Re-apply font settings after style.use, because style presets can overwrite font config.
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = [
        font_name,
        'WenQuanYi Micro Hei',
        'Droid Sans Fallback',
        'Noto Sans CJK SC',
        'SimHei',
        'DejaVu Sans',
    ]
    rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(16, 10), dpi=160)
    fig.patch.set_facecolor(bg)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15], width_ratios=[1.05, 1.05, 1.2], hspace=0.32, wspace=0.25)

    def style_ax(ax):
        ax.set_facecolor(panel_bg)
        for spine in ax.spines.values():
            spine.set_color(edge)
        ax.tick_params(colors=txt)
        ax.yaxis.label.set_color(txt)
        ax.xaxis.label.set_color(txt)
        ax.title.set_color(txt)
        ax.grid(color='#E5E7EB' if not is_dark else '#1F2937', alpha=0.5)

    # A: revenue
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1)
    vals = [metrics.revenue_2019, metrics.revenue_2020]
    ax1.bar(['2019', '2020'], vals, color=[muted, accent], edgecolor='none', width=0.58)
    ax1.set_title('A. 收入规模', loc='left', fontsize=12, weight='bold')
    ax1.set_ylabel('收入')
    for i, v in enumerate(vals):
        ax1.text(i, v, f"{v/1e6:.2f}百万", ha='center', va='bottom', fontsize=9, color=txt)
    ax1.set_ylim(0, max(vals) * 1.25)
    ax1.annotate(
        f"同比 +{pct_change(metrics.revenue_2019, metrics.revenue_2020):.1f}%",
        xy=(1, metrics.revenue_2020),
        xytext=(0.45, metrics.revenue_2020 * 0.8),
        arrowprops=dict(arrowstyle='->', lw=1.2, color=accent),
        fontsize=10,
        color=accent,
    )

    # B: drivers
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2)
    labels = ['客户数', '每客户订单数', '每客户产品覆盖数']
    v19 = [metrics.clients_2019, metrics.orders_per_client_2019, metrics.products_per_client_2019]
    v20 = [metrics.clients_2020, metrics.orders_per_client_2020, metrics.products_per_client_2020]
    x = np.arange(len(labels))
    w = 0.34
    ax2.bar(x - w / 2, v19, width=w, color=muted, edgecolor='none', label='2019')
    bars = ax2.bar(x + w / 2, v20, width=w, color=accent, edgecolor='none', label='2020')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_title('B. 增长驱动', loc='left', fontsize=12, weight='bold')
    leg = ax2.legend(frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color(txt)
    for b, v, a in zip(bars, v20, v19):
        ax2.text(b.get_x() + b.get_width() / 2, v, f"{pct_change(a, v):+.0f}%", ha='center', va='bottom', fontsize=8, color=txt)

    # C: concentration
    ax3 = fig.add_subplot(gs[0, 2])
    style_ax(ax3)
    shares = [metrics.top1_share_2020 * 100, (metrics.top10_share_2020 - metrics.top1_share_2020) * 100, (1 - metrics.top10_share_2020) * 100]
    names = ['前1客户', '前2-10客户', '其他客户']
    colors = [accent, '#60A5FA', muted]
    left = 0
    for s, c, n in zip(shares, colors, names):
        ax3.barh(['2020收入结构'], [s], left=left, color=c, edgecolor=bg, label=n)
        left += s
    ax3.set_xlim(0, 100)
    ax3.set_title('C. 客户集中度', loc='left', fontsize=12, weight='bold')
    ax3.set_xlabel('收入占比（%）')
    leg = ax3.legend(frameon=False, ncol=2, fontsize=8, loc='lower right')
    for t in leg.get_texts():
        t.set_color(txt)
    ax3.text(63, 0.13, f"前10客户 = {metrics.top10_share_2020*100:.1f}%", color=txt, fontsize=10, weight='bold')
    ax3.text(4, -0.34, f"若流失前1客户：约 -{metrics.top1_share_2020*100:.1f}% 收入", color=warn_color, fontsize=9)

    # D: monthly trend
    ax4 = fig.add_subplot(gs[1, :2])
    style_ax(ax4)
    for yr, color, lw in [(2019, muted, 2.2), (2020, accent, 2.6)]:
        d = monthly[monthly['year'] == yr].sort_values('month')
        ax4.plot(d['month'], d['revenue'], marker='o', linewidth=lw, color=color, label=str(yr))
    ax4.set_xticks(range(1, 13))
    ax4.set_title('D. 月度经营节奏', loc='left', fontsize=12, weight='bold')
    ax4.set_xlabel('月份')
    ax4.set_ylabel('收入')
    leg = ax4.legend(frameon=False)
    for t in leg.get_texts():
        t.set_color(txt)
    ax4.set_ylim(bottom=0)
    peak = monthly[monthly['year'] == 2020].sort_values('revenue', ascending=False).iloc[0]
    ax4.annotate(
        f"峰值：{int(peak['month'])}月（{peak['revenue']/1e6:.2f}百万）",
        xy=(peak['month'], peak['revenue']),
        xytext=(peak['month'] + 0.6, peak['revenue'] * 0.78),
        arrowprops=dict(arrowstyle='->', lw=1.2, color=accent),
        fontsize=9,
        color=txt,
    )

    # E: text panel
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.set_facecolor(panel_bg)
    ax5.axis('off')
    ax5.set_title('E. 结论与动作（图内标注）', loc='left', fontsize=12, weight='bold', color=txt)
    summary = (
        f"结论1：2020年收入同比 +{pct_change(metrics.revenue_2019, metrics.revenue_2020):.1f}%，规模显著增长。\n\n"
        f"结论2：客户数保持不变（{metrics.clients_2019}→{metrics.clients_2020}），增长来自“更深经营”。\n"
        f"  - 每客户订单数：{metrics.orders_per_client_2019:.2f}→{metrics.orders_per_client_2020:.2f}（{pct_change(metrics.orders_per_client_2019, metrics.orders_per_client_2020):+.0f}%）\n"
        f"  - 每客户产品覆盖：{metrics.products_per_client_2019:.2f}→{metrics.products_per_client_2020:.2f}（{pct_change(metrics.products_per_client_2019, metrics.products_per_client_2020):+.0f}%）\n\n"
        f"结论3：集中度较高，前10客户贡献 {metrics.top10_share_2020*100:.1f}% 收入。\n"
        f"  - 流失前1客户，预计影响约 {metrics.top1_share_2020*100:.1f}% 收入。\n\n"
        f"建议动作：\n"
        f"  1) 做大11-20名腰部客户\n"
        f"  2) 建立头部客户流失预警\n"
        f"  3) 复制高贡献产品组合到更多客户"
    )
    ax5.text(
        0.02,
        0.98,
        summary,
        va='top',
        ha='left',
        fontsize=10,
        color=txt,
        bbox=dict(boxstyle='round,pad=0.6', facecolor=('#0F172A' if is_dark else '#F8FAFC'), edgecolor=edge),
    )

    title = '业务经营一页总览（管理层·深色版）' if is_dark else '业务经营一页总览（管理层）'
    fig.suptitle(title, fontsize=16, weight='bold', y=0.995, color=txt)
    fig.text(0.01, 0.005, f"数据源：{src} | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=8, color=muted)

    fig.savefig(out, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Chinese one-page business overview images')
    parser.add_argument('--source', type=Path, default=Path('/data/kaggle/Business Analyst (junior).xlsx'))
    parser.add_argument('--light-output', type=Path, default=Path('/workspace/reports/assets/business-analyst-one-page-overview.png'))
    parser.add_argument('--dark-output', type=Path, default=Path('/workspace/reports/assets/business-analyst-one-page-overview-dark.png'))
    args = parser.parse_args()

    font_name = select_chinese_font()
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = [
        font_name,
        'WenQuanYi Micro Hei',
        'Droid Sans Fallback',
        'Noto Sans CJK SC',
        'SimHei',
        'DejaVu Sans',
    ]
    rcParams['axes.unicode_minus'] = False

    # Convert missing-glyph warnings into hard errors so CI can catch font regressions.
    warnings.filterwarnings('error', message='.*Glyph.*missing from font.*', category=UserWarning)

    df = load_data(args.source)
    metrics, monthly = calc_metrics(df)

    render('light', metrics, monthly, args.source, args.light_output, font_name)
    render('dark', metrics, monthly, args.source, args.dark_output, font_name)

    print(f'font={font_name}')
    print(f'light={args.light_output}')
    print(f'dark={args.dark_output}')


if __name__ == '__main__':
    main()
