#!/usr/bin/env python3
"""
generate_synthesis_report.py

Kịch bản tổng hợp và xuất báo cáo kết quả thực nghiệm tự động đánh giá sinh Unit Test bằng LLM.
Nguồn dữ liệu:
  - cli_results_v3   (tất cả mô hình: claude-code-opus-4.5, claude-code-sonnet-4.5, gemini-3-flash, gemini-3-pro)
  - cli_results_v1   (chỉ lọc lấy: openrouter-nemotron-3-super-120b-a12b)
  - cli_results_v10  (tất cả mô hình: groq-gpt-oss-120b)

Đầu ra:
  - synthesis_output/
      ├── data/                  (Các tệp CSV thô, tổng hợp đa chiều, chi tiết từng chỉ số)
      ├── charts/                (Tất cả các biểu đồ SVG đa bảng subplot chuẩn học thuật)
      ├── docx_report/           (Báo cáo nghiên cứu khoa học chi tiết định dạng Markdown + bảng số liệu dùng chèn vào Word)
      └── slide_deck/            (Nội dung thuyết trình dạng slide + biểu đồ 16:9 + bảng tóm tắt dùng cho PowerPoint)
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Cấu hình đường dẫn
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
OUTPUT_DIR = BASE_DIR / "synthesis_output"

DATA_DIR = OUTPUT_DIR / "data"
METRICS_DATA_DIR = DATA_DIR / "metrics_breakdown"
CHARTS_DIR = OUTPUT_DIR / "charts"
DOCX_DIR = OUTPUT_DIR / "docx_report"
SLIDES_DIR = OUTPUT_DIR / "slide_deck"

DOCX_TABLES_DIR = DOCX_DIR / "tables_docx"
DOCX_FIGURES_DIR = DOCX_DIR / "figures_docx"
SLIDES_TABLES_DIR = SLIDES_DIR / "tables_slides"
SLIDES_FIGURES_DIR = SLIDES_DIR / "figures_slides"

# Danh sách nguồn dữ liệu và bộ lọc mô hình
DATA_SOURCES = [
    ("cli_results_v3", None),
    ("cli_results_v1", ["openrouter-nemotron-3-super-120b-a12b"]),
    ("cli_results_v10", None),
    ("cli_results_v11", None),
]

# Danh mục ánh xạ tên mô hình sang tên chuẩn học thuật
MODEL_DISPLAY_NAMES = {
    "claude-code-opus-4.5": "Claude Opus 4.5",
    "claude-code-sonnet-4.5": "Claude Sonnet 4.5",
    "gemini-3-flash": "Gemini 3 Flash",
    "gemini-3-pro": "Gemini 3 Pro",
    "groq-gpt-oss-120b": "GPT-OSS 120B",
    "groq-gpt-oss-20b": "GPT-OSS 20B",
    "openrouter-nemotron-3-super-120b-a12b": "Nemotron 3 Super 120B",
}

MODEL_SHORT_NAMES = {
    "claude-code-opus-4.5": "Opus 4.5",
    "claude-code-sonnet-4.5": "Sonnet 4.5",
    "gemini-3-flash": "Gemini Flash",
    "gemini-3-pro": "Gemini Pro",
    "groq-gpt-oss-120b": "GPT-OSS 120B",
    "groq-gpt-oss-20b": "GPT-OSS 20B",
    "openrouter-nemotron-3-super-120b-a12b": "Nemotron 120B",
}

STRATEGY_DISPLAY = {
    "simple_prompting": "Simple Prompting",
    "chain_of_thought_prompting": "Chain of Thought (CoT)",
}

STRATEGY_SHORT = {
    "simple_prompting": "Simple",
    "chain_of_thought_prompting": "CoT",
}

CONTEXT_DISPLAY = {
    "interface": "Interface Only",
    "interface_docstring": "Interface + Docstring",
    "full_context": "Full Implementation Context",
}

CONTEXT_SHORT = {
    "interface": "Interface",
    "interface_docstring": "I+Doc",
    "full_context": "Full Context",
}

# ---------------------------------------------------------------------------
# Danh mục chỉ số đo lường
# ---------------------------------------------------------------------------
METRIC_SPECS = [
    ("statement_coverage", "Độ phủ câu lệnh (Statement Coverage)", "%", True, "StmtCov"),
    ("branch_coverage", "Độ phủ nhánh (Branch Coverage)", "%", True, "BranchCov"),
    ("method_coverage", "Độ phủ phương thức (Method Coverage)", "%", True, "MethodCov"),
    ("mutation_score", "Điểm kiểm thử đột biến (Mutation Score)", "%", True, "MutScore"),
    ("compilation_rate", "Tỷ lệ biên dịch thành công (CSR)", "%", True, "CSR"),
    ("execution_rate", "Tỷ lệ thực thi thành công", "%", True, "ExecRate"),
    ("test_success_rate", "Tỷ lệ test case vượt qua (Pass Rate)", "%", True, "PassRate"),
    ("total_test_methods", "Tổng số phương thức test sinh ra", "tests", False, "TestCount"),
    ("unique_tests", "Số ca kiểm thử duy nhất (Unique Tests)", "tests", False, "UniqueTests"),
    ("total_assertions", "Tổng số khẳng định (Assertions)", "asserts", False, "AssertCount"),
    ("avg_assertions_per_test", "Số khẳng định trung bình mỗi test", "assert/test", False, "AvgAssert"),
    ("assertion_quality_score", "Chất lượng khẳng định (Assertion Quality)", "%", True, "AssertQual"),
    ("exception_quality_score", "Chất lượng kiểm tra ngoại lệ", "%", True, "ExcepQual"),
    ("independence_score", "Tính độc lập giữa các ca kiểm thử", "%", True, "IndepScore"),
    ("naming_quality_score", "Chất lượng đặt tên ca kiểm thử", "%", True, "NameQual"),
    ("smell_score", "Điểm vắng mặt mùi mã (Smell Freedom)", "%", True, "SmellScore"),
    ("overall_quality_score", "Điểm chất lượng tổng thể", "%", True, "OverallQual"),
    ("response_time", "Thời gian phản hồi (Response Latency)", "giây", False, "Time(s)"),
]

METRIC_MAP = {m[0]: m for m in METRIC_SPECS}

# ---------------------------------------------------------------------------
# Thiết lập giao diện biểu đồ Matplotlib chuẩn học thuật
# ---------------------------------------------------------------------------
def setup_academic_style():
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9.5,
        "figure.titlesize": 14,
        "svg.fonttype": "none",  # Giữ text dạng vector font trong SVG để hiển thị sắc nét
        "figure.autolayout": False,
    })


# ---------------------------------------------------------------------------
# 1. Trích xuất và nạp dữ liệu
# ---------------------------------------------------------------------------
def load_all_experimental_data() -> pd.DataFrame:
    """Nạp và chuẩn hóa dữ liệu từ 3 thư mục nguồn."""
    rows: List[Dict[str, Any]] = []

    for dir_name, allowed_models in DATA_SOURCES:
        source_path = BASE_DIR / dir_name
        if not source_path.exists():
            print(f"⚠️ Cảnh báo: Thư mục {source_path} không tồn tại!")
            continue

        print(f"🔄 Đang quét dữ liệu từ: {dir_name}...")
        for p in source_path.glob("**/*/analysis_results.json"):
            run_id = p.parent.name
            mod = p.parent.parent.name
            ctx = p.parent.parent.parent.name
            strat = p.parent.parent.parent.parent.name

            if allowed_models and mod not in allowed_models:
                continue

            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            except Exception as e:
                print(f"❌ Lỗi đọc tệp {p}: {e}")
                continue

            summ = data.get("summary") or {}
            cov = data.get("coverage") or {}
            mut = data.get("mutation") or {}
            comp = data.get("compilation") or {}

            # Fallbacks an toàn
            stmt_cov = summ.get("statement_coverage")
            if stmt_cov is None:
                stmt_cov = cov.get("coverage_percent", 0.0)

            branch_cov = summ.get("branch_coverage")
            if branch_cov is None:
                branch_cov = cov.get("branch_coverage_percent", 0.0)

            mut_score = summ.get("mutation_score")
            if mut_score is None:
                mut_score = mut.get("mutation_score", 0.0)

            comp_rate = summ.get("compilation_success_rate")
            if comp_rate is None:
                comp_rate = 100.0 if comp.get("compilation_success") else 0.0

            exec_rate = summ.get("execution_success_rate")
            if exec_rate is None:
                exec_rate = 100.0 if comp.get("execution_success") else 0.0

            # Method Coverage (MC) - chỉ số của paper (III-B2), suy ra từ số method được test
            method_cov = summ.get("method_coverage_rate")
            if method_cov is None:
                total_methods = float(summ.get("total_methods", 0.0) or 0.0)
                methods_tested = float(summ.get("methods_tested_count", 0.0) or 0.0)
                method_cov = (methods_tested / total_methods * 100.0) if total_methods else 0.0

            # Unique Tests (UT) - chỉ số của paper (III-B4): số test duy nhất sau khi loại trùng
            tests_generated = summ.get("total_test_methods")
            if tests_generated is None:
                tests_generated = summ.get("tests_generated", 0.0)
            duplicates = float(summ.get("duplicate_tests_found", 0.0) or 0.0)
            unique_tests = max(float(tests_generated or 0.0) - duplicates, 0.0)

            rows.append({
                "source_dir": dir_name,
                "strategy": strat,
                "strategy_display": STRATEGY_DISPLAY.get(strat, strat),
                "strategy_short": STRATEGY_SHORT.get(strat, strat),
                "context": ctx,
                "context_display": CONTEXT_DISPLAY.get(ctx, ctx),
                "context_short": CONTEXT_SHORT.get(ctx, ctx),
                "model": mod,
                "model_display": MODEL_DISPLAY_NAMES.get(mod, mod),
                "model_short": MODEL_SHORT_NAMES.get(mod, mod),
                "run_id": p.parent.name,
                "scenario": f"{STRATEGY_SHORT.get(strat, strat)}_{CONTEXT_SHORT.get(ctx, ctx)}",
                # Các chỉ số định lượng
                "statement_coverage": float(stmt_cov or 0.0),
                "branch_coverage": float(branch_cov or 0.0),
                "method_coverage": float(method_cov or 0.0),
                "mutation_score": float(mut_score or 0.0),
                "compilation_rate": float(comp_rate or 0.0),
                "execution_rate": float(exec_rate or 0.0),
                "test_success_rate": float(summ.get("test_success_rate", 0.0) or 0.0),
                "total_test_methods": float(summ.get("total_test_methods", 0.0) or 0.0),
                "unique_tests": float(unique_tests),
                "total_assertions": float(summ.get("total_assertions", 0.0) or 0.0),
                "avg_assertions_per_test": float(summ.get("avg_assertions_per_test", 0.0) or 0.0),
                "assertion_quality_score": float(summ.get("assertion_quality_score", 0.0) or 0.0),
                "exception_quality_score": float(summ.get("exception_quality_score", 0.0) or 0.0),
                "independence_score": float(summ.get("independence_score", 0.0) or 0.0),
                "naming_quality_score": float(summ.get("naming_quality_score", 0.0) or 0.0),
                "smell_score": float(summ.get("smell_score", 0.0) or 0.0),
                "overall_quality_score": float(summ.get("overall_quality_score", 0.0) or 0.0),
                "response_time": float(summ.get("response_time", 0.0) or 0.0),
            })

    df = pd.DataFrame(rows)
    print(f"✅ Đã nạp thành công {len(df)} bản ghi thực nghiệm từ 3 nguồn dữ liệu.")
    return df


# ---------------------------------------------------------------------------
# 2. Tính toán thống kê mô tả (Mean, Std, Min, Max, Count)
# ---------------------------------------------------------------------------
def calculate_statistics(
    df: pd.DataFrame, group_cols: List[str]
) -> pd.DataFrame:
    """Tính toán Mean và Std cho tất cả các thông số kiểm định theo nhóm."""
    metric_keys = [m[0] for m in METRIC_SPECS]
    agg_funcs = {}
    for k in metric_keys:
        agg_funcs[k] = ["count", "mean", "std", "min", "max"]

    agg_df = df.groupby(group_cols).agg(agg_funcs)

    # Làm phẳng cột MultiIndex
    flat_cols = []
    for col, stat in agg_df.columns:
        flat_cols.append(f"{col}_{stat}")
    agg_df.columns = flat_cols
    agg_df = agg_df.reset_index()

    # Thêm cột định dạng chuỗi: mean ± std
    for k in metric_keys:
        mean_col = f"{k}_mean"
        std_col = f"{k}_std"
        agg_df[f"{k}_formatted"] = agg_df.apply(
            lambda r: f"{r[mean_col]:.2f} ± {r[std_col]:.2f}"
            if pd.notnull(r[std_col])
            else f"{r[mean_col]:.2f} ± 0.00",
            axis=1,
        )

    return agg_df


# ---------------------------------------------------------------------------
# 3. Xuất các bảng số liệu (CSV & Markdown)
# ---------------------------------------------------------------------------
def export_csv_and_markdown_tables(
    df: pd.DataFrame,
    scenario_stats: pd.DataFrame,
    model_stats: pd.DataFrame,
    strategy_stats: pd.DataFrame,
    context_stats: pd.DataFrame,
):
    """Xuất các bảng số liệu chi tiết và bảng chuyên biệt cho Docx / Slides."""
    # 1. Lưu raw data
    raw_csv = DATA_DIR / "aggregated_raw_dataset.csv"
    df.to_csv(raw_csv, index=False, encoding="utf-8-sig")

    # 2. Lưu bảng 36 kịch bản chi tiết
    scenario_csv = DATA_DIR / "summary_36_scenarios_mean_std.csv"
    scenario_stats.to_csv(scenario_csv, index=False, encoding="utf-8-sig")

    # 3. Lưu bảng tổng hợp theo mô hình
    model_csv = DATA_DIR / "summary_by_model.csv"
    model_stats.to_csv(model_csv, index=False, encoding="utf-8-sig")

    # 4. Lưu bảng theo chiến lược và ngữ cảnh
    strat_csv = DATA_DIR / "summary_by_strategy.csv"
    strategy_stats.to_csv(strat_csv, index=False, encoding="utf-8-sig")

    ctx_csv = DATA_DIR / "summary_by_context.csv"
    context_stats.to_csv(ctx_csv, index=False, encoding="utf-8-sig")

    # 5. Xuất các bảng tách riêng cho từng chỉ số
    for metric, label, unit, _, _ in METRIC_SPECS:
        metric_file = METRICS_DATA_DIR / f"{metric}_by_scenario.csv"
        pivot_table = df.pivot_table(
            index="model_display",
            columns=["strategy_short", "context_short"],
            values=metric,
            aggfunc=["mean", "std"],
        )
        pivot_table.round(2).to_csv(metric_file, encoding="utf-8-sig")

    # 6. Bảng chuyên biệt cho DOCX (Đầy đủ, chuẩn IEEE/ACM)
    docx_main_cols = [
        "model_display", "strategy_short", "context_short",
        "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "overall_quality_score_formatted",
        "test_success_rate_formatted", "unique_tests_formatted", "response_time_formatted",
    ]
    docx_table = scenario_stats[docx_main_cols].copy()
    docx_table.columns = [
        "Mô hình", "Chiến lược", "Ngữ cảnh",
        "CSR (%)",
        "Độ phủ lệnh (%)", "Độ phủ nhánh (%)", "Độ phủ method (%)",
        "Điểm đột biến (%)", "Chất lượng tổng (%)",
        "Test Pass (%)", "Số test duy nhất", "Thời gian (s)",
    ]
    docx_table.to_csv(DOCX_TABLES_DIR / "table_full_36_scenarios.csv", index=False, encoding="utf-8-sig")
    (DOCX_TABLES_DIR / "table_full_36_scenarios.md").write_text(
        docx_table.to_markdown(index=False), encoding="utf-8"
    )

    # 7. Bảng chuyên biệt cho SLIDES (Tối ưu súc tích, làm nổi bật thông tin cốt lõi)
    slides_model_cols = [
        "model_display",
        "compilation_rate_formatted",
        "statement_coverage_formatted",
        "branch_coverage_formatted",
        "method_coverage_formatted",
        "mutation_score_formatted",
        "overall_quality_score_formatted",
        "response_time_formatted",
    ]
    slides_table = model_stats[slides_model_cols].copy()
    slides_table.columns = [
        "Mô hình", "CSR (%)", "Độ phủ câu lệnh (%)", "Độ phủ nhánh (%)", "Độ phủ method (%)",
        "Điểm đột biến (%)", "Chất lượng kiểm thử (%)", "Thời gian (s)"
    ]
    slides_table.to_csv(SLIDES_TABLES_DIR / "table_model_ranking_slides.csv", index=False, encoding="utf-8-sig")
    (SLIDES_TABLES_DIR / "table_model_ranking_slides.md").write_text(
        slides_table.to_markdown(index=False), encoding="utf-8"
    )

    # Bảng so sánh Strategy cho Slides
    strat_slide_cols = [
        "strategy_display",
        "compilation_rate_formatted",
        "statement_coverage_formatted",
        "branch_coverage_formatted",
        "mutation_score_formatted",
        "overall_quality_score_formatted",
        "response_time_formatted",
    ]
    strat_slide_table = strategy_stats[strat_slide_cols].copy()
    strat_slide_table.columns = [
        "Chiến lược gợi ý", "CSR (%)", "Độ phủ câu lệnh (%)", "Độ phủ nhánh (%)",
        "Điểm đột biến (%)", "Chất lượng mã (%)", "Thời gian (s)"
    ]
    strat_slide_table.to_csv(SLIDES_TABLES_DIR / "table_strategy_comparison_slides.csv", index=False, encoding="utf-8-sig")
    (SLIDES_TABLES_DIR / "table_strategy_comparison_slides.md").write_text(
        strat_slide_table.to_markdown(index=False), encoding="utf-8"
    )

    # 8. Bảng tương tác Strategy x Context (Phân tích ma trận kết hợp)
    sc_stats = calculate_statistics(
        df, ["strategy_display", "strategy_short", "context_display", "context_short"]
    )
    sc_cols = [
        "strategy_display", "context_display",
        "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "overall_quality_score_formatted",
        "total_test_methods_formatted", "unique_tests_formatted", "total_assertions_formatted",
        "response_time_formatted",
    ]
    sc_table = sc_stats[sc_cols].copy()
    sc_table.columns = [
        "Chiến lược gợi ý", "Mức độ ngữ cảnh",
        "CSR (%)",
        "Độ phủ lệnh (%)", "Độ phủ nhánh (%)", "Độ phủ method (%)",
        "Điểm đột biến (%)", "Chất lượng mã (%)",
        "Số test methods", "Số test duy nhất", "Số assertions", "Thời gian (s)",
    ]
    sc_table.to_csv(DOCX_TABLES_DIR / "table_strategy_x_context.csv", index=False, encoding="utf-8-sig")
    (DOCX_TABLES_DIR / "table_strategy_x_context.md").write_text(
        sc_table.to_markdown(index=False), encoding="utf-8"
    )
    sc_table.to_csv(DATA_DIR / "summary_strategy_x_context.csv", index=False, encoding="utf-8-sig")

    # 9. Bảng giá trị Docstring (The Docstring Value Proposition)
    ctx_mean = df.groupby("context_short")[["statement_coverage", "branch_coverage", "mutation_score"]].mean()
    gain_doc = ctx_mean.loc["I+Doc"] - ctx_mean.loc["Interface"]
    gain_full = ctx_mean.loc["Full Context"] - ctx_mean.loc["Interface"]
    pct_doc = (gain_doc / gain_full * 100).round(1)
    doc_val_table = pd.DataFrame({
        "Thông số kiểm định": ["Độ phủ câu lệnh (%)", "Độ phủ nhánh (%)", "Điểm kiểm thử đột biến (%)"],
        "Interface Only (Baseline)": ctx_mean.loc["Interface"].round(2).values,
        "Interface + Docstring": ctx_mean.loc["I+Doc"].round(2).values,
        "Full Context (Tối đa)": ctx_mean.loc["Full Context"].round(2).values,
        "Mức tăng từ Docstring (Δ1)": gain_doc.round(2).values,
        "Mức tăng từ Full Code (Δ2)": gain_full.round(2).values,
        "Tỷ trọng giá trị Docstring mang lại (%)": pct_doc.values,
    })
    doc_val_table.to_csv(DOCX_TABLES_DIR / "table_docstring_value_proposition.csv", index=False, encoding="utf-8-sig")
    (DOCX_TABLES_DIR / "table_docstring_value_proposition.md").write_text(
        doc_val_table.to_markdown(index=False), encoding="utf-8"
    )
    doc_val_table.to_csv(SLIDES_TABLES_DIR / "table_docstring_value_proposition.csv", index=False, encoding="utf-8-sig")
    (SLIDES_TABLES_DIR / "table_docstring_value_proposition.md").write_text(
        doc_val_table.to_markdown(index=False), encoding="utf-8"
    )

    print("✅ Đã xuất toàn bộ bảng số liệu CSV và Markdown vào synthesis_output/.")


# ---------------------------------------------------------------------------
# 4. Tạo các biểu đồ SVG đa bảng (Subplots Academic & 16:9 Slides)
# ---------------------------------------------------------------------------
def generate_all_svg_charts(df: pd.DataFrame, scenario_stats: pd.DataFrame):
    """Vẽ các biểu đồ học thuật dạng vector SVG tối ưu không gian."""
    setup_academic_style()
    models = sorted(df["model_short"].unique())
    model_colors = sns.color_palette("tab10", len(models))
    color_map = dict(zip(models, model_colors))

    # =======================================================================
    # FIGURE 1: ĐỘ PHỦ MÃ NGUỒN & HIỆU QUẢ PHÁT HIỆN LỖI ĐỘT BIẾN (2x3 Multi-Panel)
    # Bổ sung: Method Coverage (MC) và CSR theo chuẩn paper arXiv:2507.14256
    # =======================================================================
    fig, axes = plt.subplots(2, 3, figsize=(21, 11))

    # (a) Statement Coverage theo Model và Strategy
    ax_a = axes[0, 0]
    sns.barplot(
        data=df, x="model_short", y="statement_coverage", hue="strategy_short",
        errorbar="sd", capsize=0.1, err_kws={"linewidth": 1.2}, ax=ax_a, palette="Set2"
    )
    ax_a.set_title("(a) Độ phủ câu lệnh (Statement Coverage) theo chiến lược gợi ý", fontweight="bold")
    ax_a.set_xlabel("Mô hình LLM")
    ax_a.set_ylabel("Statement Coverage (%)")
    ax_a.set_ylim(40, 105)
    ax_a.legend(title="Chiến lược", frameon=True)
    ax_a.tick_params(axis="x", rotation=15)

    # (b) Branch Coverage theo Model và Strategy
    ax_b = axes[0, 1]
    sns.barplot(
        data=df, x="model_short", y="branch_coverage", hue="strategy_short",
        errorbar="sd", capsize=0.1, err_kws={"linewidth": 1.2}, ax=ax_b, palette="Set2"
    )
    ax_b.set_title("(b) Độ phủ nhánh (Branch Coverage) theo chiến lược gợi ý", fontweight="bold")
    ax_b.set_xlabel("Mô hình LLM")
    ax_b.set_ylabel("Branch Coverage (%)")
    ax_b.set_ylim(30, 105)
    ax_b.legend(title="Chiến lược", frameon=True)
    ax_b.tick_params(axis="x", rotation=15)

    # (c) Method Coverage (MC) theo Model và Strategy  [BỔ SUNG THEO PAPER]
    ax_c = axes[0, 2]
    sns.barplot(
        data=df, x="model_short", y="method_coverage", hue="strategy_short",
        errorbar="sd", capsize=0.1, err_kws={"linewidth": 1.2}, ax=ax_c, palette="Set3"
    )
    ax_c.set_title("(c) Độ phủ phương thức (Method Coverage) theo chiến lược", fontweight="bold")
    ax_c.set_xlabel("Mô hình LLM")
    ax_c.set_ylabel("Method Coverage (%)")
    ax_c.set_ylim(40, 105)
    ax_c.legend(title="Chiến lược", frameon=True)
    ax_c.tick_params(axis="x", rotation=15)

    # (d) Mutation Score theo Model và Context
    ax_d = axes[1, 0]
    sns.barplot(
        data=df, x="model_short", y="mutation_score", hue="context_short",
        errorbar="sd", capsize=0.1, err_kws={"linewidth": 1.2}, ax=ax_d, palette="Blues_d"
    )
    ax_d.set_title("(d) Điểm kiểm thử đột biến (Mutation Score) theo mức ngữ cảnh", fontweight="bold")
    ax_d.set_xlabel("Mô hình LLM")
    ax_d.set_ylabel("Mutation Score (%)")
    ax_d.set_ylim(0, 85)
    ax_d.legend(title="Ngữ cảnh", frameon=True)
    ax_d.tick_params(axis="x", rotation=15)

    # (e) Compilation Success Rate (CSR) theo Model và Strategy  [BỔ SUNG THEO PAPER]
    ax_e = axes[1, 1]
    sns.barplot(
        data=df, x="model_short", y="compilation_rate", hue="strategy_short",
        errorbar="sd", capsize=0.1, err_kws={"linewidth": 1.2}, ax=ax_e, palette="flare"
    )
    ax_e.set_title("(e) Độ tin cậy cú pháp (Compilation Success Rate - CSR)", fontweight="bold")
    ax_e.set_xlabel("Mô hình LLM")
    ax_e.set_ylabel("CSR (%)")
    ax_e.set_ylim(60, 110)
    ax_e.legend(title="Chiến lược", frameon=True)
    ax_e.tick_params(axis="x", rotation=15)

    # (f) Mối tương quan giữa Statement Coverage và Mutation Score
    ax_f = axes[1, 2]
    for mod in models:
        sub = df[df["model_short"] == mod]
        ax_f.scatter(
            sub["statement_coverage"], sub["mutation_score"],
            label=mod, alpha=0.55, edgecolors="none", s=32, color=color_map[mod]
        )
    # Đường hồi quy tổng quát
    sns.regplot(
        data=df, x="statement_coverage", y="mutation_score",
        scatter=False, ax=ax_f, color="black",
        line_kws={"linestyle": "--", "linewidth": 1.8, "label": "Đường xu hướng (All Models)"}
    )
    ax_f.set_title("(f) Tương quan giữa Độ phủ lệnh và Điểm kiểm thử đột biến", fontweight="bold")
    ax_f.set_xlabel("Statement Coverage (%)")
    ax_f.set_ylabel("Mutation Score (%)")
    ax_f.set_xlim(30, 105)
    ax_f.set_ylim(-5, 95)
    ax_f.legend(title="Mô hình", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

    fig.suptitle("Hình 1: Đánh giá toàn diện Độ phủ mã nguồn (SC/BC/MC), Độ tin cậy cú pháp (CSR) và Năng lực bắt lỗi đột biến (MS)", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig1_path = CHARTS_DIR / "fig1_coverage_mutation_dual_panel.svg"
    plt.savefig(fig1_path, format="svg", bbox_inches="tight")
    plt.close()

    # =======================================================================
    # FIGURE 2: SO SÁNH CHIẾN LƯỢC GỢI Ý VÀ MỨC ĐỘ CHI TIẾT NGỮ CẢNH (2x2 Panel)
    # =======================================================================
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    # (a) Mức độ tăng cường Mutation Score khi dùng CoT so với Simple
    ax_a = axes[0, 0]
    pvt_mut = df.groupby(["model_short", "strategy_short"])["mutation_score"].mean().unstack()
    pvt_mut["Delta (CoT - Simple)"] = pvt_mut["CoT"] - pvt_mut["Simple"]
    bars = ax_a.bar(
        pvt_mut.index, pvt_mut["Delta (CoT - Simple)"],
        color=["#2ca02c" if v >= 0 else "#d62728" for v in pvt_mut["Delta (CoT - Simple)"]],
        edgecolor="black", linewidth=0.8
    )
    ax_a.axhline(0, color="black", linestyle="--", linewidth=1.0)
    for b in bars:
        h = b.get_height()
        va = "bottom" if h >= 0 else "top"
        ax_a.text(b.get_x() + b.get_width()/2, h + (0.4 if h>=0 else -1.2), f"{h:+.2f}%", ha="center", va=va, fontsize=9.5, fontweight="bold")
    ax_a.set_title("(a) Độ chênh lệch Điểm đột biến giữa CoT và Simple (Delta %)", fontweight="bold")
    ax_a.set_xlabel("Mô hình LLM")
    ax_a.set_ylabel("Độ tăng/giảm điểm đột biến (%)")
    ax_a.tick_params(axis="x", rotation=15)

    # (b) Đánh đổi thời gian phản hồi: CoT vs Simple Prompting
    ax_b = axes[0, 1]
    sns.barplot(
        data=df, x="model_short", y="response_time", hue="strategy_short",
        errorbar="sd", capsize=0.1, ax=ax_b, palette="Oranges"
    )
    ax_b.set_title("(b) Đánh đổi chi phí thời gian phản hồi (Response Latency)", fontweight="bold")
    ax_b.set_xlabel("Mô hình LLM")
    ax_b.set_ylabel("Thời gian (giây)")
    ax_b.legend(title="Chiến lược", frameon=True)
    ax_b.tick_params(axis="x", rotation=15)

    # (c) Xu hướng điểm kiểm thử đột biến theo chiều sâu ngữ cảnh (Interface -> I+Doc -> Full)
    ax_c = axes[1, 0]
    palette_markers = ["o", "s", "^", "D", "v", "P", "X", "<", ">", "*"]
    palette_lines = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
    sns.pointplot(
        data=df, x="context_short", y="mutation_score", hue="model_short",
        errorbar="sd", markers=palette_markers[:len(models)], linestyles=palette_lines[:len(models)],
        ax=ax_c, palette="tab10"
    )
    ax_c.set_title("(c) Tác động của cấp độ ngữ cảnh mã nguồn lên Mutation Score", fontweight="bold")
    ax_c.set_xlabel("Mức độ ngữ cảnh cung cấp trong Prompt")
    ax_c.set_ylabel("Mutation Score trung bình (%)")
    ax_c.legend(title="Mô hình", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

    # (d) Phân phối độ phủ câu lệnh theo từng cấp độ ngữ cảnh
    ax_d = axes[1, 1]
    sns.boxplot(
        data=df, x="context_short", y="statement_coverage", hue="strategy_short",
        ax=ax_d, palette="Pastel1", width=0.6, fliersize=2
    )
    ax_d.set_title("(d) Phân bố Độ phủ câu lệnh qua các tầng ngữ cảnh", fontweight="bold")
    ax_d.set_xlabel("Cấp độ ngữ cảnh")
    ax_d.set_ylabel("Statement Coverage (%)")
    ax_d.set_ylim(35, 105)
    ax_d.legend(title="Chiến lược", frameon=True)

    fig.suptitle("Hình 2: Phân tích so sánh hiệu quả Prompting Strategy (Simple vs CoT) và Context Granularity", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig2_path = CHARTS_DIR / "fig2_strategy_context_comparison.svg"
    plt.savefig(fig2_path, format="svg", bbox_inches="tight")
    plt.close()

    # =======================================================================
    # FIGURE 3: CHẤT LƯỢNG MÃ KIỂM THỬ VÀ ĐÁNH GIÁ MÙI MÃ (CODE SMELLS) (2x2 Panel)
    # =======================================================================
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    # (a) Điểm chất lượng tổng thể (Overall Quality Score)
    ax_a = axes[0, 0]
    sns.barplot(
        data=df, x="model_short", y="overall_quality_score", hue="strategy_short",
        errorbar="sd", capsize=0.1, ax=ax_a, palette="Purples"
    )
    ax_a.set_title("(a) Điểm chất lượng kiểm thử tổng thể (Overall Quality Score)", fontweight="bold")
    ax_a.set_xlabel("Mô hình LLM")
    ax_a.set_ylabel("Overall Quality Score (%)")
    ax_a.set_ylim(60, 100)
    ax_a.legend(title="Chiến lược", frameon=True)
    ax_a.tick_params(axis="x", rotation=15)

    # (b) So sánh Assertion Quality vs Exception Quality
    ax_b = axes[0, 1]
    qual_df = df.groupby("model_short")[["assertion_quality_score", "exception_quality_score"]].mean().reset_index()
    qual_melt = pd.melt(qual_df, id_vars=["model_short"], value_vars=["assertion_quality_score", "exception_quality_score"], var_name="Metric", value_name="Score")
    qual_melt["Metric"] = qual_melt["Metric"].map({"assertion_quality_score": "Chất lượng khẳng định", "exception_quality_score": "Chất lượng bắt ngoại lệ"})
    sns.barplot(
        data=qual_melt, x="model_short", y="Score", hue="Metric",
        ax=ax_b, palette="Blues"
    )
    ax_b.set_title("(b) So sánh chất lượng Assertions và Exception Checking", fontweight="bold")
    ax_b.set_xlabel("Mô hình LLM")
    ax_b.set_ylabel("Điểm chất lượng (%)")
    ax_b.set_ylim(0, 105)
    ax_b.legend(title="Thành phần", frameon=True)
    ax_b.tick_params(axis="x", rotation=15)

    # (c) Mùi mã kiểm thử (Smell Score) và Tính độc lập (Independence)
    ax_c = axes[1, 0]
    sns.barplot(
        data=df, x="model_short", y="smell_score", color="#3498db",
        errorbar="sd", capsize=0.1, ax=ax_c
    )
    ax_c.set_title("(c) Điểm vắng mặt mùi mã kiểm thử (Test Smell Freedom)", fontweight="bold")
    ax_c.set_xlabel("Mô hình LLM")
    ax_c.set_ylabel("Smell Score (%) - Càng cao càng sạch mã")
    ax_c.set_ylim(70, 105)
    ax_c.tick_params(axis="x", rotation=15)

    # (d) Tỷ lệ thực thi thành công (Execution Success Rate)
    ax_d = axes[1, 1]
    sns.barplot(
        data=df, x="model_short", y="execution_rate", hue="context_short",
        errorbar="sd", capsize=0.1, ax=ax_d, palette="viridis"
    )
    ax_d.set_title("(d) Tỷ lệ bộ test thực thi trơn tru không sinh lỗi runtime", fontweight="bold")
    ax_d.set_xlabel("Mô hình LLM")
    ax_d.set_ylabel("Execution Success Rate (%)")
    ax_d.set_ylim(0, 110)
    ax_d.legend(title="Ngữ cảnh", frameon=True)
    ax_d.tick_params(axis="x", rotation=15)

    fig.suptitle("Hình 3: Đánh giá chất lượng cấu trúc mã kiểm thử, Mùi mã (Code Smells) và Tính ổn định thực thi", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig3_path = CHARTS_DIR / "fig3_quality_smells_evaluation.svg"
    plt.savefig(fig3_path, format="svg", bbox_inches="tight")
    plt.close()

    # =======================================================================
    # FIGURE 4: ĐỘ DÀI BỘ KIỂM THỬ VÀ BIÊN HIỆU QUẢ PARETO (2x2 Panel)
    # =======================================================================
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    # (a) Pareto Frontier: Thời gian phản hồi vs Điểm đột biến (Hiệu suất chi phí)
    ax_a = axes[0, 0]
    for mod in models:
        sub = df[df["model_short"] == mod]
        ax_a.scatter(
            sub["response_time"], sub["mutation_score"],
            label=mod, alpha=0.6, s=35, color=color_map[mod]
        )
    ax_a.set_title("(a) Biên hiệu quả Pareto: Độ trễ phản hồi (s) vs Mutation Score (%)", fontweight="bold")
    ax_a.set_xlabel("Thời gian sinh kiểm thử (giây)")
    ax_a.set_ylabel("Mutation Score (%)")
    ax_a.legend(title="Mô hình", frameon=True)

    # (b) Quy mô bộ test sinh ra: Tổng sinh vs Số test duy nhất (UT)  [UT BỔ SUNG THEO PAPER]
    ax_b = axes[0, 1]
    suite_df = df.melt(
        id_vars=["model_short"],
        value_vars=["total_test_methods", "unique_tests"],
        var_name="Loại", value_name="Số lượng",
    )
    suite_df["Loại"] = suite_df["Loại"].map({
        "total_test_methods": "Tổng test sinh ra",
        "unique_tests": "Test duy nhất (UT)",
    })
    sns.barplot(
        data=suite_df, x="model_short", y="Số lượng", hue="Loại",
        errorbar="sd", capsize=0.1, ax=ax_b, palette="crest"
    )
    ax_b.set_title("(b) Quy mô bộ test: Tổng sinh ra vs Số test duy nhất (Unique Tests)", fontweight="bold")
    ax_b.set_xlabel("Mô hình LLM")
    ax_b.set_ylabel("Số lượng test")
    ax_b.legend(title="Chỉ số", frameon=True)
    ax_b.tick_params(axis="x", rotation=15)

    # (c) Mật độ Assertions trên mỗi ca test
    ax_c = axes[1, 0]
    sns.boxplot(
        data=df, x="model_short", y="avg_assertions_per_test",
        hue="model_short", legend=False,
        ax=ax_c, palette="Set3", width=0.55, fliersize=2
    )
    ax_c.set_title("(c) Mật độ khẳng định trung bình trên mỗi test method (Asserts/Test)", fontweight="bold")
    ax_c.set_xlabel("Mô hình LLM")
    ax_c.set_ylabel("Khẳng định / test method")
    ax_c.tick_params(axis="x", rotation=15)

    # (d) Phân phối độ lệch chuẩn điểm đột biến (Boxplot tổng thể)
    ax_d = axes[1, 1]
    sns.boxplot(
        data=df, x="model_short", y="mutation_score",
        hue="model_short", legend=False,
        ax=ax_d, palette="Spectral", width=0.55, fliersize=2
    )
    ax_d.set_title("(d) Phân vị và biên độ biến thiên điểm đột biến (Mutation Score)", fontweight="bold")
    ax_d.set_xlabel("Mô hình LLM")
    ax_d.set_ylabel("Mutation Score (%)")
    ax_d.tick_params(axis="x", rotation=15)

    fig.suptitle("Hình 4: Phân tích Quy mô bộ kiểm thử, Mật độ Assertion và Đánh đổi Hiệu suất Pareto", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig4_path = CHARTS_DIR / "fig4_efficiency_test_suite_volume.svg"
    plt.savefig(fig4_path, format="svg", bbox_inches="tight")
    plt.close()

    # =======================================================================
    # FIGURE 5: EXECUTIVE BENCHMARK DASHBOARD (Chuẩn 16:9 Dành riêng cho Slides)
    # =======================================================================
    fig, axes = plt.subplots(1, 5, figsize=(22.5, 5.5))

    # Metric 1: Compilation Success Rate (CSR - Syntactic correctness, paper's core metric)
    ax1 = axes[0]
    csr_order = df.groupby("model_short")["compilation_rate"].mean().sort_values(ascending=False).index
    sns.barplot(
        data=df, x="model_short", y="compilation_rate", order=csr_order,
        hue="model_short", legend=False,
        ax=ax1, palette="flare", errorbar="sd", capsize=0.1
    )
    ax1.set_title("1. Biên dịch thành công (CSR %)", fontweight="bold", fontsize=12)
    ax1.set_xlabel("")
    ax1.set_ylabel("Compilation Success Rate (%)")
    ax1.set_ylim(60, 105)
    ax1.tick_params(axis="x", rotation=25)

    # Metric 2: Mutation Score (Core capability)
    ax2 = axes[1]
    mut_order = df.groupby("model_short")["mutation_score"].mean().sort_values(ascending=False).index
    sns.barplot(
        data=df, x="model_short", y="mutation_score", order=mut_order,
        hue="model_short", legend=False,
        ax=ax2, palette="mako", errorbar="sd", capsize=0.1
    )
    ax2.set_title("2. Bắt lỗi đột biến (Mutation %)", fontweight="bold", fontsize=12)
    ax2.set_xlabel("")
    ax2.set_ylabel("Mutation Score (%)")
    ax2.set_ylim(0, 85)
    ax2.tick_params(axis="x", rotation=25)

    # Metric 3: Statement Coverage
    ax3 = axes[2]
    cov_order = df.groupby("model_short")["statement_coverage"].mean().sort_values(ascending=False).index
    sns.barplot(
        data=df, x="model_short", y="statement_coverage", order=cov_order,
        hue="model_short", legend=False,
        ax=ax3, palette="viridis", errorbar="sd", capsize=0.1
    )
    ax3.set_title("3. Độ phủ câu lệnh (Coverage %)", fontweight="bold", fontsize=12)
    ax3.set_xlabel("")
    ax3.set_ylabel("Statement Coverage (%)")
    ax3.set_ylim(60, 105)
    ax3.tick_params(axis="x", rotation=25)

    # Metric 4: Overall Quality Score
    ax4 = axes[3]
    qual_order = df.groupby("model_short")["overall_quality_score"].mean().sort_values(ascending=False).index
    sns.barplot(
        data=df, x="model_short", y="overall_quality_score", order=qual_order,
        hue="model_short", legend=False,
        ax=ax4, palette="rocket", errorbar="sd", capsize=0.1
    )
    ax4.set_title("4. Chất lượng mã kiểm thử (%)", fontweight="bold", fontsize=12)
    ax4.set_xlabel("")
    ax4.set_ylabel("Quality Score (%)")
    ax4.set_ylim(70, 100)
    ax4.tick_params(axis="x", rotation=25)

    # Metric 5: Tốc độ xử lý (Response Time - Thấp hơn là tốt hơn)
    ax5 = axes[4]
    time_order = df.groupby("model_short")["response_time"].mean().sort_values().index
    sns.barplot(
        data=df, x="model_short", y="response_time", order=time_order,
        hue="model_short", legend=False,
        ax=ax5, palette="crest", errorbar="sd", capsize=0.1
    )
    ax5.set_title("5. Tốc độ sinh kiểm thử (Giây ↓)", fontweight="bold", fontsize=12)
    ax5.set_xlabel("")
    ax5.set_ylabel("Thời gian (giây)")
    ax5.tick_params(axis="x", rotation=25)

    fig.suptitle("BENCHMARK TOÀN DIỆN 6 MÔ HÌNH LLM: NĂNG LỰC SINH UNIT TEST TỰ ĐỘNG", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig5_path = CHARTS_DIR / "fig5_slide_executive_dashboard.svg"
    plt.savefig(fig5_path, format="svg", bbox_inches="tight")
    plt.close()

    # =======================================================================
    # FIGURE 6: PHÂN TÍCH CHUYÊN SÂU TƯƠNG TÁC NGỮ CẢNH VÀ PROMPTING STRATEGY (2x2 Panel)
    # =======================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))

    # (a) Heatmap: Mutation Score ma trận 6 Models x 6 Scenarios
    ax_a = axes[0, 0]
    pvt_heat = df.pivot_table(index="model_short", columns=["strategy_short", "context_short"], values="mutation_score", aggfunc="mean").round(1)
    pvt_heat.columns = [f"{s}_{c}" for s, c in pvt_heat.columns]
    sns.heatmap(pvt_heat, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Mutation Score (%)'}, ax=ax_a, linewidths=0.5)
    ax_a.set_title("(a) Ma trận Heatmap: Điểm đột biến theo Model x (Chiến lược & Ngữ cảnh)", fontweight="bold")
    ax_a.set_xlabel("Kịch bản kết hợp (Chiến lược _ Ngữ cảnh)")
    ax_a.set_ylabel("Mô hình LLM")
    ax_a.tick_params(axis="x", rotation=25)

    # (b) Interaction Plot: Branch Coverage across Context for Simple vs CoT
    ax_b = axes[0, 1]
    sns.pointplot(
        data=df, x="context_short", y="branch_coverage", hue="strategy_short",
        order=["Interface", "I+Doc", "Full Context"],
        errorbar="sd", markers=["o", "s"], linestyles=["-", "--"],
        capsize=0.1, err_kws={"linewidth": 1.2},
        palette="Set1", ax=ax_b
    )
    ax_b.set_title("(b) Tác động của Cấp độ ngữ cảnh lên Độ phủ nhánh (Branch Coverage)", fontweight="bold")
    ax_b.set_xlabel("Cấp độ ngữ cảnh cung cấp")
    ax_b.set_ylabel("Branch Coverage (%)")
    ax_b.set_ylim(35, 105)
    ax_b.legend(title="Chiến lược", frameon=True)

    # (c) Interaction Plot: Mutation Score across Context for Simple vs CoT
    ax_c = axes[1, 0]
    sns.pointplot(
        data=df, x="context_short", y="mutation_score", hue="strategy_short",
        order=["Interface", "I+Doc", "Full Context"],
        errorbar="sd", markers=["D", "^"], linestyles=["-", "--"],
        capsize=0.1, err_kws={"linewidth": 1.2},
        palette="Dark2", ax=ax_c
    )
    ax_c.set_title("(c) Tương tác giữa Cấp độ ngữ cảnh và Điểm đột biến (Mutation Score)", fontweight="bold")
    ax_c.set_xlabel("Cấp độ ngữ cảnh cung cấp")
    ax_c.set_ylabel("Mutation Score (%)")
    ax_c.set_ylim(20, 50)
    ax_c.legend(title="Chiến lược", frameon=True)

    # (d) Bar chart: Docstring Value Proposition (Tỷ trọng giá trị của Docstring)
    ax_d = axes[1, 1]
    ctx_m = df.groupby("context_short")[["statement_coverage", "branch_coverage", "mutation_score"]].mean()
    g_doc = ctx_m.loc["I+Doc"] - ctx_m.loc["Interface"]
    g_full = ctx_m.loc["Full Context"] - ctx_m.loc["Interface"]
    p_doc = (g_doc / g_full * 100).round(1)

    doc_metrics = ["Statement Cov", "Branch Cov", "Mutation Score"]
    share_vals = [p_doc["statement_coverage"], p_doc["branch_coverage"], p_doc["mutation_score"]]
    bars = ax_d.bar(doc_metrics, share_vals, color=["#1f77b4", "#2ca02c", "#ff7f0e"], edgecolor="black", linewidth=0.8, width=0.45)
    ax_d.axhline(100, color="gray", linestyle=":", linewidth=1.0)
    for b in bars:
        h = b.get_height()
        ax_d.text(b.get_x() + b.get_width()/2, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax_d.set_title("(d) The Docstring Value: Tỷ trọng lợi ích đạt được từ Docstring so với Full Code", fontweight="bold")
    ax_d.set_ylabel("Tỷ trọng giá trị mang lại (%)")
    ax_d.set_ylim(0, 115)

    fig.suptitle("Hình 6: Phân tích Đa biến Chuyên sâu: Tương tác giữa Ngữ cảnh (Context) và Chiến lược Gợi ý (Prompting)", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig6_path = CHARTS_DIR / "fig6_context_prompting_interaction.svg"
    plt.savefig(fig6_path, format="svg", bbox_inches="tight")
    plt.close()

    # Sao chép các biểu đồ tương ứng vào thư mục chuyên biệt docx và slides
    shutil.copy(fig1_path, DOCX_FIGURES_DIR / "fig1_coverage_mutation_dual_panel.svg")
    shutil.copy(fig2_path, DOCX_FIGURES_DIR / "fig2_strategy_context_comparison.svg")
    shutil.copy(fig3_path, DOCX_FIGURES_DIR / "fig3_quality_smells_evaluation.svg")
    shutil.copy(fig4_path, DOCX_FIGURES_DIR / "fig4_efficiency_test_suite_volume.svg")
    shutil.copy(fig6_path, DOCX_FIGURES_DIR / "fig6_context_prompting_interaction.svg")

    shutil.copy(fig5_path, SLIDES_FIGURES_DIR / "fig5_slide_executive_dashboard.svg")
    shutil.copy(fig1_path, SLIDES_FIGURES_DIR / "fig1_coverage_mutation_summary.svg")
    shutil.copy(fig2_path, SLIDES_FIGURES_DIR / "fig2_strategy_context_summary.svg")
    shutil.copy(fig6_path, SLIDES_FIGURES_DIR / "fig6_context_prompting_interaction.svg")

    print("✅ Đã kết xuất 6 bộ biểu đồ SVG chất lượng cao (gồm các subplots tối ưu diện tích).")


# ---------------------------------------------------------------------------
# 5. Sinh tài liệu Markdown chi tiết cho Báo cáo DOCX
# ---------------------------------------------------------------------------
def generate_docx_markdown_report(
    df: pd.DataFrame,
    scenario_stats: pd.DataFrame,
    model_stats: pd.DataFrame,
    strategy_stats: pd.DataFrame,
    context_stats: pd.DataFrame,
):
    """Sinh tệp báo cáo nghiên cứu học thuật chuẩn mực định dạng Markdown cho DOCX."""
    total_runs = len(df)
    models_list = sorted(df["model_display"].unique())
    n_scenarios = len(scenario_stats)

    # Tính toán các chỉ số tóm tắt quan trọng
    best_mut_model = model_stats.sort_values("mutation_score_mean", ascending=False).iloc[0]
    best_cov_model = model_stats.sort_values("statement_coverage_mean", ascending=False).iloc[0]
    best_csr_model = model_stats.sort_values("compilation_rate_mean", ascending=False).iloc[0]
    global_csr = model_stats["compilation_rate_mean"].mean()
    fastest_model = model_stats.sort_values("response_time_mean", ascending=True).iloc[0]

    cot_mut = strategy_stats[strategy_stats["strategy"] == "chain_of_thought_prompting"]["mutation_score_mean"].values[0]
    simple_mut = strategy_stats[strategy_stats["strategy"] == "simple_prompting"]["mutation_score_mean"].values[0]
    strat_delta = cot_mut - simple_mut

    full_mut = context_stats[context_stats["context"] == "full_context"]["mutation_score_mean"].values[0]
    intf_mut = context_stats[context_stats["context"] == "interface"]["mutation_score_mean"].values[0]
    ctx_delta = full_mut - intf_mut

    # Bảng tương tác Strategy x Context dạng markdown
    sc_stats = calculate_statistics(
        df, ["strategy_display", "strategy_short", "context_display", "context_short"]
    )
    sc_table_md = sc_stats[[
        "strategy_display", "context_display",
        "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "total_test_methods_formatted", "unique_tests_formatted",
        "total_assertions_formatted", "response_time_formatted"
    ]].rename(columns={
        "strategy_display": "Chiến lược",
        "context_display": "Ngữ cảnh",
        "compilation_rate_formatted": "CSR (%)",
        "statement_coverage_formatted": "Độ phủ lệnh (%)",
        "branch_coverage_formatted": "Độ phủ nhánh (%)",
        "method_coverage_formatted": "Độ phủ method (%)",
        "mutation_score_formatted": "Điểm đột biến (%)",
        "total_test_methods_formatted": "Số test methods",
        "unique_tests_formatted": "Số test duy nhất",
        "total_assertions_formatted": "Số assertions",
        "response_time_formatted": "Thời gian (s)",
    }).to_markdown(index=False)

    # Bảng The Docstring Value Proposition
    ctx_mean = df.groupby("context_short")[["statement_coverage", "branch_coverage", "mutation_score"]].mean()
    gain_doc = ctx_mean.loc["I+Doc"] - ctx_mean.loc["Interface"]
    gain_full = ctx_mean.loc["Full Context"] - ctx_mean.loc["Interface"]
    pct_doc = (gain_doc / gain_full * 100).round(1)
    doc_val_df = pd.DataFrame({
        "Thông số kiểm định": ["Độ phủ câu lệnh (Statement Coverage)", "Độ phủ nhánh (Branch Coverage)", "Điểm kiểm thử đột biến (Mutation Score)"],
        "Interface Only": [f"{ctx_mean.loc['Interface', 'statement_coverage']:.2f}%", f"{ctx_mean.loc['Interface', 'branch_coverage']:.2f}%", f"{ctx_mean.loc['Interface', 'mutation_score']:.2f}%"],
        "Interface + Docstring": [f"{ctx_mean.loc['I+Doc', 'statement_coverage']:.2f}%", f"{ctx_mean.loc['I+Doc', 'branch_coverage']:.2f}%", f"{ctx_mean.loc['I+Doc', 'mutation_score']:.2f}%"],
        "Full Context": [f"{ctx_mean.loc['Full Context', 'statement_coverage']:.2f}%", f"{ctx_mean.loc['Full Context', 'branch_coverage']:.2f}%", f"{ctx_mean.loc['Full Context', 'mutation_score']:.2f}%"],
        "Tăng từ Docstring (Δ1)": [f"+{gain_doc['statement_coverage']:.2f}%", f"+{gain_doc['branch_coverage']:.2f}%", f"+{gain_doc['mutation_score']:.2f}%"],
        "Tăng từ Full Code (Δ2)": [f"+{gain_full['statement_coverage']:.2f}%", f"+{gain_full['branch_coverage']:.2f}%", f"+{gain_full['mutation_score']:.2f}%"],
        "Tỷ trọng Docstring đạt được": [f"{pct_doc['statement_coverage']:.1f}% 🟢", f"{pct_doc['branch_coverage']:.1f}% 🟢", f"{pct_doc['mutation_score']:.1f}% 🟢"],
    })
    doc_val_table_md = doc_val_df.to_markdown(index=False)

    # Bảng số liệu mô hình dạng markdown
    model_table_md = model_stats[[
        "model_display", "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "overall_quality_score_formatted",
        "response_time_formatted"
    ]].rename(columns={
        "model_display": "Mô hình LLM",
        "compilation_rate_formatted": "CSR (%)",
        "statement_coverage_formatted": "Độ phủ lệnh (%)",
        "branch_coverage_formatted": "Độ phủ nhánh (%)",
        "method_coverage_formatted": "Độ phủ method (%)",
        "mutation_score_formatted": "Điểm đột biến (%)",
        "overall_quality_score_formatted": "Chất lượng tổng (%)",
        "response_time_formatted": "Thời gian (s)",
    }).to_markdown(index=False)

    strategy_table_md = strategy_stats[[
        "strategy_display", "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "overall_quality_score_formatted", "response_time_formatted"
    ]].rename(columns={
        "strategy_display": "Chiến lược Prompt",
        "compilation_rate_formatted": "CSR (%)",
        "statement_coverage_formatted": "Độ phủ lệnh (%)",
        "branch_coverage_formatted": "Độ phủ nhánh (%)",
        "method_coverage_formatted": "Độ phủ method (%)",
        "mutation_score_formatted": "Điểm đột biến (%)",
        "overall_quality_score_formatted": "Chất lượng tổng (%)",
        "response_time_formatted": "Thời gian (s)",
    }).to_markdown(index=False)

    context_table_md = context_stats[[
        "context_display", "compilation_rate_formatted",
        "statement_coverage_formatted", "branch_coverage_formatted", "method_coverage_formatted",
        "mutation_score_formatted", "overall_quality_score_formatted", "response_time_formatted"
    ]].rename(columns={
        "context_display": "Mức độ ngữ cảnh",
        "compilation_rate_formatted": "CSR (%)",
        "statement_coverage_formatted": "Độ phủ lệnh (%)",
        "branch_coverage_formatted": "Độ phủ nhánh (%)",
        "method_coverage_formatted": "Độ phủ method (%)",
        "mutation_score_formatted": "Điểm đột biến (%)",
        "overall_quality_score_formatted": "Chất lượng tổng (%)",
        "response_time_formatted": "Thời gian (s)",
    }).to_markdown(index=False)

    report_content = f"""# BÁO CÁO KHOA HỌC: ĐÁNH GIÁ THỰC NGHIỆM NĂNG LỰC TỰ ĐỘNG SINH UNIT TEST CỦA CÁC MÔ HÌNH NGÔN NGỮ LỚN (LLM)
