"""
Ground truth dataset for FAIRDEAL validation metrics system.

Defines 30 scoring test cases mapped to the synthetic contract corpus,
plus known ordering pairs for systematic validation of the psychological
scoring engine.
"""

from __future__ import annotations

_SERVICE_BENEFITS_4 = ["provident_fund", "gratuity", "health_insurance", "insurance_life"]
_SERVICE_BENEFITS_5 = _SERVICE_BENEFITS_4 + ["paid_leave"]
_PRODUCT_BENEFITS_6 = ["provident_fund", "gratuity", "health_insurance", "insurance_life", "paid_leave", "performance_bonus"]
_PRODUCT_BENEFITS_7_EQ = ["provident_fund", "gratuity", "health_insurance", "insurance_life", "paid_leave", "stock_options", "performance_bonus"]
_PRODUCT_BENEFITS_8_EQ = _PRODUCT_BENEFITS_7_EQ + ["gym_wellness"]
_STARTUP_BENEFITS_6 = ["provident_fund", "gratuity", "health_insurance", "paid_leave", "stock_options", "performance_bonus"]
_STARTUP_BENEFITS_7 = _STARTUP_BENEFITS_6 + ["gym_wellness"]
_STARTUP_BENEFITS_8 = _STARTUP_BENEFITS_7 + ["internet_broadband"]
_CONSULT_BENEFITS_5 = ["provident_fund", "gratuity", "health_insurance", "insurance_life", "paid_leave"]


def _case(
    id: str, name: str, category: str, company: str, ctc: int,
    sal_pct: float, notice_pct: float, notice_days: int,
    benefits: list, benefits_count: int,
    nc: bool = False, nc_months: int = 0,
    bond: bool = False, bond_amt: int = 0, bond_months: int = 0,
    role_level: str = "entry", equity: bool = False,
    probation: int = 6, hours: int = 45,
    garden: bool = False, termination_wc: bool = False,
    unlimited_ded: bool = False, legal_violations: bool = False,
    expected_range: list = None, expected_grades: list = None,
):
    return {
        "id": id,
        "name": name,
        "category": category,
        "company": company,
        "ctc_inr": ctc,
        "inputs": {
            "salary_percentile": sal_pct,
            "notice_percentile": notice_pct,
            "benefits_count": benefits_count,
            "benefits_list": benefits,
            "non_compete": nc,
            "non_compete_months": nc_months,
            "role_level": role_level,
            "industry": "tech",
            "salary_in_inr": ctc,
            "notice_period_days": notice_days,
            "training_bond": bond,
            "training_bond_amount": bond_amt,
            "training_bond_months": bond_months,
            "pf_status": "present",
            "gratuity_status": "present",
            "garden_leave": garden,
            "probation_months": probation,
            "termination_without_cause": termination_wc,
            "unlimited_deductions": unlimited_ded,
            "working_hours_per_week": hours,
            "has_equity": equity,
            "has_legal_violations": legal_violations,
        },
        "expected_score_range": expected_range or [30, 100],
        "expected_grades": expected_grades or [],
    }


# ═══════════════════════════════════════════════════════════════════
# 30 SCORING TEST CASES — mapped to the synthetic contract corpus
# ═══════════════════════════════════════════════════════════════════

