"""Generate supplementary figures for the B.Tech project report."""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).parent / "results"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "figure.dpi": 140,
})


def fig_roadmap():
    """Project roadmap Gantt-style chart across 3 sprints."""
    fig, ax = plt.subplots(figsize=(11, 4.2))
    sprints = [
        ("Sprint I: Ingestion, OCR, Hybrid Extraction",  0, 28, "#3b82f6"),
        ("Sprint II: Benchmarking, Red Flags, Scoring",  24, 28, "#10b981"),
        ("Sprint III: RAG, Negotiation, Frontend",       48, 28, "#f59e0b"),
    ]
    milestones = [
        ("Parser + regex engine",        8),
        ("Gemini OCR tier integrated",  18),
        ("Market cohort engine",        34),
        ("5-dim scoring v3.0",          44),
        ("ChromaDB + RAG",              58),
        ("React dashboard live",        70),
        ("30-contract validation",      74),
    ]

    for i, (name, start, dur, col) in enumerate(sprints):
        ax.barh(i, dur, left=start, color=col, edgecolor="#1f2937",
                linewidth=0.8, alpha=0.85)
        ax.text(start + dur / 2, i, name, ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    for text, day in milestones:
        ax.axvline(day, color="#6b7280", ls=":", lw=0.8, alpha=0.7)
        ax.text(day, -0.8, text, rotation=35, ha="right", va="top",
                fontsize=8, color="#374151")

    ax.set_yticks(range(len(sprints)))
    ax.set_yticklabels(["Sprint I", "Sprint II", "Sprint III"])
    ax.set_xlabel("Day of project (approx.)")
    ax.set_xlim(0, 80)
    ax.set_ylim(-2.2, 3)
    ax.invert_yaxis()
    ax.set_title("Figure: Project roadmap across three agile sprints")
    ax.grid(axis="x", ls="--", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUT / "report_fig_roadmap.png", bbox_inches="tight")
    plt.close()


def _box(ax, x, y, w, h, text, color="#e0f2fe", edge="#0369a1", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                 fc=color, ec=edge, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _arrow(ax, xy1, xy2, color="#334155"):
    ax.add_patch(FancyArrowPatch(xy1, xy2, arrowstyle="->", mutation_scale=14,
                                  color=color, lw=1.2))


def fig_system_architecture():
    """High-level layered architecture diagram."""
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis("off")

    _box(ax, 0.5, 5.8, 11, 0.9, "Frontend Layer  (React 18 + TypeScript + Vite + TailwindCSS)",
         color="#dbeafe", edge="#1d4ed8", fs=11)

    _box(ax, 0.5, 4.6, 11, 0.9, "API Layer  (FastAPI + ORJSONResponse + Pydantic schemas)",
         color="#dcfce7", edge="#15803d", fs=11)

    services = [
        ("Parser\nService", "#fef3c7", "#b45309"),
        ("OCR\nService", "#fef3c7", "#b45309"),
        ("Rule\nExtraction", "#fef3c7", "#b45309"),
        ("Sniper\n(LLM)", "#fef3c7", "#b45309"),
        ("Benchmark\nService", "#fef3c7", "#b45309"),
        ("Red Flag\nEngine", "#fef3c7", "#b45309"),
        ("Scoring\nEngine v3", "#fef3c7", "#b45309"),
        ("RAG\nService", "#fef3c7", "#b45309"),
        ("Negotiation\nPlaybook", "#fef3c7", "#b45309"),
    ]
    w = 11 / 9
    for i, (t, c, e) in enumerate(services):
        _box(ax, 0.5 + i * w, 3.2, w - 0.1, 1.1, t, color=c, edge=e, fs=8)

    _box(ax, 0.5, 1.8, 11, 0.9, "LLM Layer  (Google Gemini 2.0 Flash  +  Gemini Vision API)",
         color="#fce7f3", edge="#9d174d", fs=11)

    _box(ax, 0.5,  0.4, 3.5, 1.0, "ChromaDB\n(88 contracts, 384-d vectors)",
         color="#ede9fe", edge="#5b21b6", fs=9)
    _box(ax, 4.25, 0.4, 3.5, 1.0, "Market Data\n(22 JSON cohorts)",
         color="#ede9fe", edge="#5b21b6", fs=9)
    _box(ax, 8.0,  0.4, 3.5, 1.0, "File Cache\n(SHA-256 deduped)",
         color="#ede9fe", edge="#5b21b6", fs=9)

    # connectors
    _arrow(ax, (6, 5.8), (6, 5.5))
    _arrow(ax, (6, 4.6), (6, 4.3))
    _arrow(ax, (6, 3.2), (6, 2.7))
    _arrow(ax, (6, 1.8), (6, 1.4))

    ax.text(6, 6.9, "FAIRDEAL  Layered System Architecture",
            ha="center", fontsize=13, fontweight="bold")
    plt.savefig(OUT / "report_fig_architecture.png", bbox_inches="tight")
    plt.close()


def fig_pipeline():
    """Eight-stage processing pipeline."""
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.set_xlim(0, 16); ax.set_ylim(0, 3); ax.axis("off")
    stages = [
        "1. Parse\n+ OCR",
        "2. Hybrid\nExtraction",
        "3. Market\nBenchmark",
        "4. Red Flag\nDetection",
        "5. Scoring\n(5-dim)",
        "6. Negotiation\nPlaybook",
        "7. RAG\nRetrieval",
        "8. Narration\n+ Response",
    ]
    colors = ["#fde68a", "#a7f3d0", "#bfdbfe", "#fecaca",
              "#ddd6fe", "#fed7aa", "#bae6fd", "#c7d2fe"]
    w = 1.8
    for i, (t, c) in enumerate(zip(stages, colors)):
        x = 0.2 + i * (w + 0.05)
        _box(ax, x, 1.0, w, 1.2, t, color=c, edge="#334155", fs=9)
        if i < 7:
            _arrow(ax, (x + w, 1.6), (x + w + 0.05, 1.6))

    ax.text(8, 2.6, "FAIRDEAL  End-to-End Analysis Pipeline (avg. 3–8 s per contract)",
            ha="center", fontsize=12, fontweight="bold")
    plt.savefig(OUT / "report_fig_pipeline.png", bbox_inches="tight")
    plt.close()


def fig_scoring_weights():
    """Visualize dynamic weights by role level."""
    categories = ["Salary", "Notice", "Benefits", "Clauses", "Legal"]
    entry   = [0.30, 0.20, 0.20, 0.20, 0.10]
    mid     = [0.35, 0.15, 0.20, 0.20, 0.10]
    senior  = [0.40, 0.10, 0.15, 0.25, 0.10]
    violation_active = [0.32, 0.13, 0.18, 0.17, 0.20]

    x = np.arange(len(categories))
    w = 0.2
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x - 1.5 * w, entry,  w, label="Entry level",  color="#60a5fa")
    ax.bar(x - 0.5 * w, mid,    w, label="Mid level",    color="#34d399")
    ax.bar(x + 0.5 * w, senior, w, label="Senior level", color="#fb923c")
    ax.bar(x + 1.5 * w, violation_active, w,
           label="Legal violation active", color="#f87171", hatch="//")
    ax.set_xticks(x); ax.set_xticklabels(categories)
    ax.set_ylabel("Normalized weight")
    ax.set_title("Figure: Dynamic weight reallocation across role levels")
    ax.set_ylim(0, 0.5)
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUT / "report_fig_scoring_weights.png", bbox_inches="tight")
    plt.close()