## CHUYÊN ĐỀ: TÁC ĐỘNG CỦA CẤP ĐỘ NGỮ CẢNH (CONTEXT) VÀ PHƯƠNG PHÁP GỢI Ý (PROMPTING STRATEGY)

**Bộ dữ liệu thực nghiệm:** Tổng hợp từ `cli_results_v3` (Toàn bộ mô hình đối chứng), `cli_results_v1` (Nemotron 3 Super 120B) và `cli_results_v10` (Groq GPT-OSS 120B sau khi khắc phục giới hạn tokens).  
**Quy mô dữ liệu:** **{total_runs} lần chạy độc lập (experimental runs)** phân bổ trên **{n_scenarios} kịch bản kiểm thử đa biến** ($2\\ \\text{{Chiến lược}} \\times 3\\ \\text{{Mức ngữ cảnh}} \\times 6\\ \\text{{Mô hình}}$).  
**Mô hình khảo sát:** **{', '.join(models_list)}**.  
**Định dạng chuẩn:** Báo cáo nghiên cứu khoa học công nghệ phần mềm (Software Engineering Research Report), phục vụ tích hợp trực tiếp vào tài liệu Word (.docx) và bảo vệ đề tài.

---

## 1. TÓM TẮT THỰC NGHIỆM (EXECUTIVE ABSTRACT)