SCORING_TEST_CASES = [
    # ── SERVICE COMPANIES (11) ──
    _case("TC01", "TCS – Entry Service", "service", "TCS", 362000,
          sal_pct=5, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          expected_range=[40, 65], expected_grades=["AVERAGE", "FAIR"]),

    _case("TC02", "Infosys – Service + Bond", "service", "Infosys", 425000,
          sal_pct=8, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=150000, bond_months=12,
          expected_range=[38, 60], expected_grades=["AVERAGE", "BELOW AVERAGE"]),

    _case("TC03", "Wipro – Service + Small Bond", "service", "Wipro", 350000,
          sal_pct=4, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=75000, bond_months=12,
          expected_range=[38, 60], expected_grades=["AVERAGE", "BELOW AVERAGE"]),

    _case("TC04", "HCL – Service + Bond + Short Notice", "service", "HCL", 400000,
          sal_pct=6, notice_pct=50, notice_days=60,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=100000, bond_months=12,
          expected_range=[40, 63], expected_grades=["AVERAGE", "FAIR"]),

    _case("TC05", "Cognizant – Service Clean", "service", "Cognizant", 450000,
          sal_pct=9, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_5, benefits_count=5,
          expected_range=[42, 65], expected_grades=["AVERAGE", "FAIR"]),

    _case("TC06", "Tech Mahindra – Service + Small Bond", "service", "Tech Mahindra", 380000,
          sal_pct=5, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=50000, bond_months=12,
          expected_range=[38, 62], expected_grades=["AVERAGE", "BELOW AVERAGE"]),

    _case("TC07", "Capgemini – Service Clean", "service", "Capgemini", 420000,
          sal_pct=7, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_5, benefits_count=5,
          expected_range=[42, 65], expected_grades=["AVERAGE", "FAIR"]),

    _case("TC08", "Accenture – Service Better Pay", "service", "Accenture", 500000,
          sal_pct=12, notice_pct=50, notice_days=60,
          benefits=_SERVICE_BENEFITS_5, benefits_count=5,
          expected_range=[52, 75], expected_grades=["AVERAGE", "FAIR", "GOOD"]),

    _case("TC09", "LTIMindtree – Service + Bond", "service", "LTIMindtree", 390000,
          sal_pct=6, notice_pct=75, notice_days=90,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=125000, bond_months=12,
          expected_range=[38, 60], expected_grades=["AVERAGE", "BELOW AVERAGE"]),

    _case("TC10", "Mphasis – Service Clean Short Notice", "service", "Mphasis", 410000,
          sal_pct=7, notice_pct=50, notice_days=60,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          expected_range=[45, 65], expected_grades=["AVERAGE", "FAIR"]),

    _case("TC11", "Hexaware – Service + Small Bond Short Notice", "service", "Hexaware", 370000,
          sal_pct=5, notice_pct=50, notice_days=60,
          benefits=_SERVICE_BENEFITS_4, benefits_count=4,
          bond=True, bond_amt=50000, bond_months=12,
          expected_range=[40, 63], expected_grades=["AVERAGE", "FAIR"]),

    # ── PRODUCT COMPANIES (11) ──
    _case("TC12", "Google – Top-Tier Product", "product", "Google", 2800000,
          sal_pct=92, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_7_EQ, benefits_count=7,
          role_level="mid", equity=True, probation=6,
          expected_range=[80, 96], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC13", "Microsoft – Top-Tier Product", "product", "Microsoft", 2400000,
          sal_pct=85, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_7_EQ, benefits_count=7,
          role_level="mid", equity=True, probation=6,
          expected_range=[78, 94], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC14", "Amazon – Product + NC", "product", "Amazon", 2200000,
          sal_pct=80, notice_pct=20, notice_days=30,
          benefits=_PRODUCT_BENEFITS_6, benefits_count=6,
          nc=True, nc_months=12, role_level="mid",
          expected_range=[68, 94], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC15", "Flipkart – Product Good", "product", "Flipkart", 2000000,
          sal_pct=75, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_7_EQ, benefits_count=7,
          role_level="mid", equity=True, probation=3,
          expected_range=[74, 92], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC16", "Adobe – Top-Tier Product", "product", "Adobe", 2600000,
          sal_pct=88, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_7_EQ, benefits_count=7,
          role_level="mid", equity=True, probation=6,
          expected_range=[80, 95], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC17", "Oracle – Product + NC + Long Notice", "product", "Oracle", 1800000,
          sal_pct=68, notice_pct=75, notice_days=90,
          benefits=_PRODUCT_BENEFITS_6, benefits_count=6,
          nc=True, nc_months=6, role_level="mid",
          expected_range=[60, 84], expected_grades=["FAIR", "GOOD"]),

    _case("TC18", "Samsung – Product Mid", "product", "Samsung", 1600000,
          sal_pct=60, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_6, benefits_count=6,
          role_level="mid", probation=3,
          expected_range=[72, 92], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC19", "Salesforce – Premium Product", "product", "Salesforce", 3000000,
          sal_pct=95, notice_pct=20, notice_days=30,
          benefits=_PRODUCT_BENEFITS_8_EQ, benefits_count=8,
          role_level="mid", equity=True, probation=3,
          expected_range=[85, 100], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC20", "Walmart – Product Mid", "product", "Walmart", 1900000,
          sal_pct=72, notice_pct=50, notice_days=60,
          benefits=_PRODUCT_BENEFITS_6, benefits_count=6,
          role_level="mid", probation=6,
          expected_range=[72, 92], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC21", "Intuit – Product Good + Short Notice", "product", "Intuit", 2200000,
          sal_pct=80, notice_pct=20, notice_days=30,
          benefits=_PRODUCT_BENEFITS_7_EQ, benefits_count=7,
          role_level="mid", equity=True, probation=3,
          expected_range=[85, 100], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC22", "Zoho – Product Budget", "product", "Zoho", 800000,
          sal_pct=28, notice_pct=20, notice_days=30,
          benefits=_SERVICE_BENEFITS_5, benefits_count=5,
          role_level="mid", probation=6,
          expected_range=[62, 84], expected_grades=["FAIR", "GOOD"]),

    # ── STARTUPS (6) ──
    _case("TC23", "Razorpay – Startup + NC", "startup", "Razorpay", 1800000,
          sal_pct=68, notice_pct=20, notice_days=30,
          benefits=_STARTUP_BENEFITS_7, benefits_count=7,
          nc=True, nc_months=6, role_level="mid", equity=True, probation=3,
          expected_range=[72, 94], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC24", "PhonePe – Startup Clean", "startup", "PhonePe", 1600000,
          sal_pct=60, notice_pct=20, notice_days=30,
          benefits=_STARTUP_BENEFITS_7, benefits_count=7,
          role_level="mid", equity=True, probation=3,
          expected_range=[75, 96], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC25", "CRED – Premium Startup", "startup", "CRED", 2400000,
          sal_pct=85, notice_pct=20, notice_days=30,
          benefits=_STARTUP_BENEFITS_8, benefits_count=8,
          role_level="mid", equity=True, probation=3,
          expected_range=[88, 100], expected_grades=["EXCELLENT", "EXCEPTIONAL"]),

    _case("TC26", "Swiggy – Startup + NC", "startup", "Swiggy", 1400000,
          sal_pct=52, notice_pct=20, notice_days=30,
          benefits=_STARTUP_BENEFITS_6, benefits_count=6,
          nc=True, nc_months=6, role_level="mid", equity=True, probation=3,
          expected_range=[70, 92], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC27", "Zomato – Startup Clean", "startup", "Zomato", 1200000,
          sal_pct=45, notice_pct=20, notice_days=30,
          benefits=_STARTUP_BENEFITS_6, benefits_count=6,
          role_level="mid", probation=3,
          expected_range=[72, 92], expected_grades=["GOOD", "EXCELLENT"]),

    _case("TC28", "Paytm – Startup + Long NC", "startup", "Paytm", 1000000,
          sal_pct=38, notice_pct=20, notice_days=30,
          benefits=_SERVICE_BENEFITS_5, benefits_count=5,
          nc=True, nc_months=12, role_level="mid", probation=6,
          expected_range=[60, 84], expected_grades=["FAIR", "GOOD"]),

    # ── CONSULTING (2) ──
    _case("TC29", "Deloitte – Consulting + NC", "consulting", "Deloitte", 850000,
          sal_pct=30, notice_pct=75, notice_days=90,
          benefits=_CONSULT_BENEFITS_5, benefits_count=5,
          nc=True, nc_months=6, role_level="mid",
          expected_range=[55, 78], expected_grades=["FAIR", "GOOD"]),

    _case("TC30", "EY – Consulting + Short NC", "consulting", "EY", 750000,
          sal_pct=25, notice_pct=50, notice_days=60,
          benefits=_CONSULT_BENEFITS_5, benefits_count=5,
          nc=True, nc_months=3, role_level="mid",
          expected_range=[58, 80], expected_grades=["FAIR", "GOOD"]),
]


