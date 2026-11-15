#!/usr/bin/env python3
"""
Tổng hợp kết quả thí nghiệm từ hai thư mục:
  - cli_results_v1/   (có nhiều run: run_001..run_N)
  - prompts_results/  (một run duy nhất mỗi mô hình)

Tính toán trung bình (mean) và độ lệch chuẩn (std) cho từng chỉ số,
nhóm theo (strategy, context, model) và (strategy, context).

Xuất ra:
  - aggregated_raw.csv            : toàn bộ dòng kết quả chạy lẻ
  - summary_by_model.csv          : mean ± std theo (strategy, context, model)
  - summary_by_strategy_context.csv: mean ± std theo (strategy, context)
  - tables/latex_table.tex        : bảng LaTeX chuẩn paper
  - tables/markdown_table.md      : bảng Markdown
  - charts/*.png                  : biểu đồ bar (có lỗi std) và boxplot (gộp layout)
  - report.html                   : báo cáo HTML nhúng bảng + biểu đồ

Chạy:
    cd /home/heurix/Documents/CNPMTT/paper/LLM-analysis/automation
    .venv/bin/python aggregate_results.py
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Đường dẫn
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
CLI_RESULTS = BASE / "cli_results_v1"
PROMPTS_RESULTS = BASE / "prompts_results"
OUT = BASE / "aggregation_output"
TABLES = OUT / "tables"
CHARTS = OUT / "charts"
RAW_CSV = OUT / "aggregated_raw.csv"
MODEL_CSV = OUT / "summary_by_model.csv"
SC_CSV = OUT / "summary_by_strategy_context.csv"
LATEX = TABLES / "latex_table.tex"
MD = TABLES / "markdown_table.md"
HTML = OUT / "report.html"

# ---------------------------------------------------------------------------
# Các chỉ số cần thống kê (từ trường summary của analysis_results.json)
# ---------------------------------------------------------------------------
METRICS = [
    ("response_time", "Thời gian phản hồi (s)", "s", False),
    ("compilation_success_rate", "Tỷ lệ biên dịch thành công", "%", True),
    ("execution_success_rate", "Tỷ lệ thực thi thành công", "%", True),
    ("test_success_rate", "Tỷ lệ test thành công", "%", True),
    ("statement_coverage", "Độ phủ câu lệnh", "%", True),
    ("branch_coverage", "Độ phủ nhánh", "%", True),
    ("mutation_score", "Điểm đột biến (mutation score)", "%", True),
    ("total_test_methods", "Số phương thức test", "test", False),
    ("total_assertions", "Tổng số khẳng định", "assert", False),
    ("avg_assertions_per_test", "TB khẳng định/test", "assert/test", False),
    ("methods_tested_count", "Số phương thức được test", "phương thức", False),
    ("total_methods", "Tổng số phương thức", "phương thức", False),
    ("method_coverage_rate", "Tỷ lệ phương thức được test", "%", True),
    ("duplicate_tests_found", "Số test trùng lặp", "test", False),
    ("assertion_quality_score", "Điểm chất lượng khẳng định", "%", True),
    ("exception_quality_score", "Điểm chất lượng ngoại lệ", "%", True),
    ("independence_score", "Điểm độc lập test", "%", True),
    ("naming_quality_score", "Điểm đặt tên", "%", True),
    ("smell_score", "Điểm mùi mã", "%", True),
    ("overall_quality_score", "Điểm chất lượng tổng thể", "%", True),
]

METRIC_KEYS = [m[0] for m in METRICS]
METRIC_LABELS = {m[0]: m[1] for m in METRICS}
METRIC_UNITS = {m[0]: m[2] for m in METRICS}
METRIC_HIGHER_BETTER = {m[0]: m[3] for m in METRICS}

# Tên viết tắt dùng trên biểu đồ (tránh thiếu không gian)
METRIC_SHORT = {
    "test_success_rate": "TestRate",
    "statement_coverage": "StmtCov",
    "branch_coverage": "BranchCov",
    "mutation_score": "MutScore",
    "overall_quality_score": "Quality",
    "response_time": "Time(s)",
}

STRATEGY_SHORT = {
    "simple_prompting": "Simple",
    "chain_of_thought_prompting": "CoT",
}

CONTEXT_SHORT = {
    "interface": "Intf",
    "interface_docstring": "I+Doc",
    "full_context": "Full",
}

MODEL_PREFIX_SHORT = [
    ("openrouter-", "or-"),
    ("gemini-api-", "gapi-"),
    ("groq-", "gq-"),
    ("intern-ai-", "ia-"),
]


def shorten_model(name: str) -> str:
    for prefix, repl in MODEL_PREFIX_SHORT:
        if name.startswith(prefix):
            name = repl + name[len(prefix):]
    return name.replace("-", " ").title()


# ---------------------------------------------------------------------------
# Thu thập dữ liệu
# ---------------------------------------------------------------------------
def extract_summary(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    summary = data.get("summary") or {}
    if not summary:
        return None
    return summary


def parse_path(p: Path, root: Path) -> dict | None:
    """
    Trích toán metadata từ đường dẫn tương đối.
    Cấu trúc: <strategy>/<context>/<model>[/run_N]/analysis_results.json
    """
    try:
        rel = p.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 4:
        return None
    strategy, context, model = parts[0], parts[1], parts[2]
    run_id = None
    if len(parts) >= 5 and re.fullmatch(r"run_\d+", parts[3]):
        run_id = parts[3]
    return {"strategy": strategy, "context": context, "model": model, "run_id": run_id}


def collect() -> list[dict]:
    rows: list[dict] = []
    for root, label in ((CLI_RESULTS, "cli_results_v1"), (PROMPTS_RESULTS, "prompts_results")):
        if not root.exists():
            continue
        for json_path in root.rglob("analysis_results.json"):
            meta = parse_path(json_path, root)
            if not meta:
                continue
            summary = extract_summary(json_path)
            if not summary:
                continue
            row = {"source": label}
            row.update(meta)
            row["response_time"] = summary.get("response_time", summary.get("response_time"))
            for key in METRIC_KEYS:
                if key == "response_time":
                    continue
                row[key] = summary.get(key)
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Tính mean ± std
# ---------------------------------------------------------------------------
def agg_stats(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    records = []
    for keys, grp in df.groupby(group_cols):
        rec = dict(zip(group_cols, keys))
        rec["n"] = len(grp)
        for key in METRIC_KEYS:
            vals = pd.to_numeric(grp[key], errors="coerce").dropna()
            if len(vals) == 0:
                rec[f"{key}_mean"] = np.nan
                rec[f"{key}_std"] = np.nan
                rec[f"{key}_min"] = np.nan
                rec[f"{key}_max"] = np.nan
            else:
                rec[f"{key}_mean"] = round(float(vals.mean()), 3)
                rec[f"{key}_std"] = round(float(vals.std(ddof=1) if len(vals) > 1 else 0.0), 3)
                rec[f"{key}_min"] = round(float(vals.min()), 3)
                rec[f"{key}_max"] = round(float(vals.max()), 3)
        records.append(rec)
    return pd.DataFrame(records)


def mean_std_str(mean: float | None, std: float | None, unit: str) -> str:
    if mean is None or (isinstance(mean, float) and math.isnan(mean)):
        return "–"
    if std is None or (isinstance(std, float) and math.isnan(std)):
        std = 0.0
    return f"{mean:.2f} ± {std:.2f} {unit}"


# ---------------------------------------------------------------------------
# Xuất CSV
# ---------------------------------------------------------------------------
def write_raw_csv(rows: list[dict]) -> None:
    if not rows:
        return
    cols = ["source", "strategy", "context", "model", "run_id"] + METRIC_KEYS
    with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c) for c in cols})


def write_model_csv(df: pd.DataFrame) -> None:
    df.to_csv(MODEL_CSV, index=False, encoding="utf-8")


def write_sc_csv(df: pd.DataFrame) -> None:
    df.to_csv(SC_CSV, index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# Bảng LaTeX / Markdown
# ---------------------------------------------------------------------------
def build_comparison_df(model_df: pd.DataFrame, sc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo bảng so sánh dễ đọc: mỗi hàng là một (strategy, context, model),
    cột là các chỉ số chính dạng "mean ± std".
    """
    core_keys = [
        "test_success_rate", "statement_coverage", "branch_coverage",
        "mutation_score", "compilation_success_rate", "response_time",
        "total_test_methods", "total_assertions", "method_coverage_rate",
        "overall_quality_score",
    ]
    rows = []
    for _, r in model_df.iterrows():
        rec = {
            "Strategy": r["strategy"].replace("_", " ").title(),
            "Context": r["context"].replace("_", " ").title(),
            "Model": r["model"],
            "N": int(r["n"]),
        }
        for key in core_keys:
            rec[METRIC_LABELS[key]] = mean_std_str(
                r.get(f"{key}_mean"), r.get(f"{key}_std"), METRIC_UNITS[key]
            )
        rows.append(rec)
    # Thêm hàng tổng hợp theo (strategy, context)
    for _, r in sc_df.iterrows():
        rec = {
            "Strategy": r["strategy"].replace("_", " ").title(),
            "Context": r["context"].replace("_", " ").title(),
            "Model": "TRUNG BÌNH TẤT CẢ MÔ HÌNH",
            "N": int(r["n"]),
        }
        for key in core_keys:
            rec[METRIC_LABELS[key]] = mean_std_str(
                r.get(f"{key}_mean"), r.get(f"{key}_std"), METRIC_UNITS[key]
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def to_latex(df: pd.DataFrame) -> str:
    caption = (
        "Bảng tóm tắt các chỉ số đánh giá (trung bình ± độ lệch chuẩn) "
        "theo chiến lược prompt, mức ngữ cảnh và mô hình LLM."
    )
    col_fmt = "lll" + "c" * (len(df.columns) - 3)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        f"\\caption{{{caption}}}\\label{{tab:summary}}",
        f"\\begin{{tabular}}{{{col_fmt}}}",
        "\\toprule",
        " & ".join(df.columns) + " \\\\",
        "\\midrule",
    ]
    for _, row in df.iterrows():
        vals = []
        for c in df.columns:
            v = str(row[c])
            v = v.replace("%", "\\%").replace("_", "\\_")
            vals.append(v)
        lines.append(" & ".join(vals) + " \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def to_markdown(df: pd.DataFrame) -> str:
    def esc(v):
        return str(v).replace("|", "\\|").replace("%", "\\%").replace("_", "\\_")
    header = "| " + " | ".join(esc(c) for c in df.columns) + " |"
    sep = "| " + " | ".join("---" for _ in df.columns) + " |"
    body = "\n".join(
        "| " + " | ".join(esc(row[c]) for c in df.columns) + " |" for _, row in df.iterrows()
    )
    lines = [
        "# Bảng tóm tắt kết quả (trung bình ± độ lệch chuẩn)",
        "",
        header,
        sep,
        body,
        "",
        "**Chú ý:** Các giá trị ở dạng `mean ± std` (đơn vị tùy chỉ số). ",
        "Càng cao càng tốt đối với tất cả chỉ số trừ `Thời gian phản hồi`.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Biểu đồ (gộp layout, viết tắt)
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 8,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})