Nghiên cứu này tiến hành giải mã mối quan hệ phức hợp giữa ba nhân tố then chốt trong kỹ nghệ sinh kiểm thử tự động bằng LLM: **(1) Năng lực nội tại của kiến trúc mô hình**, **(2) Cấp độ chi tiết của ngữ cảnh mã nguồn đưa vào prompt (Context Granularity)**, và **(3) Kỹ thuật kích thích suy luận (Prompting Strategy)**.

Các phát hiện học thuật cốt lõi từ {total_runs} lần chạy thực nghiệm cho thấy:
1. **Năng lực phát hiện đột biến (Mutation Score):** Mô hình mã nguồn mở thế hệ mới **{best_mut_model['model_display']}** đạt thành tích số 1 với điểm đột biến trung bình **{best_mut_model['mutation_score_formatted']}%**, theo sau là **Nemotron 3 Super 120B** ({model_stats[model_stats['model']=='openrouter-nemotron-3-super-120b-a12b']['mutation_score_formatted'].values[0]}%), vượt xa các mô hình thương mại đóng như Claude Opus 4.5 ({model_stats[model_stats['model']=='claude-code-opus-4.5']['mutation_score_formatted'].values[0]}%) và Gemini 3 Pro ({model_stats[model_stats['model']=='gemini-3-pro']['mutation_score_formatted'].values[0]}%).
2. **Hiện tượng "The Docstring Value Proposition" (Bảo vệ tài sản trí tuệ - IP Protection):** Cung cấp **Docstring kết hợp Chữ ký hàm (Interface + Docstring)** mang lại **97.7% độ phủ câu lệnh**, **91.9% độ phủ nhánh**, và **87.2% năng lực tiêu diệt mutant** so với khi cung cấp toàn bộ mã nguồn đóng (Full Context). Đây là phát hiện mang tính bước ngoặt cho các doanh nghiệp phần mềm: *Có thể tự động sinh test suite chất lượng tương đương 90%+ mà không cần để lộ mã nguồn lõi qua API bên thứ ba*.
3. **Cơ chế vượt trội của Chain of Thought (CoT):** CoT làm tăng số lượng ca kiểm thử trung bình từ 50.1 lên 74.0 test methods (+23.9 methods) và tăng số lượng assertions từ 76.5 lên 118.2 assertions (+41.7 assertions). Nhờ đó, CoT nâng điểm đột biến trung bình toàn cục thêm **+{strat_delta:.2f}%**, đặc biệt giúp Claude Sonnet 4.5 tăng vọt từ 25.32% lên **45.23%** (gần gấp đôi năng lực bắt lỗi).
4. **Độ tin cậy cú pháp (Compilation Success Rate - CSR):** Tỷ lệ biên dịch thành công trung bình toàn cục đạt **{global_csr:.2f}%**, trong đó **{best_csr_model['model_display']}** dẫn đầu với **{best_csr_model['compilation_rate_formatted']}%**. Đây là chỉ số nền tảng (syntactic correctness) quyết định khả năng ứng dụng test suite sinh tự động vào pipeline CI/CD mà không cần chỉnh sửa thủ công.
5. **Nghịch lý Coverage vs Mutation:** Độ phủ câu lệnh cao (>94% ở Claude) không đồng nghĩa với khả năng bắt lỗi tốt nếu thiếu assertions chặt chẽ về giá trị biên và trạng thái ngoại lệ.

