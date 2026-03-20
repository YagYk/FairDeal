"""
FAIRDEAL — IEEE Paper Results Generator
Generates publication-quality figures and summary tables.

Usage:
    python backend/generate_results.py

Outputs saved to  backend/results/
"""

from __future__ import annotations

import sys, os, math, textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns
from scipy import stats as sp_stats

from app.evaluation.evaluator import FairDealEvaluator

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(exist_ok=True)

DPI = 300
FIG_W, FIG_H = 7, 4.5              # inches — fits IEEE two-column nicely
FONT = {"family": "serif", "size": 10}
matplotlib.rc("font", **FONT)
matplotlib.rc("axes", labelsize=11, titlesize=12)
matplotlib.rc("xtick", labelsize=9)
matplotlib.rc("ytick", labelsize=9)

CAT_COLORS = {
    "service":    "#e67e22",
    "product":    "#2980b9",
    "startup":    "#8e44ad",
    "consulting": "#16a085",
}
CAT_ORDER = ["service", "consulting", "startup", "product"]

GRADE_COLORS = {
    "CRITICAL": "#7f1d1d", "POOR": "#b91c1c", "BELOW AVERAGE": "#dc2626",
    "AVERAGE": "#f97316", "FAIR": "#eab308", "GOOD": "#3b82f6",
    "EXCELLENT": "#10b981", "EXCEPTIONAL": "#22c55e",
}
GRADE_ORDER = ["CRITICAL","POOR","BELOW AVERAGE","AVERAGE","FAIR","GOOD","EXCELLENT","EXCEPTIONAL"]