# ═══════════════════════════════════════════════════════════════════
# KNOWN ORDERINGS — pairs where contract A should score higher than B
# ═══════════════════════════════════════════════════════════════════
KNOWN_ORDERINGS = [
    ("TC19", "TC01"),   # Salesforce (₹30L, no restrictions) > TCS (₹3.6L)
    ("TC12", "TC03"),   # Google (₹28L) > Wipro (₹3.5L + bond)
    ("TC25", "TC28"),   # CRED (₹24L, no NC) > Paytm (₹10L, 12mo NC)
    ("TC08", "TC01"),   # Accenture (₹5L, 60d) > TCS (₹3.6L, 90d)
    ("TC15", "TC17"),   # Flipkart (₹20L, no NC) > Oracle (₹18L, 6mo NC, 90d)
    ("TC16", "TC11"),   # Adobe (₹26L) > Hexaware (₹3.7L + bond)
    ("TC13", "TC02"),   # Microsoft (₹24L) > Infosys (₹4.25L + bond)
    ("TC21", "TC09"),   # Intuit (₹22L) > LTIMindtree (₹3.9L + bond)
    ("TC24", "TC29"),   # PhonePe (₹16L, 30d) > Deloitte (₹8.5L, 90d, NC)
    ("TC18", "TC06"),   # Samsung (₹16L) > Tech Mahindra (₹3.8L + bond)
    ("TC19", "TC14"),   # Salesforce (no NC) > Amazon (12mo NC)
    ("TC12", "TC17"),   # Google (₹28L, no NC) > Oracle (₹18L, 6mo NC)
    ("TC25", "TC30"),   # CRED (₹24L) > EY (₹7.5L)
    ("TC13", "TC28"),   # Microsoft (₹24L) > Paytm (₹10L, 12mo NC)
    ("TC16", "TC29"),   # Adobe (₹26L) > Deloitte (₹8.5L + NC)
]