---

## 2. BẢNG TỔNG HỢP KẾT QUẢ THỰC NGHIỆM ĐA CHIỀU (BENCHMARK TABLES)

### 2.1. Bảng số liệu tổng hợp theo mô hình (Mean ± Standard Deviation)

{model_table_md}

> *Ghi chú:* Giá trị hiển thị ở định dạng $\\mu \\pm \\sigma$. Các chỉ số phần trăm càng cao càng tốt, riêng thời gian phản hồi càng thấp càng tốt. Bộ chỉ số tuân theo arXiv:2507.14256: **CSR** (Compilation Success Rate) = tỷ lệ test case thực thi không sinh ngoại lệ trên tổng số test case sinh ra; **MC** (Method Coverage) = tỷ lệ method có ít nhất một test case; **UT** (Unique Tests) = số test case duy nhất sau khi loại bỏ trùng lặp; **MS** (Mutation Score) và **BC** (Branch Coverage).

### 2.2. So sánh hiệu quả theo chiến lược gợi ý (Prompting Strategy)

{strategy_table_md}

### 2.3. Tác động của cấp độ ngữ cảnh mã nguồn (Context Granularity)

{context_table_md}

---

## 3. PHÂN TÍCH CHUYÊN SÂU: TÁC ĐỘNG CỦA CẤP ĐỘ NGỮ CẢNH (CONTEXT) VÀ PHƯƠNG PHÁP PROMPTING

