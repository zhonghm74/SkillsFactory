# Business Analyst (junior) 可视化分析与 Storytelling 报告

- 数据源：`/data/kaggle/Business Analyst (junior).xlsx`
- 生成时间：2026-04-02 08:00:15
- 口径：剔除无 `delivery_date` 或无 `delivery_amount` 的记录，并过滤非正金额。

## Executive Title
**在客户数不变的情况下，2020 年通过订单频次与产品扩展，实现营收显著增长，但集中度风险上升。**

## Big Idea
**The single thing this audience must understand is：增长质量来自“更高交易密度 + 更宽产品覆盖”，下一步应在稳增长同时降低头部依赖。**

## 1) 情境与数据质量（Context）

- 原始记录：**1,049,082**；有效记录：**778**。
- 缺失交付日期：**1,048,304**（主要为空白尾行）；缺失金额：**494**。
- 本报告结论基于有效交付流水，适用于经营分析与管理复盘。

## 2) 证据一：年度规模增长（Evidence A）

![Yearly Revenue Comparison](assets/yearly-revenue-comparison.png)

- 2020 营收：**16,846,277**，较 2019 同比 **77.13%**。
- 2020 订单数：**221**，同比 **225.00%**。
- 2020 产品数：**99**，同比 **54.69%**。

**Annotation:** 增长并非来自客户数扩张（客户数保持 21），而是来自更高频次交易和更丰富产品覆盖。

## 3) 证据二：月度节奏变化（Evidence B）

![Monthly Revenue Trend](assets/monthly-revenue-trend.png)

- 2020 峰值出现在 **6 月**，当月营收 **4,143,440**。
- 2020 多数月份高于 2019，显示增长具有持续性，但个别月份波动明显。

**Annotation:** 经营节奏可能存在活动驱动或供给节拍效应，建议纳入月度预警与产销协同计划。

## 4) 证据三：客户与产品结构（Evidence C）

![Top 10 Clients 2020](assets/top10-clients-2020.png)

![Top 10 Products 2020](assets/top10-products-2020.png)

- Top10 客户营收占比：**67.40%**。
- Top10 产品营收占比：**40.34%**。

**Annotation:** 头部贡献高可带来效率，但也意味着波动放大与议价风险，需要分层经营策略。

## 5) 决策建议（So What / Now What）

1. **稳增长**：围绕已验证高贡献产品，推进交叉销售，延续交易密度提升。
2. **降风险**：设置 Top 客户与 Top 产品集中度阈值（例如 Top10 客户占比预警线），月度自动监控。
3. **提质量**：建立月度复盘模板，跟踪“订单频次、产品覆盖、客单价分层、峰谷原因”。
4. **数据治理**：在 ETL 中拦截空日期与异常值，减少分析噪声。

## 6) 可视化完整性与可访问性说明

- 图表类型与目标匹配：年度/结构对比采用 bar，趋势采用 line。
- 柱状图均使用 0 基线；线图显式披露基线。
- 采用“中性色 + 单一强调色”并配合直接标注，避免仅靠颜色传达。
- 对应 chart spec 已生成于 `reports/chart-specs/`，并可使用 data-visualization 脚本校验。