CORE_PLOT_KEYS = [
    "test_success_rate", "statement_coverage", "branch_coverage",
    "mutation_score", "overall_quality_score",
]


def _group_label(strategy: str, context: str) -> str:
    return f"{STRATEGY_SHORT.get(strategy, strategy)} × {CONTEXT_SHORT.get(context, context)}"


def _model_label(model: str) -> str:
    return shorten_model(model)


def plot_model_comparison_grid(model_df: pd.DataFrame) -> None:
    """
    Gộp nhiều plot cùng loại vào 1 layout:
    Mỗi figure là 1 chỉ số (metric), lưới subplots theo (strategy × context),
    mỗi ô vẽ bar các mô hình trong nhóm đó (mean ± std).
    """
    for key in CORE_PLOT_KEYS:
        mean_col, std_col = f"{key}_mean", f"{key}_std"
        sub = model_df.dropna(subset=[mean_col]).copy()
        if sub.empty:
            continue

        groups = sorted(sub.groupby(["strategy", "context"]), key=lambda g: (g[0][0], g[0][1]))
        n_groups = len(groups)
        cols = min(3, n_groups)
        rows = math.ceil(n_groups / cols)

        fig_w = 4.0 * cols + 2.0
        fig_h = 3.2 * rows + 1.5
        fig, axes = plt.subplots(rows, cols, figsize=(fig_w, fig_h), squeeze=False)
        fig.suptitle(f"{METRIC_SHORT[key]} — so sánh mô hình theo nhóm (mean ± std)", fontsize=11, y=1.0)

        for idx, ((strategy, context), grp) in enumerate(groups):
            r = idx // cols
            c = idx % cols
            ax = axes[r][c]
            grp = grp.sort_values(mean_col, ascending=False)
            labels = [_model_label(m) for m in grp["model"]]
            means = grp[mean_col].values
            stds = grp[std_col].fillna(0).values
            n = len(labels)

            x = np.arange(n)
            colors = plt.cm.tab10(np.linspace(0, 1, n))
            bars = ax.bar(x, means, yerr=stds, capsize=2, color=colors,
                          edgecolor="black", linewidth=0.4)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
            ax.set_title(_group_label(strategy, context), fontsize=8, pad=4)
            ax.set_ylim(bottom=0, top=max(means.max() * 1.3, 10))
            ax.tick_params(axis="y", labelsize=6)
            for bar, m in zip(bars, means):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(means) * 0.02,
                        f"{m:.1f}", ha="center", va="bottom", fontsize=5, rotation=0)

        # Ẩn subplot thừa
        for idx in range(n_groups, rows * cols):
            r = idx // cols
            c = idx % cols
            axes[r][c].set_visible(False)

        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(CHARTS / f"grid_{key}.png", bbox_inches="tight")
        plt.close(fig)