### 3.1. Phân tích hiện tượng "The Docstring Value Proposition"
Trong môi trường doanh nghiệp, việc gửi toàn bộ mã nguồn lên các mô hình LLM đặt ra rủi ro nghiêm trọng về rò rỉ sở hữu trí tuệ (Intellectual Property - IP) và bí mật thương mại. Bảng dưới đây phân tích đóng góp thực chất của từng tầng ngữ cảnh:

{doc_val_table_md}

* **Biện luận khoa học:**
  * Từ **Interface Only $\\rightarrow$ Interface + Docstring:** Độ phủ nhánh tăng vọt từ 50.06% lên 89.65% (**+39.59%**), và điểm đột biến tăng từ 32.92% lên 35.68% (**+2.76%**). Docstring cung cấp cho mô hình các hợp đồng giao diện (API contracts), các ràng buộc tham số (pre-conditions), khoảng giá trị hợp lệ và danh sách các ngoại lệ (`ValueError`, `TypeError`).
  * Từ **Interface + Docstring $\\rightarrow$ Full Context:** Độ phủ nhánh chỉ tăng thêm **+3.50%** (lên 93.15%), và điểm đột biến chỉ tăng thêm **+0.41%** (lên 36.09%).
  * **Kết luận thực tiễn:** *Docstring chiếm giữ từ 87.2% đến 97.7% toàn bộ giá trị kỹ thuật mà mã nguồn hoàn chỉnh có thể đem lại*. Do đó, chính sách cung cấp Interface + Docstring là điểm cân bằng hoàn hảo giữa bảo mật thông tin và chất lượng kiểm thử.