# ═══════════════════════════════════════════════════════════════════
# EXTRACTION GROUND TRUTH — expected values from the 30 DOCX files
# ═══════════════════════════════════════════════════════════════════
EXTRACTION_GROUND_TRUTH = [
    {"filename": "TCS_Aarav_Sharma_offer_letter.docx", "ctc_inr": 362000, "notice_period_days": 90, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "TCS", "category": "service"},
    {"filename": "Infosys_Priya_Patel_offer_letter.docx", "ctc_inr": 425000, "notice_period_days": 90, "bond_amount_inr": 150000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "Infosys", "category": "service"},
    {"filename": "Wipro_Rohan_Mehta_offer_letter.docx", "ctc_inr": 350000, "notice_period_days": 90, "bond_amount_inr": 75000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "Wipro", "category": "service"},
    {"filename": "HCL_Ananya_Reddy_offer_letter.docx", "ctc_inr": 400000, "notice_period_days": 60, "bond_amount_inr": 100000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "HCL", "category": "service"},
    {"filename": "Cognizant_Vikram_Singh_offer_letter.docx", "ctc_inr": 450000, "notice_period_days": 90, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 5, "company": "Cognizant", "category": "service"},
    {"filename": "Tech_Mahindra_Sneha_Gupta_offer_letter.docx", "ctc_inr": 380000, "notice_period_days": 90, "bond_amount_inr": 50000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "Tech Mahindra", "category": "service"},
    {"filename": "Capgemini_Kavya_Iyer_offer_letter.docx", "ctc_inr": 420000, "notice_period_days": 90, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 5, "company": "Capgemini", "category": "service"},
    {"filename": "Accenture_Rahul_Deshmukh_offer_letter.docx", "ctc_inr": 500000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 5, "company": "Accenture", "category": "service"},
    {"filename": "LTIMindtree_Arjun_Nair_offer_letter.docx", "ctc_inr": 390000, "notice_period_days": 90, "bond_amount_inr": 125000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "LTIMindtree", "category": "service"},
    {"filename": "Mphasis_Neha_Joshi_offer_letter.docx", "ctc_inr": 410000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "Mphasis", "category": "service"},
    {"filename": "Hexaware_Sanya_Choudhary_offer_letter.docx", "ctc_inr": 370000, "notice_period_days": 60, "bond_amount_inr": 50000, "non_compete_months": 0, "probation_months": 6, "benefits_count": 4, "company": "Hexaware", "category": "service"},
    {"filename": "Google_Aditya_Verma_offer_letter.docx", "ctc_inr": 2800000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 7, "company": "Google", "category": "product"},
    {"filename": "Microsoft_Pooja_Agarwal_offer_letter.docx", "ctc_inr": 2400000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 7, "company": "Microsoft", "category": "product"},
    {"filename": "Amazon_Karan_Malhotra_offer_letter.docx", "ctc_inr": 2200000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 12, "probation_months": 6, "benefits_count": 6, "company": "Amazon", "category": "product"},
    {"filename": "Flipkart_Ishita_Banerjee_offer_letter.docx", "ctc_inr": 2000000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 7, "company": "Flipkart", "category": "product"},
    {"filename": "Adobe_Nikhil_Rajan_offer_letter.docx", "ctc_inr": 2600000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 7, "company": "Adobe", "category": "product"},
    {"filename": "Oracle_Siddharth_Pillai_offer_letter.docx", "ctc_inr": 1800000, "notice_period_days": 90, "bond_amount_inr": 0, "non_compete_months": 6, "probation_months": 6, "benefits_count": 6, "company": "Oracle", "category": "product"},
    {"filename": "Samsung_Meera_Chauhan_offer_letter.docx", "ctc_inr": 1600000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 6, "company": "Samsung", "category": "product"},
    {"filename": "Salesforce_Riya_Saxena_offer_letter.docx", "ctc_inr": 3000000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 8, "company": "Salesforce", "category": "product"},
    {"filename": "Walmart_Devesh_Kumar_offer_letter.docx", "ctc_inr": 1900000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 6, "company": "Walmart", "category": "product"},
    {"filename": "Intuit_Shruti_Mishra_offer_letter.docx", "ctc_inr": 2200000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 7, "company": "Intuit", "category": "product"},
    {"filename": "Zoho_Raj_Kapoor_offer_letter.docx", "ctc_inr": 800000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 6, "benefits_count": 5, "company": "Zoho", "category": "product"},
    {"filename": "Razorpay_Amit_Tiwari_offer_letter.docx", "ctc_inr": 1800000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 6, "probation_months": 3, "benefits_count": 7, "company": "Razorpay", "category": "startup"},
    {"filename": "PhonePe_Gaurav_Yadav_offer_letter.docx", "ctc_inr": 1600000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 7, "company": "PhonePe", "category": "startup"},
    {"filename": "CRED_Divya_Krishnan_offer_letter.docx", "ctc_inr": 2400000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 8, "company": "CRED", "category": "startup"},
    {"filename": "Swiggy_Tanvi_Srinivasan_offer_letter.docx", "ctc_inr": 1400000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 6, "probation_months": 3, "benefits_count": 6, "company": "Swiggy", "category": "startup"},
    {"filename": "Zomato_Harsh_Vardhan_offer_letter.docx", "ctc_inr": 1200000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 0, "probation_months": 3, "benefits_count": 6, "company": "Zomato", "category": "startup"},
    {"filename": "Paytm_Aparna_Menon_offer_letter.docx", "ctc_inr": 1000000, "notice_period_days": 30, "bond_amount_inr": 0, "non_compete_months": 12, "probation_months": 6, "benefits_count": 5, "company": "Paytm", "category": "startup"},
    {"filename": "Deloitte_Varun_Bhatia_offer_letter.docx", "ctc_inr": 850000, "notice_period_days": 90, "bond_amount_inr": 0, "non_compete_months": 6, "probation_months": 6, "benefits_count": 5, "company": "Deloitte", "category": "consulting"},
    {"filename": "EY_Nandini_Hegde_offer_letter.docx", "ctc_inr": 750000, "notice_period_days": 60, "bond_amount_inr": 0, "non_compete_months": 3, "probation_months": 6, "benefits_count": 5, "company": "EY", "category": "consulting"},
]