def plot_top14_grid(model_df: pd.DataFrame) -> None:
    """1 figure, 5 subplot (theo metric), top 14 mô hình theo mean, gộp chung layout."""
    fig, axes = plt.subplots(1, len(CORE_PLOT_KEYS), figsize=(4.2 * len(CORE_PLOT_KEYS) + 1, 4.0))
    if len(CORE_PLOT_KEYS) == 1:
        axes = [axes]

    for ax, key in zip(axes, CORE_PLOT_KEYS):
        mean_col, std_col = f"{key}_mean", f"{key}_std"
        sub = model_df.dropna(subset=[mean_col]).copy()
        if sub.empty:
            ax.set_visible(False)
            continue
        sub = sub.sort_values(mean_col, ascending=False).head(14)
        labels = [_model_label(m) for m in sub["model"]]
        means = sub[mean_col].values
        stds = sub[std_col].fillna(0).values
        n = len(labels)

        x = np.arange(n)
        colors = plt.cm.tab10(np.linspace(0, 1, n))
        bars = ax.bar(x, means, yerr=stds, capsize=2, color=colors,
                      edgecolor="black", linewidth=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
        ax.set_title(f"{METRIC_SHORT[key]} (Top14)", fontsize=9, pad=6)
        ax.set_ylim(bottom=0, top=max(means.max() * 1.3, 10))
        ax.tick_params(axis="y", labelsize=7)
        for bar, m in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(means) * 0.02,
                    f"{m:.1f}", ha="center", va="bottom", fontsize=5, rotation=0)

    fig.tight_layout()
    fig.savefig(CHARTS / "grid_top14.png", bbox_inches="tight")
    plt.close(fig)