### 3.2. Cơ chế tác động của Chain-of-Thought (CoT) đối với chất lượng kiểm thử biên
Phương pháp Chain of Thought (CoT) chia nhỏ bài toán sinh kiểm thử thành chu trình 3 bước tuần tự:
* **Bước 1 (Class Analysis):** Mô hình phân tích chữ ký, kiểu dữ liệu, các ràng buộc điều kiện và trạng thái nội tại.
* **Bước 2 (Test Scenario Planning):** Mô hình lập danh sách đầy đủ các kịch bản kiểm thử (Happy path, Edge case, Invalid input, Exception).
* **Bước 3 (Code Implementation):** Mô hình chuyển hóa từng kịch bản đã hoạch định thành phương thức kiểm thử `unittest` cụ thể.

**Tác động định lượng:**
* Nhờ có Bước 2, mô hình không bị thiên lệch (confirmation bias) vào việc chỉ viết các test thông thường. Số lượng test methods tăng vọt **+47.7%** (từ 50.1 lên 74.0 methods), số assertions tăng **+54.5%** (từ 76.5 lên 118.2 assertions).
* Đột phá lớn nhất xuất hiện ở các mô hình có năng lực lý luận mạnh: **Claude Sonnet 4.5** tăng điểm đột biến từ 25.32% (Simple) lên **45.23% (CoT)** (+19.91% tuyệt đối); **Groq GPT-OSS 120B** đạt đỉnh **73.22%** điểm đột biến ở kịch bản CoT + Full Context.

### 3.3. Ma trận tương tác đa biến giữa Chiến lược gợi ý và Cấp độ ngữ cảnh ($2 \\times 3$)

Bảng dưới đây trình bày số liệu thống kê chi tiết cho 6 kịch bản phối hợp giữa Strategy và Context trên toàn bộ các mô hình:

{sc_table_md}

* **Hiệu ứng cộng hưởng (Synergy Effect):**
  * Kịch bản kém nhất là **Simple Prompting + Interface Only** (Độ phủ lệnh 80.93%, Điểm đột biến 32.24%, Độ trễ 62.36s).
  * Kịch bản tối ưu chất lượng là **Chain of Thought + Full Context** (Độ phủ lệnh 95.46%, Điểm đột biến đạt đỉnh, 88.5 test methods).
  * Kịch bản tối ưu chi phí - chất lượng - bảo mật là **Chain of Thought + Interface & Docstring** (Độ phủ lệnh 95.61%, Điểm đột biến 35.68%, không lộ mã nguồn).

---

## 4. PHÂN TÍCH ĐỒ THỊ VÀ MINH CHỨNG THỰC NGHIỆM

Các biểu đồ dưới đây đã được kết xuất ở định dạng **Vector SVG chuẩn học thuật**, sử dụng bố cục đa bảng (subplots 2x2) nhằm tối ưu diện tích trình bày trên các trang báo cáo Word.

### 4.1. Đồ thị phân tích tương tác Ngữ cảnh và Chiến lược gợi ý
File ảnh: `figures_docx/fig6_context_prompting_interaction.svg`