def fig_kb_composition():
    """Knowledge base composition pie + bar."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    labels = ["Service MNCs", "Product Companies", "Startups", "Consulting", "Real Pilot"]
    sizes  = [32, 28, 18, 4, 6]
    colors = ["#93c5fd", "#86efac", "#fbbf24", "#d8b4fe", "#fca5a5"]
    ax1.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%",
            startangle=90, textprops={"fontsize": 9},
            wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax1.set_title("Knowledge base composition (88 contracts)")

    roles = ["SDE", "Analyst", "HR", "Marketing", "Finance", "Ops", "Product"]
    counts = [9, 3, 2, 2, 2, 1, 3]
    ax2.barh(roles, counts, color="#6366f1")
    ax2.set_xlabel("Number of market cohorts")
    ax2.set_title("Market data coverage by role (22 cohorts)")
    ax2.invert_yaxis()
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.grid(axis="x", ls="--", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT / "report_fig_kb_composition.png", bbox_inches="tight")
    plt.close()


def fig_rag_flow():
    """Illustrate the RAG retrieval flow."""
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")

    _box(ax, 0.3, 2.2, 2.2, 1.2, "Input\ncontract\n(PDF/DOCX)", color="#fde68a", edge="#b45309")
    _box(ax, 3.0, 2.2, 2.2, 1.2, "Clause\nchunking\n(6 types)", color="#a7f3d0", edge="#047857")
    _box(ax, 5.7, 2.2, 2.2, 1.2, "MiniLM-L6\nembeddings\n(384-d)", color="#bfdbfe", edge="#1d4ed8")
    _box(ax, 8.4, 2.2, 2.2, 1.2, "ChromaDB\ncosine search\n(top-3)", color="#ddd6fe", edge="#6d28d9")
    _box(ax, 11.1, 2.2, 2.4, 1.2, "Evidence\nbundle +\nsimilarity", color="#fecaca", edge="#b91c1c")

    for x in (2.5, 5.2, 7.9, 10.6):
        _arrow(ax, (x, 2.8), (x + 0.5, 2.8))

    _box(ax, 5.7, 0.3, 2.2, 1.0, "88 indexed\ncontracts", color="#f3f4f6", edge="#6b7280", fs=9)
    _arrow(ax, (6.8, 1.3), (9.4, 2.2))

    ax.text(7, 4.3, "RAG Evidence Retrieval Flow",
            ha="center", fontsize=13, fontweight="bold")
    plt.savefig(OUT / "report_fig_rag_flow.png", bbox_inches="tight")
    plt.close()


def fig_ocr_pipeline():
    """Illustrate the 3-tier OCR cascade."""
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")

    _box(ax, 0.2, 2.0, 2.4, 1.2, "PDF page\n(raw bytes)", color="#fde68a", edge="#b45309")
    _box(ax, 3.0, 2.0, 2.4, 1.2, "Text density\n/page check", color="#fef3c7", edge="#d97706")

    _box(ax, 5.8, 3.4, 3.0, 1.0,
         "Tier 1: Gemini\nVision API", color="#dcfce7", edge="#15803d")
    _box(ax, 5.8, 2.0, 3.0, 1.0,
         "Tier 2: PyMuPDF\ntext extraction", color="#bfdbfe", edge="#1d4ed8")
    _box(ax, 5.8, 0.6, 3.0, 1.0,
         "Tier 3: pdf2image\n+ Tesseract", color="#fecaca", edge="#b91c1c")

    _box(ax, 9.4, 2.0, 2.6, 1.2, "Post-process\n(normalize, validate)",
         color="#ede9fe", edge="#6d28d9")
    _box(ax, 12.2, 2.0, 1.7, 1.2, "Clean\ntext", color="#e0f2fe", edge="#0369a1")

    _arrow(ax, (2.6, 2.6), (3.0, 2.6))
    _arrow(ax, (5.4, 2.8), (5.8, 3.9))
    _arrow(ax, (5.4, 2.6), (5.8, 2.5))
    _arrow(ax, (5.4, 2.4), (5.8, 1.1))
    _arrow(ax, (8.8, 3.9), (9.4, 2.8))
    _arrow(ax, (8.8, 2.5), (9.4, 2.6))
    _arrow(ax, (8.8, 1.1), (9.4, 2.4))
    _arrow(ax, (12.0, 2.6), (12.2, 2.6))

    ax.text(7, 4.5, "Cascaded OCR strategy with progressive fallback",
            ha="center", fontsize=13, fontweight="bold")
    plt.savefig(OUT / "report_fig_ocr_cascade.png", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig_roadmap()
    fig_system_architecture()
    fig_pipeline()
    fig_scoring_weights()
    fig_kb_composition()
    fig_rag_flow()
    fig_ocr_pipeline()
    print("All report figures generated in", OUT)