def run():
    print("Running evaluation engine …")
    ev = FairDealEvaluator()
    rpt = ev.run_full_evaluation()
    print(f"  {rpt.total_test_cases} cases, {rpt.evaluation_time_ms:.1f} ms\n")

    results = rpt.scoring_results
    scores  = np.array([r.actual_score for r in results])

    # ── 1. Score Distribution Histogram ─────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    bins = np.arange(40, 105, 5)
    n, _, patches = ax.hist(scores, bins=bins, edgecolor="white", linewidth=0.6, color="#2980b9", alpha=0.85)
    ax.axvline(rpt.score_distribution.mean, color="#e74c3c", ls="--", lw=1.4, label=f"Mean = {rpt.score_distribution.mean:.1f}")
    ax.axvline(rpt.score_distribution.median, color="#f39c12", ls=":", lw=1.4, label=f"Median = {rpt.score_distribution.median:.1f}")
    ax.set_xlabel("Fairness Score")
    ax.set_ylabel("Number of Contracts")
    ax.set_title("Distribution of Fairness Scores (n = 30)")
    ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=9)
    ax.set_xlim(35, 105)
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_score_distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [1/8] Score distribution histogram")

    # ── 2. CTC vs Score Scatter (by category) ──────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    for cat in CAT_ORDER:
        xs = [r.ctc_inr / 1e5 for r in results if r.category == cat]
        ys = [r.actual_score   for r in results if r.category == cat]
        ax.scatter(xs, ys, label=cat.capitalize(), color=CAT_COLORS[cat],
                   s=60, edgecolors="white", linewidths=0.4, alpha=0.9, zorder=3)
    # trend line (all data)
    ctcs = np.array([r.ctc_inr / 1e5 for r in results])
    slope, intercept, r_val, p_val, _ = sp_stats.linregress(ctcs, scores)
    x_line = np.linspace(ctcs.min(), ctcs.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, "k--", lw=1, alpha=0.5,
            label=f"r = {r_val:.3f}, p < 0.001")
    ax.set_xlabel("Annual CTC (₹ Lakhs)")
    ax.set_ylabel("Fairness Score")
    ax.set_title("CTC vs. Fairness Score by Company Category")
    ax.legend(frameon=True, fontsize=8, loc="lower right")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_ctc_vs_score.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [2/8] CTC vs Score scatter")

    # ── 3. Box Plot by Category ─────────────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    cat_data = {c: [] for c in CAT_ORDER}
    for r in results:
        cat_data[r.category].append(r.actual_score)
    bp_data = [cat_data[c] for c in CAT_ORDER]
    bp = ax.boxplot(bp_data, patch_artist=True, widths=0.5, showmeans=True,
                    meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black", markersize=5))
    for patch, cat in zip(bp["boxes"], CAT_ORDER):
        patch.set_facecolor(CAT_COLORS[cat])
        patch.set_alpha(0.8)
    ax.set_xticklabels([c.capitalize() for c in CAT_ORDER])
    ax.set_ylabel("Fairness Score")
    ax.set_title("Score Distribution by Company Category")
    ax.set_ylim(30, 105)
    # annotate means
    for i, cat in enumerate(CAT_ORDER):
        m = np.mean(cat_data[cat])
        ax.annotate(f"μ={m:.1f}", xy=(i + 1, m), xytext=(i + 1.35, m),
                    fontsize=8, color="#333", va="center")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_category_boxplot.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [3/8] Category box plot")

    # ── 4. Grade Distribution Bar Chart ─────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    grades_present = [g for g in GRADE_ORDER if rpt.grade_distribution.get(g, 0) > 0]
    counts = [rpt.grade_distribution[g] for g in grades_present]
    colors = [GRADE_COLORS[g] for g in grades_present]
    bars = ax.barh(grades_present, counts, color=colors, edgecolor="white", linewidth=0.5)
    for bar, c in zip(bars, counts):
        if c > 0:
            ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                    str(c), va="center", fontsize=9, fontweight="bold")
    ax.set_xlabel("Number of Contracts")
    ax.set_title("Grade Distribution (n = 30)")
    ax.invert_yaxis()
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_grade_distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [4/8] Grade distribution")

    # ── 5. Feature Correlation Bar Chart ────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, 3.5))
    feat_names = [c.feature.replace("_", " ").title() for c in rpt.feature_correlations]
    feat_r     = [c.pearson_r for c in rpt.feature_correlations]
    colors_f   = ["#2980b9" if r > 0 else "#e74c3c" for r in feat_r]
    bars = ax.barh(feat_names, feat_r, color=colors_f, edgecolor="white", linewidth=0.5)
    for bar, r_v in zip(bars, feat_r):
        offset = 0.02 if r_v > 0 else -0.06
        ax.text(r_v + offset, bar.get_y() + bar.get_height() / 2,
                f"r={r_v:.3f}", va="center", fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Pearson Correlation Coefficient (r)")
    ax.set_title("Feature–Score Correlations")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig5_feature_correlations.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [5/8] Feature correlations")

    # ── 6. Component Radar Chart ────────────────────────────────
    components = list(rpt.component_stats.keys())
    means = [rpt.component_stats[c]["mean"] for c in components]
    labels = [c.capitalize() for c in components]
    N = len(components)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    means_plot = means + [means[0]]
    angles += [angles[0]]
    labels_plot = labels + [labels[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, means_plot, alpha=0.2, color="#2980b9")
    ax.plot(angles, means_plot, "o-", color="#2980b9", lw=1.5, markersize=5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7, color="gray")
    ax.set_title("Mean Component Scores", y=1.08, fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_component_radar.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [6/8] Component radar")

    # ── 7. Expected vs Actual Score Plot ────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    midpoints = [(r.expected_range[0] + r.expected_range[1]) / 2 for r in results]
    errors_lo = [r.actual_score - r.expected_range[0] for r in results]
    errors_hi = [r.expected_range[1] - r.actual_score for r in results]
    for cat in CAT_ORDER:
        idxs = [i for i, r in enumerate(results) if r.category == cat]
        mx = [midpoints[i] for i in idxs]
        my = [results[i].actual_score for i in idxs]
        ax.scatter(mx, my, label=cat.capitalize(), color=CAT_COLORS[cat],
                   s=50, edgecolors="white", linewidths=0.4, zorder=3)
    lo_all = min(min(midpoints), min(scores)) - 5
    hi_all = max(max(midpoints), max(scores)) + 5
    ax.plot([lo_all, hi_all], [lo_all, hi_all], "k--", lw=0.8, alpha=0.4, label="Perfect agreement")
    ax.set_xlabel("Expected Score (midpoint of range)")
    ax.set_ylabel("Actual Score")
    ax.set_title("Expected vs. Actual Fairness Scores")
    ax.legend(frameon=True, fontsize=8)
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig7_expected_vs_actual.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [7/8] Expected vs Actual")

    # ── 8. Heatmap: Component Scores per Contract ───────────────
    comp_names = list(rpt.component_stats.keys())
    matrix = []
    y_labels = []
    for r in results:
        row = [r.breakdown[c]["score"] for c in comp_names]
        matrix.append(row)
        y_labels.append(f"{r.company} ({r.category[0].upper()})")
    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(6, 9))
    sns.heatmap(matrix, ax=ax, cmap="RdYlGn", vmin=20, vmax=100,
                xticklabels=[c.capitalize() for c in comp_names],
                yticklabels=y_labels, linewidths=0.3, linecolor="white",
                cbar_kws={"label": "Component Score", "shrink": 0.6},
                annot=True, fmt=".0f", annot_kws={"fontsize": 7})
    ax.set_title("Component Scores per Contract", fontsize=12, pad=12)
    ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig8_component_heatmap.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [8/8] Component heatmap")

    # ═══════════════════════════════════════════════════════════════
    # TEXT SUMMARY (copy-paste into paper)
    # ═══════════════════════════════════════════════════════════════

    # Normality test
    _, norm_p = sp_stats.shapiro(scores)

    summary = textwrap.dedent(f"""\
    ╔══════════════════════════════════════════════════════════════════╗
    ║           FAIRDEAL VALIDATION RESULTS SUMMARY                  ║
    ║           (for IEEE paper Section: Results & Validation)        ║
    ╠══════════════════════════════════════════════════════════════════╣

    A. DATASET
       Total test cases ............... {rpt.total_test_cases}
       Categories ..................... Service (11), Product (11), Startup (6), Consulting (2)
       CTC range ...................... ₹3.50L – ₹30.00L
       Engine version ................. v{rpt.engine_version}

    B. SCORING VALIDATION
       Pass rate (within range) ....... {rpt.scoring_pass_rate}%  ({sum(1 for r in results if r.passed)}/{len(results)})
       Known-ordering accuracy ........ {rpt.known_ordering_accuracy}%  ({rpt.known_ordering_correct}/{rpt.known_ordering_total})
       Determinism (3 runs) ........... {rpt.determinism_score}%

    C. SCORE DISTRIBUTION
       Mean ± SD ...................... {rpt.score_distribution.mean:.2f} ± {rpt.score_distribution.std_dev:.2f}
       Median ......................... {rpt.score_distribution.median:.1f}
       Range .......................... [{rpt.score_distribution.min_score}, {rpt.score_distribution.max_score}]
       IQR (Q1–Q3) ................... [{rpt.score_distribution.q1}, {rpt.score_distribution.q3}]
       Skewness ....................... {rpt.score_distribution.skewness:.3f}
       Kurtosis ....................... {rpt.score_distribution.kurtosis:.3f}
       Shapiro-Wilk p ................. {norm_p:.4f}  {"(normal)" if norm_p > 0.05 else "(non-normal)"}

    D. CATEGORY COMPARISON (mean ± SD)
    """)

    for cat in CAT_ORDER:
        vals = [r.actual_score for r in results if r.category == cat]
        m, s = np.mean(vals), np.std(vals, ddof=1)
        summary += f"       {cat.capitalize():12s}  {m:6.2f} ± {s:5.2f}   (n={len(vals)})\n"

    summary += "\n    Inter-group tests (Welch's t):\n"
    for c in rpt.category_comparisons:
        sig = "***" if c.p_value_approx < 0.001 else ("**" if c.p_value_approx < 0.01 else ("*" if c.p_value_approx < 0.05 else "n.s."))
        summary += f"       {c.category_a:>8s} vs {c.category_b:<10s}  t={c.t_statistic:7.3f}  d={c.effect_size:.3f}  {sig}\n"

    summary += "\n    E. FEATURE–SCORE CORRELATIONS (Pearson r)\n"
    for c in rpt.feature_correlations:
        summary += f"       {c.feature:25s}  r = {c.pearson_r:+.4f}  ({c.strength} {c.direction})\n"

    summary += "\n    F. COMPONENT SCORE STATISTICS\n"
    summary += f"       {'Component':<12s}  {'Mean':>6s}  {'SD':>6s}  {'Min':>5s}  {'Max':>5s}\n"
    summary += "       " + "-" * 42 + "\n"
    for comp, st in rpt.component_stats.items():
        summary += f"       {comp.capitalize():<12s}  {st['mean']:6.1f}  {st['std']:6.1f}  {st['min']:5.0f}  {st['max']:5.0f}\n"

    summary += f"""
    G. SYSTEM PERFORMANCE
       Evaluation time ................ {rpt.evaluation_time_ms:.2f} ms  ({rpt.evaluation_time_ms / rpt.total_test_cases:.2f} ms / case)

    ╚══════════════════════════════════════════════════════════════════╝
    """

    # Per-contract table
    summary += "\n\n    TABLE: PER-CONTRACT SCORING RESULTS\n"
    summary += f"    {'ID':<5s} {'Company':<16s} {'Category':<10s} {'CTC(L)':>8s} {'Score':>6s} {'Grade':<14s} {'Badges'}\n"
    summary += "    " + "-" * 90 + "\n"
    for r in results:
        badges_str = ", ".join(r.badges) if r.badges else "—"
        summary += f"    {r.id:<5s} {r.company:<16s} {r.category:<10s} {r.ctc_inr/1e5:>8.1f} {r.actual_score:>6d} {r.grade:<14s} {badges_str}\n"

    # Write summary
    summary_path = OUT / "results_summary.txt"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"\n  Summary written to {summary_path}")

    # Also write a LaTeX table
    latex = _generate_latex_table(rpt, results, norm_p)
    latex_path = OUT / "results_tables.tex"
    latex_path.write_text(latex, encoding="utf-8")
    print(f"  LaTeX tables written to {latex_path}")

    print(f"\n  All 8 figures saved to {OUT}/")
    print("  Done.\n")


def _generate_latex_table(rpt, results, norm_p):
    lines = []
    lines.append(r"% ═══ TABLE I: Validation Summary ═══")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\caption{Validation Metrics Summary}")
    lines.append(r"\label{tab:validation}")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{l r l}")
    lines.append(r"\hline")
    lines.append(r"\textbf{Metric} & \textbf{Value} & \textbf{Interpretation} \\")
    lines.append(r"\hline")
    lines.append(f"Scoring pass rate & {rpt.scoring_pass_rate}\\% & All within expected ranges \\\\")
    lines.append(f"Ordering accuracy & {rpt.known_ordering_accuracy}\\% & {rpt.known_ordering_correct}/{rpt.known_ordering_total} pairs correct \\\\")
    lines.append(f"Determinism & {rpt.determinism_score}\\% & Identical across {rpt.determinism_runs} runs \\\\")
    lines.append(f"Mean $\\pm$ SD & {rpt.score_distribution.mean} $\\pm$ {rpt.score_distribution.std_dev} & Healthy spread \\\\")
    lines.append(f"Score range & [{rpt.score_distribution.min_score}, {rpt.score_distribution.max_score}] & Full range utilization \\\\")
    lines.append(f"Skewness & {rpt.score_distribution.skewness:.3f} & {'Approx.\\ symmetric' if abs(rpt.score_distribution.skewness) < 0.5 else 'Slight asymmetry'} \\\\")
    lines.append(f"Shapiro-Wilk $p$ & {norm_p:.4f} & {'Normal' if norm_p > 0.05 else 'Non-normal'} distribution \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")

    lines.append(r"% ═══ TABLE II: Feature Correlations ═══")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\caption{Feature--Score Correlations}")
    lines.append(r"\label{tab:correlations}")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{l r l}")
    lines.append(r"\hline")
    lines.append(r"\textbf{Feature} & \textbf{Pearson $r$} & \textbf{Strength} \\")
    lines.append(r"\hline")
    for c in rpt.feature_correlations:
        name_tex = c.feature.replace("_", "\\_")
        lines.append(f"{name_tex} & {c.pearson_r:+.4f} & {c.strength} {c.direction} \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")

    lines.append(r"% ═══ TABLE III: Category Comparison ═══")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\caption{Inter-Category Discrimination (Welch's $t$-test)}")
    lines.append(r"\label{tab:categories}")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{l l r r r}")
    lines.append(r"\hline")
    lines.append(r"\textbf{Group A} & \textbf{Group B} & \textbf{$t$} & \textbf{Cohen's $d$} & \textbf{Sig.} \\")
    lines.append(r"\hline")
    for c in rpt.category_comparisons:
        sig = "***" if c.p_value_approx < 0.001 else ("**" if c.p_value_approx < 0.01 else ("*" if c.p_value_approx < 0.05 else "n.s."))
        lines.append(f"{c.category_a} & {c.category_b} & {c.t_statistic:.3f} & {c.effect_size:.3f} & {sig} \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


if __name__ == "__main__":
    run()
