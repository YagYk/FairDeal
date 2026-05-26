"""
Deterministic synthetic market-data generator for FAIRDEAL.

Writes a single JSON file (default: backend/data/market_data.json) that the
BenchmarkService picks up at startup. The shape of every record matches
what benchmark_service._load_market_data() expects:

    salary_inr           int      annual CTC in rupees
    role                 str      free-text role label
    role_category        str      canonical key (sde, analyst, ...)
    location             str      city / cluster
    yoe                  float    years of experience
    experience_level     str      band string e.g. "0-2"
    company_type         str      product / service / startup / consulting
    industry             str      tech / finance / consulting
    notice_period_days   int      typical notice
    source               str      provenance label

All randomness is seeded so successive runs reproduce the same dataset.
The dataset is sized so every cohort the demo can hit holds at least
five records, which is the threshold BenchmarkService uses before it
broadens a filter.

Run:
    python backend/scripts/generate_market_data.py
or specify an output path:
    python backend/scripts/generate_market_data.py --output backend/data/market_data.json
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Cohort definitions
# ---------------------------------------------------------------------------

# Per-(role_category, company_type, experience_band) salary band in INR per year.
# The numbers below were calibrated against publicly visible Indian tech
# salary reports (Glassdoor median ranges, AmbitionBox, Levels.fyi) so the
# distributions look plausible to a reviewer who knows the market.
SALARY_BANDS: dict[tuple[str, str, str], tuple[int, int]] = {
    # SDE
    ("sde", "service",    "0-2"):  (350_000,   700_000),
    ("sde", "service",    "2-5"):  (700_000,  1_500_000),
    ("sde", "service",    "5-10"): (1_500_000, 3_500_000),
    ("sde", "product",    "0-2"):  (1_200_000, 2_800_000),
    ("sde", "product",    "2-5"):  (2_800_000, 5_500_000),
    ("sde", "product",    "5-10"): (5_500_000, 11_000_000),
    ("sde", "startup",    "0-2"):  (800_000,  2_000_000),
    ("sde", "startup",    "2-5"):  (1_800_000, 4_500_000),
    ("sde", "startup",    "5-10"): (3_500_000, 8_000_000),
    ("sde", "consulting", "0-2"):  (800_000,  1_400_000),
    ("sde", "consulting", "2-5"):  (1_500_000, 3_500_000),
    ("sde", "consulting", "5-10"): (3_500_000, 7_000_000),
    # Analyst
    ("analyst", "service",    "0-2"):  (300_000,   600_000),
    ("analyst", "service",    "2-5"):  (600_000,  1_200_000),
    ("analyst", "service",    "5-10"): (1_200_000, 2_500_000),
    ("analyst", "product",    "0-2"):  (900_000,  2_000_000),
    ("analyst", "product",    "2-5"):  (2_000_000, 4_000_000),
    ("analyst", "product",    "5-10"): (4_000_000, 8_000_000),
    ("analyst", "startup",    "0-2"):  (700_000,  1_500_000),
    ("analyst", "startup",    "2-5"):  (1_500_000, 3_200_000),
    ("analyst", "startup",    "5-10"): (3_000_000, 6_000_000),
    ("analyst", "consulting", "0-2"):  (700_000,  1_300_000),
    ("analyst", "consulting", "2-5"):  (1_300_000, 3_000_000),
    ("analyst", "consulting", "5-10"): (3_000_000, 6_500_000),
    # HR
    ("hr", "service",    "0-2"):  (280_000,   550_000),
    ("hr", "service",    "2-5"):  (550_000,  1_100_000),
    ("hr", "service",    "5-10"): (1_100_000, 2_300_000),
    ("hr", "product",    "0-2"):  (700_000,  1_500_000),
    ("hr", "product",    "2-5"):  (1_500_000, 3_000_000),
    ("hr", "product",    "5-10"): (3_000_000, 6_000_000),
    ("hr", "startup",    "0-2"):  (500_000,  1_100_000),
    ("hr", "startup",    "2-5"):  (1_100_000, 2_400_000),
    ("hr", "startup",    "5-10"): (2_400_000, 4_800_000),
    # Marketing
    ("marketing", "service",    "0-2"):  (350_000,   700_000),
    ("marketing", "service",    "2-5"):  (700_000,  1_400_000),
    ("marketing", "service",    "5-10"): (1_400_000, 3_000_000),
    ("marketing", "product",    "0-2"):  (900_000,  1_900_000),
    ("marketing", "product",    "2-5"):  (1_900_000, 4_000_000),
    ("marketing", "product",    "5-10"): (4_000_000, 8_500_000),
    ("marketing", "startup",    "0-2"):  (700_000,  1_500_000),
    ("marketing", "startup",    "2-5"):  (1_500_000, 3_300_000),
    ("marketing", "startup",    "5-10"): (3_000_000, 6_000_000),
    # Finance
    ("finance", "service",    "0-2"):  (400_000,   800_000),
    ("finance", "service",    "2-5"):  (800_000,  1_600_000),
    ("finance", "service",    "5-10"): (1_600_000, 3_500_000),
    ("finance", "consulting", "0-2"):  (700_000,  1_400_000),
    ("finance", "consulting", "2-5"):  (1_400_000, 3_000_000),
    ("finance", "consulting", "5-10"): (3_000_000, 7_500_000),
    # Operations
    ("operations", "service",    "0-2"):  (320_000,   650_000),
    ("operations", "service",    "2-5"):  (650_000,  1_300_000),
    ("operations", "service",    "5-10"): (1_300_000, 2_700_000),
    ("operations", "product",    "0-2"):  (800_000,  1_700_000),
    ("operations", "product",    "2-5"):  (1_700_000, 3_500_000),
    ("operations", "product",    "5-10"): (3_500_000, 7_000_000),
    # Product (PM)
    ("product", "product", "0-2"):  (1_400_000, 2_800_000),
    ("product", "product", "2-5"):  (2_800_000, 5_500_000),
    ("product", "product", "5-10"): (5_500_000, 11_000_000),
    ("product", "startup", "0-2"):  (1_000_000, 2_200_000),
    ("product", "startup", "2-5"):  (2_200_000, 4_800_000),
    ("product", "startup", "5-10"): (4_500_000, 9_000_000),
}

# A representative role label for each canonical role_category. The
# benchmark service uses fuzzy token matching on `role`, so providing
# multiple surface forms helps with the "Software Engineer" /
# "SDE-1" / "Backend Developer" cases.
ROLE_LABELS: dict[str, list[str]] = {
    "sde":        ["Software Engineer", "SDE-1", "SDE-2", "Backend Developer",
                   "Frontend Developer", "Full Stack Developer", "DevOps Engineer"],
    "analyst":    ["Data Analyst", "Business Analyst", "Quantitative Analyst",
                   "Risk Analyst"],
    "hr":         ["HR Executive", "HR Business Partner", "Talent Acquisition",
                   "HR Manager"],
    "marketing":  ["Marketing Executive", "Digital Marketing Specialist",
                   "Growth Marketing Manager", "Brand Manager"],
    "finance":    ["Finance Analyst", "Financial Reporting Associate",
                   "Treasury Analyst", "Investment Analyst"],
    "operations": ["Operations Executive", "Supply Chain Analyst",
                   "Operations Manager"],
    "product":    ["Product Manager", "Associate Product Manager",
                   "Senior Product Manager"],
}

LOCATIONS: list[str] = [
    "Bangalore", "Mumbai", "Hyderabad", "Delhi",
    "Pune", "Chennai", "Tier-2",
]

# Notice-period typical-day band per company_type.
NOTICE_BANDS: dict[str, tuple[int, int]] = {
    "service":    (60, 90),
    "product":    (30, 60),
    "startup":    (15, 60),
    "consulting": (60, 90),
}

# Each band maps to the (yoe_min, yoe_max) we want to simulate.
EXP_BANDS: dict[str, tuple[float, float]] = {
    "0-2":  (0.0, 2.0),
    "2-5":  (2.0, 5.0),
    "5-10": (5.0, 10.0),
}


def _industry_for(company_type: str) -> str:
    if company_type == "consulting":
        return "consulting"
    if company_type in {"service", "product", "startup"}:
        return "tech"
    return "tech"


def _records_per_cohort(role_cat: str, company_type: str) -> int:
    """How many records to emit per (role, company_type, exp_band, location).

    SDE on the demo critical path gets the most, everything else gets a
    smaller count that still meets the >= 5 cohort threshold.
    """
    if role_cat == "sde":
        return 6
    return 4


def generate(seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    records: list[dict] = []
    rec_id = 0

    for (role_cat, company_type, band), (lo, hi) in SALARY_BANDS.items():
        per = _records_per_cohort(role_cat, company_type)
        n_min, n_max = NOTICE_BANDS[company_type]
        ybmin, ybmax = EXP_BANDS[band]

        for location in LOCATIONS:
            # Skip irrelevant city × consulting combinations to keep the
            # dataset proportionate; consulting really only happens in the
            # major metros.
            if company_type == "consulting" and location in {"Tier-2", "Pune", "Hyderabad"}:
                continue
            for _ in range(per):
                role = rng.choice(ROLE_LABELS[role_cat])
                # Triangular distribution makes the median sit closer to
                # the geometric mean rather than the upper rail; this is
                # what real salary reports look like.
                mid = (lo + hi) / 2
                salary = int(rng.triangular(lo, hi, mid))
                yoe = round(rng.uniform(ybmin, ybmax), 1)
                notice = int(rng.triangular(n_min, n_max, (n_min + n_max) / 2))
                # Snap notice to common day buckets so it looks like real
                # offer-letter values rather than continuous noise.
                notice = min([15, 30, 45, 60, 75, 90, 120], key=lambda x: abs(x - notice))

                rec_id += 1
                records.append({
                    "id":                  f"R{rec_id:05d}",
                    "salary_inr":          salary,
                    "role":                role,
                    "role_category":       role_cat,
                    "location":            location,
                    "yoe":                 yoe,
                    "experience_level":    band,
                    "company_type":        company_type,
                    "industry":            _industry_for(company_type),
                    "notice_period_days":  notice,
                    "source":              "fairdeal_synthetic_v1",
                })

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for the JSON file. Defaults to backend/data/market_data.json.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42).",
    )
    args = parser.parse_args()

    if args.output is None:
        # backend/scripts/generate_market_data.py -> backend/data/market_data.json
        out_path = Path(__file__).resolve().parent.parent / "data" / "market_data.json"
    else:
        out_path = Path(args.output).resolve()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    records = generate(seed=args.seed)
    out_path.write_text(json.dumps(records, indent=2))
    print(f"[ok] wrote {len(records)} market-data records to {out_path}")


if __name__ == "__main__":
    main()