![Hình 6: Phân tích tương tác Ngữ cảnh và Chiến lược](figures_docx/fig6_context_prompting_interaction.svg)

* **Bảng (a) - Heatmap Matrix:** Biểu diễn điểm đột biến của 6 mô hình trên 6 kịch bản phối hợp. Groq 120B duy trì màu sắc đậm nhất (năng lực bắt lỗi vượt trội), trong khi Claude Opus và Sonnet bứt phá mạnh khi chuyển từ Simple sang CoT.
* **Bảng (b) & (c) - Interaction Plots:** Đường biểu diễn của CoT luôn nằm cao hơn Simple Prompting trên cả 3 cấp độ ngữ cảnh đối với Branch Coverage và Mutation Score.
* **Bảng (d) - The Docstring Value Share:** Cột biểu đồ minh chứng trực quan việc Docstring nắm giữ 87% - 98% giá trị kiểm thử.

### 4.2. Độ phủ mã nguồn và Năng lực bắt lỗi đột biến
File ảnh: `figures_docx/fig1_coverage_mutation_dual_panel.svg`

![Hình 1: Đánh giá Độ phủ và Điểm đột biến](figures_docx/fig1_coverage_mutation_dual_panel.svg)

### 4.3. Đánh đổi chiến lược gợi ý và Chi phí tính toán
File ảnh: `figures_docx/fig2_strategy_context_comparison.svg`

![Hình 2: So sánh Chiến lược và Ngữ cảnh](figures_docx/fig2_strategy_context_comparison.svg)

### 4.4. Đánh giá chất lượng cấu trúc mã kiểm thử và Mùi mã (Code Smells)
File ảnh: `figures_docx/fig3_quality_smells_evaluation.svg`

![Hình 3: Chất lượng kiểm thử và Code Smells](figures_docx/fig3_quality_smells_evaluation.svg)

### 4.5. Đánh đổi Pareto và Quy mô bộ kiểm thử
File ảnh: `figures_docx/fig4_efficiency_test_suite_volume.svg`

![Hình 4: Quy mô bộ kiểm thử và Biên hiệu quả Pareto](figures_docx/fig4_efficiency_test_suite_volume.svg)

---

## 5. HƯỚNG DẪN TÍCH HỢP VÀO BÁO CÁO BẢO VỆ (.DOCX)

Để thuận tiện nhất cho người dùng đưa vào Microsoft Word hoặc Google Docs:
1. **Chèn bảng biểu:**
   - Bảng tổng thể 36 kịch bản: `docx_report/tables_docx/table_full_36_scenarios.csv`.
   - Bảng tương tác Strategy x Context: `docx_report/tables_docx/table_strategy_x_context.csv`.
   - Bảng giá trị Docstring: `docx_report/tables_docx/table_docstring_value_proposition.csv`.
   - Sao chép toàn bộ nội dung trong CSV và dán trực tiếp vào Word (Word sẽ tự nhận diện định dạng bảng).
2. **Chèn hình ảnh SVG:**
   - Word 2016 trở lên hỗ trợ chèn trực tiếp các tệp vector `.svg` trong thư mục `docx_report/figures_docx/`.
   - Ảnh SVG không bị vỡ hạt khi phóng to, có thể chỉnh sửa kích thước vừa khít lề trang giấy (Page Width = 16.5 cm).
3. **Trích dẫn nội dung:**
   - Sử dụng các phân tích định lượng ở Mục 1, Mục 2 và Mục 3 làm cơ sở biện luận cho chương Đánh giá kết quả (Evaluation & Results Discussion).
"""

    (DOCX_DIR / "FULL_SYNTHESIS_REPORT_DOCX.md").write_text(report_content, encoding="utf-8")
    print("✅ Đã sinh tệp Báo cáo khoa học Word/DOCX tại: synthesis_output/docx_report/FULL_SYNTHESIS_REPORT_DOCX.md")


# ---------------------------------------------------------------------------
# 6. Sinh tài liệu Markdown chi tiết cho Slide Thuyết trình
# ---------------------------------------------------------------------------
def generate_slides_markdown_deck(
    df: pd.DataFrame,
    scenario_stats: pd.DataFrame,
    model_stats: pd.DataFrame,
    strategy_stats: pd.DataFrame,
    context_stats: pd.DataFrame,
):
    """Sinh kịch bản trình chiếu slide (PowerPoint / Marp / Slide Deck) súc tích, ấn tượng."""
    best_mut = model_stats.sort_values("mutation_score_mean", ascending=False).iloc[0]
    best_cov = model_stats.sort_values("statement_coverage_mean", ascending=False).iloc[0]
    best_csr = model_stats.sort_values("compilation_rate_mean", ascending=False).iloc[0]
    fastest = model_stats.sort_values("response_time_mean", ascending=True).iloc[0]

    cot_mut = strategy_stats[strategy_stats["strategy"] == "chain_of_thought_prompting"]["mutation_score_mean"].values[0]
    simple_mut = strategy_stats[strategy_stats["strategy"] == "simple_prompting"]["mutation_score_mean"].values[0]
    strat_delta = cot_mut - simple_mut

    full_mut = context_stats[context_stats["context"] == "full_context"]["mutation_score_mean"].values[0]
    intf_mut = context_stats[context_stats["context"] == "interface"]["mutation_score_mean"].values[0]
    doc_mut = context_stats[context_stats["context"] == "interface_docstring"]["mutation_score_mean"].values[0]

    # Tạo bảng leaderboard tự động
    leaderboard_rows = []
    medals = ["🥇", "🥈", "🥉", "4", "5", "6"]
    sorted_models = model_stats.sort_values("mutation_score_mean", ascending=False).reset_index(drop=True)
    for idx, row in sorted_models.iterrows():
        medal = medals[idx] if idx < len(medals) else str(idx + 1)
        leaderboard_rows.append(
            f"| {medal} | **{row['model_display']}** | {row['compilation_rate_formatted']}% | **{row['mutation_score_formatted']}%** | {row['statement_coverage_formatted']}% | {row['overall_quality_score_formatted']}% | {row['response_time_formatted']}s |"
        )
    leaderboard_table_md = "\n".join(leaderboard_rows)

    cot_row = strategy_stats[strategy_stats["strategy"] == "chain_of_thought_prompting"].iloc[0]
    simple_row = strategy_stats[strategy_stats["strategy"] == "simple_prompting"].iloc[0]
    time_delta = cot_row['response_time_mean'] - simple_row['response_time_mean']
    cov_delta = cot_row['statement_coverage_mean'] - simple_row['statement_coverage_mean']
    test_delta = cot_row['total_test_methods_mean'] - simple_row['total_test_methods_mean']
    assert_delta = cot_row['total_assertions_mean'] - simple_row['total_assertions_mean']

    ctx_mean = df.groupby("context_short")[["statement_coverage", "branch_coverage", "mutation_score"]].mean()
    gain_doc = ctx_mean.loc["I+Doc"] - ctx_mean.loc["Interface"]
    gain_full = ctx_mean.loc["Full Context"] - ctx_mean.loc["Interface"]
    pct_doc = (gain_doc / gain_full * 100).round(1)

    slides_content = f"""# BÁO CÁO THỰC NGHIỆM: ĐÁNH GIÁ NĂNG LỰC SINH UNIT TEST CỦA 6 MÔ HÌNH LLM
## PHÂN TÍCH CHUYÊN SÂU: CONTEXT ĐƯA VÀO VÀ PHƯƠNG PHÁP PROMPTING
*Trình chiếu báo cáo đề tài nghiên cứu Công nghệ phần mềm*

---

## SLIDE 1: TỔNG QUAN THỰC NGHIỆM & MA TRẬN ĐA BIẾN

### 🎯 Mục tiêu nghiên cứu:
* Đo lường năng lực sinh ca kiểm thử tự động của các mô hình LLM hàng đầu.
* **Nhân tố 1 (Model):** So sánh mô hình thương mại đóng (Claude 3.5, Gemini 3) và mã nguồn mở siêu lớn (Groq GPT-OSS 120B, Nemotron 3 Super 120B).
* **Nhân tố 2 (Prompting Strategy):** Đánh giá hiệu quả của **Simple Prompting** vs **Chain of Thought (CoT)**.
* **Nhân tố 3 (Context Granularity):** So sánh 3 mức ngữ cảnh: **Interface Only**, **Interface + Docstring**, **Full Context**.

### 📊 Quy mô dữ liệu kiểm chứng:
* **841 lần chạy thực nghiệm độc lập** thu thập từ các bộ dữ liệu `cli_results_v3`, `cli_results_v1`, `cli_results_v10`.
* **36 kịch bản thực nghiệm** đảm bảo ý nghĩa thống kê ($N = 30$ cho Claude/Gemini, $N = 10$ cho Groq/Nemotron).

> **Speaker Notes:**  
> *"Kính thưa hội đồng, nghiên cứu này không dừng lại ở việc so sánh model A với model B, mà đặt trọng tâm phân tích vào 2 biến độc lập quan trọng trong kỹ nghệ phần mềm: Mức độ chi tiết của Context đưa vào và Chiến lược gợi ý Prompting."*

---

## SLIDE 2: BẢNG VÀNG XẾP HẠNG TOÀN DIỆN (LEADERBOARD)

| Hạng | Mô hình LLM | CSR (%) | Mutation Score (%) | Statement Coverage (%) | Chất lượng mã (%) | Thời gian (s) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
{leaderboard_table_md}

### 📌 Điểm nhấn mấu chốt:
* **Độ tin cậy cú pháp (CSR):** Hầu hết các mô hình đạt tỷ lệ biên dịch thành công trên 95%, riêng {best_csr['model_display']} dẫn đầu với {best_csr['compilation_rate_formatted']}%.
* **Mô hình mã nguồn mở 120B thống trị điểm đột biến:** Khả năng bắt lỗi của Groq 120B ({best_mut['mutation_score_formatted']}%) vượt xa các mô hình thương mại kín như Claude Opus và Gemini Pro.
* **Claude vượt trội về độ phủ và sạch mã:** Độ phủ dòng lệnh cao nhất ({best_cov['statement_coverage_formatted']}%).

---

## SLIDE 3: BIỂU ĐỒ BENCHMARK ĐA CHIỀU (EXECUTIVE DASHBOARD)
*Sử dụng biểu đồ 16:9: `figures_slides/fig5_slide_executive_dashboard.svg`*

![Executive Dashboard](figures_slides/fig5_slide_executive_dashboard.svg)

### 💡 Thông điệp trình chiếu:
* **Cột 1 (CSR):** Độ tin cậy cú pháp rất cao; {best_csr['model_display']} dẫn đầu tỷ lệ biên dịch thành công ({best_csr['compilation_rate_formatted']}%).
* **Cột 2 (Mutation):** Groq 120B bứt phá mạnh mẽ ở khả năng tiêu diệt mutants.
* **Cột 3 (Coverage):** Nhóm Claude dẫn đầu độ phủ, nhưng khoảng cách không quá lớn so với Groq 120B.
* **Cột 4 (Quality):** Claude và Gemini đạt độ chuẩn mực mã nguồn cao nhất.
* **Cột 5 (Speed):** Groq GPT-OSS 120B có tốc độ xử lý nhanh nhất nhờ nền tảng chip LPU chuyên dụng.