def plot_strategy_context_grouped(sc_df: pd.DataFrame) -> None:
    """Grouped bar so sánh (strategy × context) × metric, gộp 1 layout, tên viết tắt."""
    keys = ["test_success_rate", "statement_coverage", "branch_coverage", "mutation_score", "overall_quality_score"]
    labels = [_group_label(r["strategy"], r["context"]) for _, r in sc_df.iterrows()]
    x = np.arange(len(labels))
    width = 0.15
    fig, ax = plt.subplots(figsize=(2.2 * len(labels) + 2, 4.6))
    for i, key in enumerate(keys):
        means = sc_df[f"{key}_mean"].fillna(0).values
        stds = sc_df[f"{key}_std"].fillna(0).values
        ax.bar(x + (i - 2) * width, means, width, yerr=stds, capsize=2,
               label=METRIC_SHORT[key])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Giá trị (%)", fontsize=9)
    ax.set_title("Chiến lược × ngữ cảnh — trung bình tất cả mô hình (mean ± std)", fontsize=10, pad=10)
    ax.legend(fontsize=7, ncol=5, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    ax.set_ylim(bottom=0, top=105)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHARTS / "grouped_strategy_context.png", bbox_inches="tight")
    plt.close(fig)


def plot_box_grid(raw_df: pd.DataFrame) -> None:
    """Boxplot gộp 5 metric theo strategy vào 1 layout (5 subplot)."""
    fig, axes = plt.subplots(1, len(CORE_PLOT_KEYS), figsize=(4.0 * len(CORE_PLOT_KEYS) + 1, 4.2))
    if len(CORE_PLOT_KEYS) == 1:
        axes = [axes]

    for ax, key in zip(axes, CORE_PLOT_KEYS):
        sub = raw_df.dropna(subset=[key]).copy()
        if sub.empty:
            ax.set_visible(False)
            continue
        groups = list(sub.groupby("strategy"))
        if len(groups) < 2:
            ax.set_visible(False)
            continue
        data = [grp[key].values for _, grp in groups]
        labels = [STRATEGY_SHORT.get(g, g) for g, _ in groups]
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True,
                        medianprops={"color": "black"},
                        whiskerprops={"linewidth": 1.0},
                        capprops={"linewidth": 1.0})
        for patch, color in zip(bp["boxes"], plt.cm.Set2.colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title(f"{METRIC_SHORT[key]} theo chiến lược", fontsize=9, pad=6)
        ax.set_ylabel(METRIC_UNITS[key], fontsize=8)
        ax.tick_params(axis="x", labelsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(CHARTS / "grid_boxplot.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Báo cáo HTML
# ---------------------------------------------------------------------------
def build_html(model_df: pd.DataFrame, sc_df: pd.DataFrame, chart_files: list[Path]) -> str:
    cmp_df = build_comparison_df(model_df, sc_df)
    html_table = cmp_df.to_html(index=False, border=0, classes="data-table", escape=False)

    scale_html = """
    <h3>Thang đánh giá kết quả</h3>
    <table class="data-table">
      <tr><th>Chỉ số (tỷ lệ %)</th><th>Xuất sắc</th><th>Tốt</th><th>Khá</th><th>Yếu</th></tr>
      <tr><td>Độ phủ / Chất lượng / Thành công</td><td>≥ 90</td><td>80–89</td><td>70–79</td><td>&lt; 70</td></tr>
      <tr><td>Độ phủ nhánh (branch coverage)</td><td>≥ 80</td><td>60–79</td><td>40–59</td><td>&lt; 40</td></tr>
      <tr><td>Điểm đột biến (mutation score)</td><td>≥ 50</td><td>30–49</td><td>15–29</td><td>&lt; 15</td></tr>
      <tr><td>Thời gian phản hồi</td><td>&lt; 30s</td><td>30–60s</td><td>60–120s</td><td>&gt; 120s</td></tr>
    </table>
    """

    # Phân loại chart theo loại
    grid_metric = [cf for cf in chart_files if cf.name.startswith("grid_") and not cf.name.startswith("grid_top14") and not cf.name.startswith("grid_boxplot")]
    top14 = [cf for cf in chart_files if cf.name == "grid_top14.png"]
    grouped = [cf for cf in chart_files if cf.name == "grouped_strategy_context.png"]
    boxgrid = [cf for cf in chart_files if cf.name == "grid_boxplot.png"]

    def img_block(files, col_w="320px"):
        out = ""
        for cf in sorted(files):
            out += f'<div class="chart"><img src="charts/{cf.name}" alt="{cf.stem}" style="max-width:{col_w};"><p class="chart-caption">{cf.stem}</p></div>\n'
        return out

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo cáo tổng hợp kết quả thí nghiệm LLM</title>
<style>
  body {{ font-family: DejaVu Sans, sans-serif; margin: 24px; color: #222; }}
  h1, h2, h3 {{ color: #1a3a5c; }}
  table.data-table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 13px; }}
  table.data-table th, table.data-table td {{ border: 1px solid #999; padding: 6px 8px; text-align: center; }}
  table.data-table th {{ background: #eef3f8; font-weight: bold; }}
  table.data-table tr:nth-child(even) {{ background: #f7f9fc; }}
  .section {{ margin: 32px 0; page-break-inside: avoid; }}
  .chart {{ margin: 16px 0; text-align: center; page-break-inside: avoid; }}
  .chart img {{ max-width: 100%; border: 1px solid #ddd; }}
  .chart-caption {{ font-size: 12px; color: #555; margin-top: 4px; }}
  .note {{ font-size: 12px; color: #666; }}
  .two-col {{ display: flex; gap: 24px; flex-wrap: wrap; }}
  .two-col > div {{ flex: 1; min-width: 280px; }}
  .group-title {{ font-size: 14px; font-weight: bold; color: #1a3a5c; margin-top: 20px; }}
</style>
</head>
<body>
<h1>Báo cáo tổng hợp kết quả thí nghiệm tạo test đơn vị bằng LLM</h1>
<p class="note">Nguồn dữ liệu: <code>cli_results_v1/</code> và <code>prompts_results/</code>. Tất cả giá trị ở dạng <b>trung bình ± độ lệch chuẩn</b> (mean ± std).</p>

<div class="section">
  <h2>1. Bảng tóm tắt so sánh</h2>
  {html_table}
  <p class="note">Cột "N" là số lần chạy được tổng hợp. "TRUNG BÌNH TẤT CẢ MÔ HÌNH" là tổng hợp theo (strategy, context) toàn bộ mô hình.</p>
</div>

<div class="section">
  <h2>2. Thang đánh giá (dùng cho phân tích paper)</h2>
  {scale_html}
</div>

<div class="section two-col">
  <h2>3. Biểu đồ số liệu (gộp layout, viết tắt tên)</h2>
  <div class="group-title">3a. So sánh mô hình theo nhóm — mỗi figure là 1 chỉ số, lưới các nhóm (strategy × context)</div>
  {img_block(grid_metric)}
  <div class="group-title">3b. Top 14 mô hình — 5 chỉ số trong 1 figure</div>
  {img_block(top14)}
  <div class="group-title">3c. Chiến lược × ngữ cảnh (grouped bar, 5 chỉ số)</div>
  {img_block(grouped)}
  <div class="group-title">3d. Boxplot phân phối — 5 chỉ số trong 1 figure</div>
  {img_block(boxgrid)}
</div>

<div class="section">
  <h2>4. Tệp xuất ra</h2>
  <ul>
    <li><code>aggregation_output/aggregated_raw.csv</code> — dữ liệu thô từng lần chạy</li>
    <li><code>aggregation_output/summary_by_model.csv</code> — mean ± std theo (strategy, context, model)</li>
    <li><code>aggregation_output/summary_by_strategy_context.csv</code> — mean ± std theo (strategy, context)</li>
    <li><code>aggregation_output/tables/latex_table.tex</code> — bảng LaTeX chèn trực tiếp vào paper</li>
    <li><code>aggregation_output/tables/markdown_table.md</code> — bảng Markdown</li>
    <li><code>aggregation_output/charts/</code> — tất cả biểu đồ PNG</li>
  </ul>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)

    rows = collect()
    print(f"[+] Thu thập được {len(rows)} dòng kết quả chạy lẻ.")
    if not rows:
        print("[!] Không tìm thấy analysis_results.json nào. Kiểm tra lại đường dẫn.")
        return

    raw_df = pd.DataFrame(rows)
    write_raw_csv(rows)

    model_df = agg_stats(raw_df, ["strategy", "context", "model"])
    sc_df = agg_stats(raw_df, ["strategy", "context"])

    write_model_csv(model_df)
    write_sc_csv(sc_df)

    cmp_df = build_comparison_df(model_df, sc_df)
    LATEX.write_text(to_latex(cmp_df), encoding="utf-8")
    MD.write_text(to_markdown(cmp_df), encoding="utf-8")

    plot_model_comparison_grid(model_df)
    plot_top14_grid(model_df)
    plot_strategy_context_grouped(sc_df)
    plot_box_grid(raw_df)
    chart_files = sorted(CHARTS.glob("*.png"))
    print(f"[+] Sinh {len(chart_files)} biểu đồ vào {CHARTS}")

    HTML.write_text(build_html(model_df, sc_df, chart_files), encoding="utf-8")
    print(f"[+] Báo cáo HTML: {HTML}")
    print(f"[+] Bảng LaTeX: {LATEX}")
    print(f"[+] Bảng Markdown: {MD}")
    print(f"[+] CSV chi tiết: {MODEL_CSV}")
    print(f"[+] CSV chiến lược×ngữ cảnh: {SC_CSV}")
    print("[+] Hoàn tất.")


if __name__ == "__main__":
    main()