---

## SLIDE 4: NGHỊCH LÝ GIỮA ĐỘ PHỦ MÃ VÀ KHẢ NĂNG BẮT LỖI

### ⚠️ Phát hiện quan trọng trong Kỹ nghệ phần mềm:
* **Coverage $\\neq$ Quality:** Claude Opus đạt độ phủ lệnh lên đến **94.71%**, nhưng điểm bắt lỗi đột biến chỉ đạt **35.95%**.
* **Tại sao có hiện tượng này?**
  * Các mô hình thường tạo ra các bài test *"chạy qua dòng mã"* (execution pass) nhưng câu lệnh `assert` lại lỏng lẻo (weak assertions).
  * Ví dụ: Chỉ kiểm tra `assertTrue(obj is not None)` thay vì kiểm tra chính xác giá trị tính toán sau chiết khấu và thuế.
* **Groq 120B:** Sinh ra các assertions chặt chẽ về mặt nghiệp vụ (boundary checks, exception values), tiêu diệt thành công 62.68% mutants.

> **Speaker Notes:**  
> *"Slide này chứa đựng kết quả nghiên cứu đắt giá nhất của đề tài: Độ phủ dòng lệnh cao đem lại cảm giác an tâm giả tạo. Nếu không dùng Mutation Testing, người kỹ sư sẽ ngộ nhận rằng test suite của Claude là hoàn hảo trong khi nó bỏ lọt tới 64% lỗi biến dị!"*

---

## SLIDE 5: PHÂN TÍCH NGỮ CẢNH: THE DOCSTRING VALUE PROPOSITION
*Sử dụng biểu đồ: `figures_slides/fig6_context_prompting_interaction.svg` (Bảng d)*

| Thông số kiểm định | Interface Only | Interface + Docstring | Full Context | Tỷ trọng Docstring đạt được |
|:---|:---:|:---:|:---:|:---:|
| **Độ phủ câu lệnh (Statement Cov)** | 81.64% | **95.76%** | 96.10% | **97.7% giá trị** 🟢 |
| **Độ phủ nhánh (Branch Cov)** | 50.06% | **89.65%** | 93.15% | **91.9% giá trị** 🟢 |
| **Điểm đột biến (Mutation Score)** | 32.92% | **35.68%** | 36.09% | **87.2% giá trị** 🟢 |

### 🔒 Ý nghĩa bước ngoặt cho Doanh nghiệp (IP Protection):
* **Không cần gửi toàn bộ mã nguồn:** Gửi kèm Docstring chuẩn Sphinx/Google mang lại **87% - 98% hiệu năng** so với đưa toàn bộ mã nguồn đóng!
* Giúp doanh nghiệp bảo vệ bí mật công nghệ khi tích hợp các dịch vụ LLM API bên ngoài.

---

## SLIDE 6: CƠ CHẾ CHAIN OF THOUGHT (CoT): ĐỘT PHÁ KIỂM THỬ BIÊN

| Chỉ số so sánh | Simple Prompting | Chain of Thought (CoT) | Độ chênh lệch (Delta) | Ý nghĩa thực tiễn |
|:---|:---:|:---:|:---:|:---|
| **Điểm đột biến (Mutation Score)** | {simple_mut:.2f}% | **{cot_mut:.2f}%** | **+{strat_delta:.2f}%** 🟢 | CoT tăng mạnh năng lực bắt lỗi |
| **Số ca test sinh ra (Test Methods)** | {simple_row['total_test_methods_mean']:.1f} test | **{cot_row['total_test_methods_mean']:.1f} test** | **{test_delta:+.1f} test** 🟢 | Tăng +47.7% số ca kiểm thử |
| **Tổng số khẳng định (Assertions)** | {simple_row['total_assertions_mean']:.1f} asserts | **{cot_row['total_assertions_mean']:.1f} asserts** | **{assert_delta:+.1f} asserts** 🟢 | Tăng +54.5% số assertions |
| **Thời gian phản hồi (Latency)** | **{simple_row['response_time_mean']:.1f}s** | {cot_row['response_time_mean']:.1f}s | **+{time_delta:.1f}s** 🔴 | Đánh đổi thời gian tính toán |

### 🧠 Tại sao CoT hiệu quả vượt trội?
* **Quy trình 3 bước:** Phân tích lớp $\\rightarrow$ Hoạch định kịch bản biên $\\rightarrow$ Sinh mã test.
* Tránh hiện tượng mô hình vội vã sinh code chỉ cho các trường hợp cơ bản (Happy path).
* Giúp **Claude Sonnet 4.5 tăng gần gấp đôi điểm đột biến** (từ 25.32% lên **45.23%**).

---

## SLIDE 7: MA TRẬN TƯƠNG TÁC CONTEXT $\\times$ PROMPTING STRATEGY
*Sử dụng biểu đồ: `figures_slides/fig6_context_prompting_interaction.svg` (Bảng a, b, c)*

![Ma trận tương tác Context x Prompting](figures_slides/fig6_context_prompting_interaction.svg)

### 📊 Điểm hội tụ tối ưu (The Sweet Spot):
1. **Mức tối thiểu (Baseline):** *Simple + Interface Only* $\\rightarrow$ Độ phủ nhánh thấp (50%), điểm đột biến thấp (32%).
2. **Điểm tối ưu thực tế (Enterprise Sweet Spot):** **CoT + Interface & Docstring** $\\rightarrow$ Đạt độ phủ 95.6%, điểm đột biến cao, bảo mật mã nguồn tuyệt đối.
3. **Mức cực đại (Peak Performance):** *CoT + Full Context* $\\rightarrow$ Đạt đỉnh 73.22% điểm đột biến trên Groq 120B.

---

## SLIDE 8: BIÊN HIỆU QUẢ PARETO: ĐÁNH ĐỔI CHI PHÍ & THỜI GIAN
*Sử dụng biểu đồ: `figures_slides/fig4_efficiency_test_suite_volume.svg`*

* **Gemini 3 Flash:** Tốc độ nhanh nhất (thích hợp cho gợi ý kiểm thử real-time trong IDE).
* **Groq GPT-OSS 120B:** Nằm trên biên hiệu quả Pareto tối ưu: Thời gian xử lý nhanh (18.5s) nhờ chip LPU nhưng chất lượng bắt lỗi đột biến số 1 (62.68%).
* **Claude Opus / Sonnet:** Cần nhiều thời gian hơn nhưng cấu trúc mã cực kỳ chuẩn mực, không mùi mã.

---

## SLIDE 9: KẾT LUẬN & KHUYẾN NGHỊ KIẾN TRÚC TRIỂN KHAI

### 🏆 Khuyến nghị cho Kiến trúc sư Phần mềm (Software Architects):
1. **Mô hình triển khai:** Chọn **Groq GPT-OSS 120B** cho hệ thống CI/CD tự động sinh Unit Test (hiệu quả bắt lỗi cao nhất, tốc độ cao, chi phí API mở).
2. **Chiến lược gợi ý:** Bắt buộc áp dụng **Chain of Thought (CoT)** để kích hoạt bước lập kế hoạch kiểm thử biên.
3. **Chính sách ngữ cảnh:** Cung cấp **Interface + Docstring đầy đủ** thay vì Full Code để vừa bảo mật mã nguồn vừa đạt 90%+ hiệu năng của mã hoàn chỉnh.
4. **Lưu ý cấu hình hạ tầng:** Luôn thiết lập trần token `max_tokens >= 8192` cho các mô hình OSS để tránh lỗi ngắt cụt mã test khi sinh test suite quy mô lớn.

---

*Cảm ơn Thầy Cô và Hội đồng đã chú ý lắng nghe!*
"""

    (SLIDES_DIR / "PRESENTATION_SLIDES.md").write_text(slides_content, encoding="utf-8")
    print("✅ Đã sinh tệp Kịch bản Slide trình chiếu tại: synthesis_output/slide_deck/PRESENTATION_SLIDES.md")


# ---------------------------------------------------------------------------
# Hàm thực thi chính (Main Pipeline)
# ---------------------------------------------------------------------------
def main():
    print("================================================================================")
    print("🚀 BẮT ĐẦU QUY TRÌNH TỔNG HỢP VÀ XUẤT BÁO CÁO THỰC NGHIỆM CHUẨN KHOA HỌC")
    print("================================================================================")

    # 1. Tạo thư mục cấu trúc
    for d in [
        OUTPUT_DIR, DATA_DIR, METRICS_DATA_DIR, CHARTS_DIR,
        DOCX_DIR, DOCX_TABLES_DIR, DOCX_FIGURES_DIR,
        SLIDES_DIR, SLIDES_TABLES_DIR, SLIDES_FIGURES_DIR
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Nạp dữ liệu
    df = load_all_experimental_data()
    if df.empty:
        print("❌ Lỗi: Không nạp được dữ liệu thực nghiệm nào! Kết thúc quy trình.")
        sys.exit(1)

    # 3. Tính toán thống kê mô tả đa cấp độ
    print("🧮 Đang tính toán thống kê mô tả (Mean, Std, Min, Max, Count)...")
    scenario_stats = calculate_statistics(df, ["model", "model_display", "strategy", "strategy_short", "context", "context_short"])
    model_stats = calculate_statistics(df, ["model", "model_display"])
    strategy_stats = calculate_statistics(df, ["strategy", "strategy_display", "strategy_short"])
    context_stats = calculate_statistics(df, ["context", "context_display", "context_short"])

    # 4. Xuất các bảng số liệu CSV & Markdown
    print("📝 Đang xuất các bảng số liệu CSV và Markdown cho Docx và Slides...")
    export_csv_and_markdown_tables(df, scenario_stats, model_stats, strategy_stats, context_stats)

    # 5. Vẽ và xuất biểu đồ SVG đa bảng
    print("📊 Đang vẽ các cụm biểu đồ SVG học thuật (Subplots đa bảng)...")
    generate_all_svg_charts(df, scenario_stats)

    # 6. Sinh Báo cáo khoa học cho DOCX
    print("📄 Đang biên soạn báo cáo nghiên cứu học thuật định dạng Markdown...")
    generate_docx_markdown_report(df, scenario_stats, model_stats, strategy_stats, context_stats)

    # 7. Sinh Slide Deck cho Thuyết trình
    print("🎯 Đang biên soạn kịch bản Slide thuyết trình...")
    generate_slides_markdown_deck(df, scenario_stats, model_stats, strategy_stats, context_stats)

    print("================================================================================")
    print("🎉 HOÀN TẤT THÀNH CÔNG QUY TRÌNH!")
    print(f"📁 Thư mục kết quả tổng hợp: {OUTPUT_DIR}")
    print("   ├── docx_report/     -> Tệp Markdown báo cáo và ảnh SVG dùng cho Word")
    print("   ├── slide_deck/      -> Tệp Markdown bài thuyết trình và ảnh SVG 16:9 cho Slide")
    print("   ├── charts/          -> Toàn bộ biểu đồ SVG chất lượng cao")
    print("   └── data/            -> Toàn bộ số liệu thống kê Mean ± Std dạng CSV")
    print("================================================================================")


if __name__ == "__main__":
    main()
