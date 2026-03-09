#!/usr/bin/env python3
"""
Legal Aid Bot — Terminal Prototype
A citizen legal assistant that guides users through legal procedures,
generates documents, tracks cases, and sends deadline reminders.
"""

import os
import json
import datetime
import textwrap
import time
from typing import Optional

# ─── PDF Generation (using ReportLab) ───────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ─── ANSI Color Helpers ──────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"
    MAGENTA= "\033[95m"

def bot(msg: str):
    """Print a bot message with formatting."""
    print()
    lines = msg.strip().split("\n")
    print(f"  {C.CYAN}╔{'═' * 64}╗{C.RESET}")
    for line in lines:
        # Word-wrap long lines
        wrapped = textwrap.wrap(line, width=62) if line.strip() else [""]
        for wline in wrapped:
            pad = 62 - len(wline)
            print(f"  {C.CYAN}║{C.RESET} {C.WHITE}{wline}{' ' * pad}{C.RESET} {C.CYAN}║{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * 64}╝{C.RESET}")
    print()

def user_input(prompt: str = "You") -> str:
    """Get user input with styled prompt."""
    return input(f"  {C.GREEN}▶ {prompt}: {C.RESET}").strip()

def header(title: str):
    print(f"\n  {C.BOLD}{C.BLUE}{'━' * 66}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}  {title}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}{'━' * 66}{C.RESET}\n")

def step_banner(step: int, title: str):
    print(f"\n  {C.MAGENTA}┌─ Step {step}: {title} {'─' * max(0, 50 - len(title))}┐{C.RESET}")

def info(msg: str):
    print(f"  {C.DIM}{C.YELLOW}ℹ  {msg}{C.RESET}")

def success(msg: str):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")

def warning(msg: str):
    print(f"  {C.YELLOW}⚠️  {msg}{C.RESET}")

def thinking(msg: str = "Processing"):
    print(f"  {C.DIM}🔄 {msg}...", end="", flush=True)
    time.sleep(0.6)
    print(f"\r  {C.DIM}✔  {msg} complete.{C.RESET}     ")

# ─── Dispute Classification ──────────────────────────────────────────────────
DISPUTE_KEYWORDS = {
    "deposit":        ("Rental / Tenant Dispute",    "Money Recovery",          "Small Causes Court"),
    "rent":           ("Rental / Tenant Dispute",    "Eviction / Rent Recovery","Civil Court"),
    "landlord":       ("Rental / Tenant Dispute",    "Money Recovery",          "Small Causes Court"),
    "salary":         ("Employment Dispute",         "Wage Recovery",           "Labour Court"),
    "wages":          ("Employment Dispute",         "Wage Recovery",           "Labour Court"),
    "fired":          ("Employment Dispute",         "Wrongful Termination",    "Labour Court"),
    "dismissed":      ("Employment Dispute",         "Wrongful Termination",    "Labour Court"),
    "consumer":       ("Consumer Dispute",           "Consumer Complaint",      "Consumer Forum"),
    "refund":         ("Consumer Dispute",           "Refund / Defective Goods","Consumer Forum"),
    "cheque":         ("Financial Dispute",          "Cheque Bounce",           "Magistrate Court"),
    "bounce":         ("Financial Dispute",          "Cheque Bounce",           "Magistrate Court"),
    "loan":           ("Financial Dispute",          "Loan Recovery",           "Civil Court"),
    "property":       ("Property Dispute",           "Property Recovery",       "Civil Court"),
    "neighbour":      ("Property Dispute",           "Nuisance / Encroachment", "Civil Court"),
    "accident":       ("Motor Accident",             "Compensation Claim",      "Motor Accident Tribunal"),
    "harassment":     ("Criminal / Civil Harassment","Protection Order",        "Magistrate Court"),
    "domestic":       ("Domestic Violence",          "Protection Order",        "Family Court"),
    "divorce":        ("Family Dispute",             "Divorce Petition",        "Family Court"),
    "maintenance":    ("Family Dispute",             "Maintenance Claim",       "Family Court"),
    # ── New Categories ──
    "contract":       ("Contract Dispute",           "Breach of Contract",      "Civil Court"),
    "agreement":      ("Contract Dispute",           "Breach of Contract",      "Civil Court"),
    "breach":         ("Contract Dispute",           "Breach of Contract",      "Civil Court"),
    "partition":      ("Partition Suit",             "Partition of Property",   "Civil Court"),
    "joint property": ("Partition Suit",             "Partition of Property",   "Civil Court"),
    "inheritance":    ("Succession / Probate",       "Succession Certificate",  "District Court"),
    "probate":        ("Succession / Probate",       "Probate of Will",         "High Court"),
    "succession":     ("Succession / Probate",       "Succession Certificate",  "District Court"),
    "will":           ("Succession / Probate",       "Probate of Will",         "District Court"),
    "cyber":          ("Cybercrime",                 "Cybercrime Complaint",    "Cyber Crime Cell / Magistrate Court"),
    "online fraud":   ("Cybercrime",                 "Cybercrime Complaint",    "Cyber Crime Cell / Magistrate Court"),
    "hacking":        ("Cybercrime",                 "Cybercrime Complaint",    "Cyber Crime Cell / Magistrate Court"),
    "phishing":       ("Cybercrime",                 "Cybercrime Complaint",    "Cyber Crime Cell / Magistrate Court"),
    "custody":        ("Child Custody",              "Custody Petition",        "Family Court"),
    "child":          ("Child Custody",              "Custody Petition",        "Family Court"),
    "guardian":       ("Child Custody",              "Guardianship Petition",   "Family Court"),
    "insurance":      ("Insurance Dispute",          "Insurance Claim Recovery","Consumer Forum / IRDAI"),
    "claim rejected": ("Insurance Dispute",          "Insurance Claim Recovery","Consumer Forum / IRDAI"),
    "policy":         ("Insurance Dispute",          "Insurance Claim Recovery","Consumer Forum / IRDAI"),
    "defamation":     ("Defamation Suit",            "Defamation Compensation","Civil Court / Magistrate Court"),
    "slander":        ("Defamation Suit",            "Defamation Compensation","Civil Court / Magistrate Court"),
    "libel":          ("Defamation Suit",            "Defamation Compensation","Civil Court / Magistrate Court"),
    "pil":            ("Public Interest Litigation", "PIL Filing",              "High Court / Supreme Court"),
    "public interest":("Public Interest Litigation", "PIL Filing",              "High Court / Supreme Court"),
    "government":     ("Government Service Dispute", "Service Matter Petition", "Central Administrative Tribunal"),
    "pension":        ("Government Service Dispute", "Pension Recovery",        "Central Administrative Tribunal"),
    "transfer":       ("Government Service Dispute", "Service Matter Petition", "Central Administrative Tribunal"),
    "promotion":      ("Government Service Dispute", "Service Matter Petition", "Central Administrative Tribunal"),
    "tax":            ("Tax Dispute",                "Tax Appeal",              "Income Tax Appellate Tribunal"),
    "income tax":     ("Tax Dispute",                "Tax Appeal",              "Income Tax Appellate Tribunal"),
    "gst":            ("Tax Dispute",                "GST Appeal",              "GST Appellate Authority"),
    "assessment":     ("Tax Dispute",                "Tax Appeal",              "Income Tax Appellate Tribunal"),
}

WORKFLOWS = {
    "Rental / Tenant Dispute": {
        "title": "Rental Deposit / Rent Recovery",
        "steps": [
            "Identify rental agreement and deposit proof",
            "Calculate exact amount owed (deposit + interest if applicable)",
            "Send legal notice to landlord (optional but recommended)",
            "Prepare Money Recovery Petition",
            "File case in Small Causes Court with supporting documents",
            "Court issues summons/notice to defendant (landlord)",
            "Attend hearing and present evidence",
            "Receive judgment and execute decree if won",
        ],
        "documents_needed": ["Rental Agreement", "Deposit Payment Proof (receipt/bank transfer)", "ID Proof", "Vacated date proof / key return receipt"],
        "court_fee": "Approx ₹200–₹500 depending on claim amount",
        "time_estimate": "3–6 months",
        "questions": [
            ("landlord_name",    "Landlord's full name"),
            ("landlord_address", "Landlord's current address"),
            ("property_address", "Property address"),
            ("deposit_amount",   "Security deposit amount (₹)"),
            ("vacated_date",     "Date you vacated the house (DD MMM YYYY)"),
            ("rental_start",     "Rental start date (DD MMM YYYY)"),
        ]
    },
    "Employment Dispute": {
        "title": "Wage / Employment Recovery",
        "steps": [
            "Gather employment proof (offer letter, payslips, ID card)",
            "Calculate exact dues (unpaid salary, notice pay, gratuity)",
            "Send written complaint to employer HR",
            "File complaint with Labour Commissioner",
            "Labour conciliation proceedings",
            "If unresolved — file case in Labour Court",
            "Attend hearings and present evidence",
            "Receive order and enforcement",
        ],
        "documents_needed": ["Offer Letter / Appointment Letter", "Payslips", "Termination Letter (if any)", "Bank statements showing salary credits", "ID Proof"],
        "court_fee": "Generally free at Labour Commissioner level",
        "time_estimate": "2–8 months",
        "questions": [
            ("employer_name",    "Employer / Company name"),
            ("employer_address", "Employer address"),
            ("amount_due",       "Total amount due (₹)"),
            ("last_working_day", "Last working day (DD MMM YYYY)"),
            ("designation",      "Your designation / job title"),
        ]
    },
    "Consumer Dispute": {
        "title": "Consumer Complaint",
        "steps": [
            "Collect bill/invoice and evidence of defect or non-delivery",
            "Send written complaint to company/seller",
            "If unresolved in 15 days — file consumer complaint",
            "Determine correct forum (District/State/National based on amount)",
            "File complaint with prescribed form and fee",
            "Forum sends notice to opposite party",
            "Hearing and mediation attempt",
            "Final order and compensation",
        ],
        "documents_needed": ["Invoice / Receipt", "Warranty Card", "Complaint email/letter to company", "Photos of defective product (if applicable)", "ID Proof"],
        "court_fee": "₹100–₹500 depending on claim amount",
        "time_estimate": "3–12 months",
        "questions": [
            ("company_name",     "Company / Seller name"),
            ("company_address",  "Company address"),
            ("product_service",  "Product or service description"),
            ("amount_paid",      "Amount paid (₹)"),
            ("purchase_date",    "Date of purchase (DD MMM YYYY)"),
        ]
    },
    "Financial Dispute": {
        "title": "Cheque Bounce / Loan Recovery",
        "steps": [
            "Collect the bounced cheque and bank memo",
            "Send legal demand notice within 30 days of bounce",
            "Wait 15 days for payment",
            "If unpaid — file criminal complaint under Section 138 NI Act",
            "Court issues summons to accused",
            "Trial proceedings",
            "Conviction and recovery order",
        ],
        "documents_needed": ["Original bounced cheque", "Bank dishonour memo", "Legal demand notice copy", "Proof of legal notice delivery", "ID Proof"],
        "court_fee": "Approx ₹200",
        "time_estimate": "6–18 months",
        "questions": [
            ("accused_name",     "Accused person / company name"),
            ("accused_address",  "Accused address"),
            ("cheque_amount",    "Cheque amount (₹)"),
            ("cheque_date",      "Cheque date (DD MMM YYYY)"),
            ("bounce_date",      "Date cheque bounced (DD MMM YYYY)"),
        ]
    },
    "Family Dispute": {
        "title": "Divorce / Maintenance Petition",
        "steps": [
            "Consult a family lawyer to understand grounds for divorce",
            "Attempt mediation or counselling (court may require this)",
            "Gather marriage certificate, address proof, and evidence",
            "File divorce petition in Family Court under applicable law",
            "Court issues notice to the respondent (spouse)",
            "Mediation attempt by court-appointed counsellor",
            "If unresolved — trial with evidence and witnesses",
            "Final decree of divorce passed by the court",
        ],
        "documents_needed": [
            "Marriage Certificate",
            "Address proof of both parties",
            "Evidence supporting grounds for divorce (photos, messages, etc.)",
            "ID Proof",
            "Details of children / shared assets (if any)",
        ],
        "court_fee": "Approx ₹500–₹2,000",
        "time_estimate": "6 months – 3 years",
        "questions": [
            ("spouse_name",      "Spouse's full name"),
            ("spouse_address",   "Spouse's current address"),
            ("marriage_date",    "Date of marriage (DD MMM YYYY)"),
            ("marriage_place",   "Place of marriage"),
            ("grounds",         "Grounds for divorce (e.g. adultery, cruelty, desertion)"),
        ]
    },
    "Property Dispute": {
        "title": "Property / Encroachment Recovery",
        "steps": [
            "Gather property documents (title deed, tax receipts, survey records)",
            "Send legal notice to the encroaching party",
            "File a civil suit for possession / injunction in Civil Court",
            "Court issues notice to defendant",
            "Attend hearings and present property documents",
            "Court passes order for possession or status quo",
            "Execute court order with help of local authorities if needed",
        ],
        "documents_needed": [
            "Title Deed / Sale Deed",
            "Property Tax Receipts",
            "Survey / Sketch of property",
            "Encroachment evidence (photos, witness statements)",
            "ID Proof",
        ],
        "court_fee": "Approx ₹500–₹5,000 depending on property value",
        "time_estimate": "1–5 years",
        "questions": [
            ("opponent_name",    "Encroaching party's name"),
            ("opponent_address", "Their address"),
            ("property_address", "Property address / survey number"),
            ("nature_of_dispute","Nature of dispute (e.g. encroachment, illegal possession)"),
        ]
    },
    "Motor Accident": {
        "title": "Motor Accident Compensation Claim",
        "steps": [
            "File an FIR at the nearest police station immediately",
            "Collect accident scene evidence (photos, witness contacts)",
            "Obtain medical records and treatment bills",
            "Send claim notice to vehicle owner and insurance company",
            "File claim petition before Motor Accident Claims Tribunal (MACT)",
            "Tribunal issues notice to respondents",
            "Evidence and arguments presented",
            "Compensation award passed by Tribunal",
        ],
        "documents_needed": [
            "FIR copy",
            "Medical records and bills",
            "Photos of accident scene and injuries",
            "Vehicle details of the other party",
            "Insurance policy details",
            "ID Proof / Driving Licence",
        ],
        "court_fee": "Generally free at MACT level",
        "time_estimate": "1–3 years",
        "questions": [
            ("accused_name",     "Name of other vehicle's owner / driver"),
            ("accused_address",  "Their address"),
            ("accident_date",    "Date of accident (DD MMM YYYY)"),
            ("accident_place",   "Place of accident"),
            ("injury_details",   "Brief description of injuries / damage"),
        ]
    },
    "Criminal / Civil Harassment": {
        "title": "Harassment / Protection Order",
        "steps": [
            "Document all incidents with dates, times, and details",
            "Gather evidence — messages, emails, witness statements",
            "File a complaint at the nearest police station",
            "Apply for a protection order in Magistrate Court if needed",
            "Court issues notice to the harassing party",
            "Hearing and evidence presentation",
            "Court passes protection order or restraining order",
        ],
        "documents_needed": [
            "Written complaint with incident details",
            "Screenshots of messages / emails",
            "Witness statements",
            "Medical reports (if physical harm occurred)",
            "ID Proof",
        ],
        "court_fee": "Generally free for complaint filing",
        "time_estimate": "1–6 months",
        "questions": [
            ("harasser_name",    "Name of the harassing person"),
            ("harasser_address", "Their address (if known)"),
            ("incident_dates",   "Dates of incidents (approximate)"),
            ("nature_of_harm",   "Nature of harassment (e.g. threats, stalking, physical)"),
        ]
    },
    # ── New Category Workflows ──
    "Contract Dispute": {
        "title": "Breach of Contract Recovery",
        "steps": [
            "Gather the original contract / agreement document",
            "Identify the specific clauses that were breached",
            "Collect evidence of breach (emails, messages, receipts)",
            "Send a legal notice to the defaulting party",
            "Wait 15–30 days for response",
            "If unresolved — file a civil suit for damages in Civil Court",
            "Attend hearings and present documentary evidence",
            "Receive court decree and execute judgment",
        ],
        "documents_needed": [
            "Original Contract / Agreement",
            "Evidence of breach (correspondence, receipts)",
            "Legal notice copy and delivery proof",
            "ID Proof",
            "Any amendments or addendums to the contract",
        ],
        "court_fee": "Based on suit valuation — typically ₹500–₹10,000",
        "time_estimate": "1–3 years",
        "questions": [
            ("opponent_name",       "Name of the defaulting party"),
            ("opponent_address",    "Their address"),
            ("contract_date",       "Date of the contract / agreement"),
            ("contract_subject",    "Subject matter of the contract"),
            ("breach_details",      "How was the contract breached?"),
            ("claim_amount",        "Damages / amount claimed (₹)"),
        ]
    },
    "Partition Suit": {
        "title": "Partition of Joint Property",
        "steps": [
            "Identify all co-owners / legal heirs of the property",
            "Gather property documents (title deed, revenue records, survey)",
            "Attempt an amicable partition through mediation",
            "If unresolved — file a partition suit in Civil Court",
            "Court appoints a Commissioner to inspect and divide property",
            "Commissioner submits report to the court",
            "Court passes preliminary decree for partition",
            "Final decree passed and property divided / sold",
        ],
        "documents_needed": [
            "Title Deed / Sale Deed",
            "Revenue Records (Patta, Chitta)",
            "Family tree / legal heir certificate",
            "Property Tax Receipts",
            "Survey / Sketch of property",
            "ID Proof",
        ],
        "court_fee": "Based on property value — typically ₹1,000–₹10,000",
        "time_estimate": "2–5 years",
        "questions": [
            ("coowner_names",       "Names of all co-owners / parties"),
            ("opponent_address",    "Address of the opposing party"),
            ("property_address",    "Property address / survey number"),
            ("property_value",      "Approximate property value (₹)"),
            ("share_claimed",       "Your claimed share (e.g. 1/3, 1/4)"),
        ]
    },
    "Succession / Probate": {
        "title": "Succession Certificate / Probate of Will",
        "steps": [
            "Identify whether the deceased left a Will or died intestate",
            "Gather death certificate and family relationship proof",
            "If Will exists — apply for Probate in District / High Court",
            "If no Will — apply for Succession Certificate in District Court",
            "Court publishes notice in newspaper inviting objections",
            "Wait for objection period (usually 45 days)",
            "If no objections — court grants certificate / probate",
            "Use certificate to claim assets, bank accounts, property",
        ],
        "documents_needed": [
            "Death Certificate of the deceased",
            "Original Will (if available)",
            "Legal Heir Certificate",
            "Family relationship proof (birth certificate, ration card)",
            "List of assets and liabilities of the deceased",
            "ID Proof of applicant",
        ],
        "court_fee": "Based on estate value — typically ₹500–₹5,000",
        "time_estimate": "3–12 months",
        "questions": [
            ("deceased_name",       "Name of the deceased"),
            ("death_date",          "Date of death (DD MMM YYYY)"),
            ("relationship",        "Your relationship with the deceased"),
            ("has_will",            "Did the deceased leave a Will? (Yes/No)"),
            ("estate_details",      "Brief description of assets / estate"),
        ]
    },
    "Cybercrime": {
        "title": "Cybercrime Complaint",
        "steps": [
            "Preserve all digital evidence (screenshots, URLs, transaction records)",
            "File a complaint on the National Cyber Crime Portal (cybercrime.gov.in)",
            "Also file an FIR at the nearest Cyber Crime Police Station",
            "If financial fraud — immediately contact your bank to freeze transactions",
            "Provide all evidence to the investigating officer",
            "Cooperate with investigation and forensic analysis",
            "Attend hearings if the case goes to Magistrate Court",
        ],
        "documents_needed": [
            "Screenshots of fraudulent messages / websites",
            "Transaction records / bank statements",
            "Copy of FIR / online complaint acknowledgement",
            "Device details (if hacking involved)",
            "ID Proof",
        ],
        "court_fee": "Free for FIR filing; court fee varies if private complaint",
        "time_estimate": "3–18 months",
        "questions": [
            ("accused_name",        "Name of the accused (if known)"),
            ("accused_address",     "Their address (if known)"),
            ("cyber_crime_type",    "Type of cybercrime (e.g. fraud, hacking, identity theft)"),
            ("incident_date",       "Date of incident (DD MMM YYYY)"),
            ("financial_loss",      "Financial loss amount (₹, if any)"),
            ("evidence_summary",    "Brief summary of evidence you have"),
        ]
    },
    "Child Custody": {
        "title": "Child Custody / Guardianship Petition",
        "steps": [
            "Consult a family lawyer regarding custody rights",
            "Gather evidence showing you are the fit parent / guardian",
            "Attempt mediation for an amicable custody arrangement",
            "File custody petition in Family Court under Guardians and Wards Act",
            "Court considers the welfare of the child as paramount",
            "Court may appoint a welfare officer to investigate",
            "Attend hearings and present evidence",
            "Court passes custody / visitation order",
        ],
        "documents_needed": [
            "Child's birth certificate",
            "Marriage certificate",
            "Evidence of financial stability (income proof, property)",
            "School records of the child",
            "Medical records of the child",
            "Character references / witness statements",
            "ID Proof",
        ],
        "court_fee": "Approx ₹500–₹1,000",
        "time_estimate": "6 months – 2 years",
        "questions": [
            ("spouse_name",         "Name of the other parent"),
            ("spouse_address",      "Their current address"),
            ("child_name",          "Child's name"),
            ("child_age",           "Child's age"),
            ("custody_type",        "Type of custody sought (sole / joint / visitation)"),
            ("grounds_custody",     "Grounds for seeking custody"),
        ]
    },
    "Insurance Dispute": {
        "title": "Insurance Claim Recovery",
        "steps": [
            "Gather the insurance policy document and claim rejection letter",
            "Understand the reason for claim rejection / delay",
            "File a formal grievance with the insurance company",
            "If unresolved — file complaint with IRDAI (Insurance Ombudsman)",
            "If still unresolved — file consumer complaint in Consumer Forum",
            "Attend hearings and present policy documents and evidence",
            "Receive order for claim settlement and compensation",
        ],
        "documents_needed": [
            "Insurance Policy Document",
            "Claim application and supporting documents",
            "Rejection / Repudiation letter from insurer",
            "Medical records (for health / life insurance)",
            "FIR / Survey report (for vehicle / property insurance)",
            "ID Proof",
        ],
        "court_fee": "Nominal — ₹100–₹500 at Consumer Forum",
        "time_estimate": "3–12 months",
        "questions": [
            ("insurer_name",        "Insurance company name"),
            ("insurer_address",     "Insurer's office address"),
            ("policy_number",       "Policy number"),
            ("claim_amount",        "Claim amount (₹)"),
            ("rejection_reason",    "Reason given for rejection / delay"),
            ("policy_type",         "Type of policy (life / health / vehicle / property)"),
        ]
    },
    "Defamation Suit": {
        "title": "Defamation — Compensation & Injunction",
        "steps": [
            "Document the defamatory statements (screenshots, copies, recordings)",
            "Identify whether it is libel (written) or slander (spoken)",
            "Send a cease-and-desist / legal notice to the defamer",
            "If unresolved — file a civil suit for damages in Civil Court",
            "Optionally file a criminal complaint under Section 499 IPC",
            "Court issues notice to the defendant",
            "Attend hearings and present evidence",
            "Court awards damages and / or injunction",
        ],
        "documents_needed": [
            "Proof of defamatory statements (screenshots, newspaper clippings, recordings)",
            "Evidence of damage to reputation (lost business, social harm)",
            "Legal notice copy and delivery proof",
            "Witness statements",
            "ID Proof",
        ],
        "court_fee": "Based on compensation claimed — ₹500–₹5,000",
        "time_estimate": "1–3 years",
        "questions": [
            ("defamer_name",        "Name of the person who defamed you"),
            ("defamer_address",     "Their address"),
            ("defamation_type",     "Type of defamation (written / spoken / online)"),
            ("statement_details",   "What was the defamatory statement?"),
            ("publication_date",    "When was it published / said? (DD MMM YYYY)"),
            ("damages_claimed",     "Compensation amount claimed (₹)"),
        ]
    },
    "Public Interest Litigation": {
        "title": "Public Interest Litigation (PIL)",
        "steps": [
            "Identify a matter of public concern (environment, rights, governance)",
            "Gather evidence and data supporting the public interest issue",
            "Draft the PIL petition with clear prayers / relief sought",
            "File the PIL directly in the High Court or Supreme Court",
            "Court examines whether the PIL is maintainable",
            "If admitted — court issues notice to the government / authorities",
            "Hearings and submission of reports / affidavits",
            "Court passes directions or orders for public benefit",
        ],
        "documents_needed": [
            "Detailed petition explaining the public interest issue",
            "Supporting evidence (reports, data, photographs)",
            "News articles / media reports on the issue",
            "Any government orders or notifications related to the matter",
            "ID Proof of petitioner",
        ],
        "court_fee": "Nominal — ₹50–₹500",
        "time_estimate": "6 months – 3 years",
        "questions": [
            ("authority_name",      "Government body / authority involved"),
            ("authority_address",   "Their office address"),
            ("public_issue",        "Describe the public interest issue"),
            ("affected_area",       "Area / community affected"),
            ("relief_description",  "What relief are you seeking from the court?"),
        ]
    },
    "Government Service Dispute": {
        "title": "Government Service Matter Petition",
        "steps": [
            "Gather all service records (appointment order, pay slips, promotion orders)",
            "File a formal representation / grievance with the department",
            "If unresolved — file an appeal with the appropriate appellate authority",
            "If still unresolved — file OA (Original Application) before CAT / State Tribunal",
            "Tribunal issues notice to the department",
            "Attend hearings and submit service records",
            "Tribunal passes order for relief",
        ],
        "documents_needed": [
            "Appointment Order",
            "Service Book / Records",
            "Pay slips and pension documents",
            "Representation / grievance copy submitted to department",
            "Orders / communications being challenged",
            "ID Proof / Service ID",
        ],
        "court_fee": "₹50 at CAT",
        "time_estimate": "6–18 months",
        "questions": [
            ("department_name",     "Government department / ministry name"),
            ("department_address",  "Department office address"),
            ("designation",         "Your designation / post"),
            ("service_issue",       "Nature of dispute (e.g. transfer, promotion, pension)"),
            ("order_date",          "Date of the order being challenged (DD MMM YYYY)"),
        ]
    },
    "Tax Dispute": {
        "title": "Tax Assessment Appeal",
        "steps": [
            "Review the tax assessment / demand order carefully",
            "Gather all relevant financial documents and returns filed",
            "File a rectification application if there is an apparent error",
            "If not resolved — file an appeal before CIT(A) / GST Appellate Authority",
            "If still aggrieved — appeal to ITAT / GST Appellate Tribunal",
            "Attend hearings and present financial records",
            "Tribunal passes order on the appeal",
            "If needed — further appeal to High Court on questions of law",
        ],
        "documents_needed": [
            "Assessment / Demand Order",
            "Income Tax Returns / GST Returns filed",
            "Financial statements / audit reports",
            "Correspondence with tax authorities",
            "Challan / payment receipts for tax paid",
            "ID Proof / PAN Card",
        ],
        "court_fee": "₹500–₹10,000 depending on tax amount",
        "time_estimate": "6 months – 3 years",
        "questions": [
            ("tax_authority",       "Tax authority (e.g. Income Tax, GST)"),
            ("authority_address",   "Tax office address"),
            ("assessment_year",     "Assessment year / period"),
            ("demand_amount",       "Tax demand amount (₹)"),
            ("dispute_grounds",     "Grounds for disputing the assessment"),
        ]
    },
}

# ─── AI Classifier ───────────────────────────────────────────────────────────
def classify_dispute(message: str) -> tuple[str, str, str]:
    """Classify the dispute based on message keywords."""
    msg_lower = message.lower()
    for keyword, (category, process, court) in DISPUTE_KEYWORDS.items():
        if keyword in msg_lower:
            return category, process, court
    return "General Civil Dispute", "Civil Recovery", "Civil Court"

def get_workflow(category: str) -> dict:
    """Get the workflow for a dispute category."""
    for key in WORKFLOWS:
        if key in category or category in key:
            return WORKFLOWS[key]
    # No match found — return a safe generic fallback instead of silently using Rental
    return {
        "title": "General Civil Dispute",
        "steps": [
            "Document your complaint clearly with dates and facts",
            "Gather all relevant evidence and correspondence",
            "Send a legal notice to the opposing party",
            "Consult a lawyer to identify the correct court and procedure",
            "File the appropriate petition/complaint in the relevant court",
            "Attend hearings and present your evidence",
            "Receive court order or judgment",
        ],
        "documents_needed": ["Written complaint", "Supporting evidence", "ID Proof", "Any relevant agreements or correspondence"],
        "court_fee": "Varies by court and claim type",
        "time_estimate": "Varies",
        "questions": [
            ("opponent_name",    "Name of the opposing party"),
            ("opponent_address", "Their address"),
            ("dispute_details",  "Brief description of the dispute"),
            ("amount_involved",  "Amount or value involved (if any, in ₹)"),
        ]
    }

# ─── Document Generator ──────────────────────────────────────────────────────
def generate_pdf_document(case_data: dict, workflow: dict, output_path: str) -> bool:
    """Generate a legal petition PDF."""
    if not PDF_AVAILABLE:
        return generate_text_document(case_data, workflow, output_path.replace(".pdf", ".txt"))

    try:
        from reportlab.lib.colors import HexColor
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []

        navy   = HexColor("#1a1a2e")
        dark   = HexColor("#333333")
        grey   = HexColor("#666666")
        silver = HexColor("#888888")
        ltgrey = HexColor("#cccccc")

        # Title style
        title_style = ParagraphStyle("LBTitle", parent=styles["Heading1"],
                                     fontSize=14, alignment=TA_CENTER,
                                     spaceAfter=6, textColor=navy)
        sub_style   = ParagraphStyle("LBSub",   parent=styles["Normal"],
                                     fontSize=10, alignment=TA_CENTER,
                                     spaceAfter=4, textColor=dark)
        body_style  = ParagraphStyle("LBBody",  parent=styles["Normal"],
                                     fontSize=11, leading=16,
                                     alignment=TA_JUSTIFY, spaceAfter=8)
        label_style = ParagraphStyle("LBLabel", parent=styles["Normal"],
                                     fontSize=11, leading=16,
                                     textColor=navy, spaceBefore=8)
        heading_style = ParagraphStyle("LBHeading", parent=styles["Heading2"],
                                       fontSize=12, textColor=navy,
                                       spaceBefore=12, spaceAfter=4)

        court_name = case_data.get("court", "Small Causes Court")
        city       = case_data.get("city", "Chennai")
        today      = datetime.date.today().strftime("%d %B %Y")

        # ── Court Header ──
        story.append(Paragraph(f"IN THE {court_name.upper()}", title_style))
        story.append(Paragraph(f"AT {city.upper()}", sub_style))
        story.append(Spacer(1, 0.1 * inch))
        story.append(HRFlowable(width="100%", thickness=2, color=navy))
        story.append(Spacer(1, 0.15 * inch))

        # ── Parties ──
        plaintiff = case_data.get("user_name", "[Plaintiff Name]")
        story.append(Paragraph(f"<b>Plaintiff:</b>", label_style))
        story.append(Paragraph(f"{plaintiff}", body_style))
        story.append(Spacer(1, 0.05 * inch))

        defendant_key = next((k for k in ["landlord_name","employer_name","company_name","accused_name","harasser_name","spouse_name","opponent_name"] if k in case_data), None)
        defendant     = case_data.get(defendant_key, "[Defendant Name]") if defendant_key else "[Defendant Name]"
        story.append(Paragraph(f"<b>Defendant:</b>", label_style))
        story.append(Paragraph(f"{defendant}", body_style))

        address_key = next((k for k in ["landlord_address","employer_address","company_address","accused_address","harasser_address","spouse_address","opponent_address"] if k in case_data), None)
        if address_key and case_data.get(address_key):
            story.append(Paragraph(f"<b>Address:</b>  {case_data[address_key]}", body_style))

        story.append(Spacer(1, 0.1 * inch))

        # ── Subject ──
        subject = build_subject(case_data, workflow)
        story.append(Paragraph(f"<b>Subject:</b>", label_style))
        story.append(Paragraph(f"{subject}", body_style))
        story.append(Spacer(1, 0.1 * inch))

        # ── Facts ──
        story.append(Paragraph("FACTS", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))

        facts = build_facts(case_data, workflow)
        for fact in facts:
            story.append(Paragraph(fact, body_style))

        story.append(Spacer(1, 0.1 * inch))

        # ── Relief Requested ──
        story.append(Paragraph("RELIEF REQUESTED", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))

        relief = build_relief(case_data, workflow)
        for i, r in enumerate(relief, 1):
            story.append(Paragraph(f"{i}. {r}", body_style))

        story.append(Spacer(1, 0.1 * inch))

        # ── Documents Enclosed ──
        story.append(Paragraph("DOCUMENTS ENCLOSED", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))
        for i, doc in enumerate(workflow["documents_needed"], 1):
            story.append(Paragraph(f"{i}. {doc}", body_style))

        story.append(Spacer(1, 0.3 * inch))

        # ── Signature ──
        story.append(Paragraph(f"Date: {today}", body_style))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("______________________________", body_style))
        story.append(Paragraph(f"Signature of Plaintiff", body_style))
        story.append(Paragraph(f"({plaintiff})", body_style))

        story.append(Spacer(1, 0.2 * inch))
        story.append(HRFlowable(width="100%", thickness=0.5, color=ltgrey))
        story.append(Spacer(1, 0.05 * inch))
        story.append(Paragraph(
            "<i>This document was generated by Legal Aid Bot for procedural guidance only. "
            "It does not constitute legal advice. Please consult a qualified advocate for legal representation.</i>",
            ParagraphStyle("Disclaimer", parent=styles["Normal"],
                           fontSize=8, textColor=grey, alignment=TA_CENTER)
        ))

        doc.build(story)
        return True
    except Exception as e:
        # Fallback to text document
        return generate_text_document(case_data, workflow, output_path.replace(".pdf", ".txt"))


def generate_text_document(case_data: dict, workflow: dict, output_path: str) -> bool:
    """Fallback: generate a plain-text legal petition."""
    today = datetime.date.today().strftime("%d %B %Y")
    court = case_data.get("court", "Small Causes Court")
    city  = case_data.get("city", "Chennai")
    plaintiff = case_data.get("user_name", "[Plaintiff Name]")

    defendant_key = next((k for k in ["landlord_name","employer_name","company_name","accused_name","harasser_name","spouse_name","opponent_name"] if k in case_data), None)
    defendant = case_data.get(defendant_key, "[Defendant Name]") if defendant_key else "[Defendant Name]"

    # Resolve defendant address from various possible keys
    address_key = next((k for k in ["landlord_address","employer_address","company_address","accused_address","harasser_address","spouse_address","opponent_address"] if k in case_data), None)
    defendant_address = case_data.get(address_key, "") if address_key else ""

    subject = build_subject(case_data, workflow)

    lines = [
        "=" * 66,
        f"        IN THE {court.upper()}",
        f"                AT {city.upper()}",
        "=" * 66,
        "",
        f"Plaintiff:",
        f"{plaintiff}",
        "",
        f"Defendant:",
        f"{defendant}",
    ]
    if defendant_address:
        lines.append(f"Address: {defendant_address}")
    lines += [
        "",
        f"Subject:",
        f"{subject}",
        "",
        "-" * 66,
        "FACTS",
        "-" * 66,
    ]
    for fact in build_facts(case_data, workflow):
        lines.append(textwrap.fill(fact, 60, subsequent_indent='   '))
        lines.append("")
    lines += ["-" * 66, "RELIEF REQUESTED", "-" * 66]
    for i, r in enumerate(build_relief(case_data, workflow), 1):
        lines.append(f"{i}. {r}")
    lines += [
        "",
        "-" * 66,
        "DOCUMENTS ENCLOSED",
        "-" * 66,
    ]
    for i, d in enumerate(workflow["documents_needed"], 1):
        lines.append(f"{i}. {d}")
    lines += [
        "",
        f"Date: {today}",
        "",
        "_______________________________",
        f"Signature of Plaintiff",
        f"({plaintiff})",
        "",
        "─" * 66,
        "DISCLAIMER: This document is generated by Legal Aid Bot for",
        "procedural guidance only. Not legal advice.",
        "=" * 66,
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


def txt_to_pdf(txt_path: str, pdf_path: str) -> bool:
    """Read a .txt legal document and convert it to a formatted PDF."""
    if not PDF_AVAILABLE:
        print("  reportlab is not installed. Cannot convert to PDF.")
        return False

    try:
        from reportlab.lib.colors import HexColor

        with open(txt_path, "r", encoding="utf-8") as f:
            raw_lines = f.read().splitlines()

        doc = SimpleDocTemplate(
            pdf_path, pagesize=A4,
            rightMargin=0.75 * inch, leftMargin=0.75 * inch,
            topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        )
        styles = getSampleStyleSheet()
        story = []

        navy   = HexColor("#1a1a2e")
        dark   = HexColor("#333333")
        grey   = HexColor("#666666")
        silver = HexColor("#888888")

        # Styles
        court_header = ParagraphStyle(
            "CourtHeader", parent=styles["Heading1"],
            fontSize=14, alignment=TA_CENTER,
            spaceAfter=2, textColor=navy,
        )
        section_title = ParagraphStyle(
            "SectionTitle", parent=styles["Heading2"],
            fontSize=12, textColor=navy,
            spaceBefore=10, spaceAfter=4,
        )
        label_style = ParagraphStyle(
            "LabelStyle", parent=styles["Normal"],
            fontSize=11, textColor=navy, spaceBefore=6,
        )
        body_style = ParagraphStyle(
            "BodyStyle", parent=styles["Normal"],
            fontSize=11, leading=16,
            alignment=TA_JUSTIFY, spaceAfter=6,
        )
        small_style = ParagraphStyle(
            "SmallStyle", parent=styles["Normal"],
            fontSize=8, textColor=grey, alignment=TA_CENTER,
        )

        separator_chars = {"=", "-", "\u2500"}

        for line in raw_lines:
            stripped = line.strip()

            # Skip pure separator lines (===, ---, ───)
            if stripped and all(c in separator_chars for c in stripped):
                story.append(HRFlowable(width="100%", thickness=1.5 if "=" in stripped else 0.5, color=navy if "=" in stripped else silver))
                story.append(Spacer(1, 0.05 * inch))
                continue

            # Empty line → spacer
            if not stripped:
                story.append(Spacer(1, 0.1 * inch))
                continue

            # Court header lines (IN THE ... / AT ...)
            if stripped.startswith("IN THE ") or stripped.startswith("AT "):
                story.append(Paragraph(stripped, court_header))
                continue

            # Section headers (FACTS, RELIEF REQUESTED, etc.)
            if stripped.isupper() and len(stripped) > 3 and not stripped.startswith("("):
                story.append(Paragraph(stripped, section_title))
                continue

            # Labels (Plaintiff:, Defendant:, Subject:, Address:, Date:)
            if ":" in stripped and stripped.split(":")[0].strip() in (
                "Plaintiff", "Defendant", "Subject", "Address", "Date"
            ):
                parts = stripped.split(":", 1)
                label = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                story.append(Paragraph(f"<b>{label}:</b>  {value}", label_style))
                continue

            # Signature line
            if stripped.startswith("___"):
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph(stripped, body_style))
                continue

            # Disclaimer line
            if "DISCLAIMER" in stripped or "procedural guidance" in stripped:
                story.append(Paragraph(f"<i>{stripped}</i>", small_style))
                continue

            # Regular body text
            story.append(Paragraph(stripped, body_style))

        doc.build(story)
        return True

    except Exception as e:
        print(f"  Error converting to PDF: {e}")
        return False


def build_subject(case_data: dict, workflow: dict) -> str:
    """Build a subject line for the petition based on dispute type."""
    if "deposit_amount" in case_data:
        return "Recovery of Security Deposit"
    elif "amount_due" in case_data:
        return "Recovery of Unpaid Wages / Dues"
    elif "amount_paid" in case_data:
        return "Consumer Complaint — Defective Product / Service"
    elif "cheque_amount" in case_data:
        return "Dishonour of Cheque — Recovery of Amount"
    elif "nature_of_dispute" in case_data:
        return "Property Dispute — " + case_data.get("nature_of_dispute", "Recovery")
    elif "injury_details" in case_data:
        return "Motor Accident — Compensation Claim"
    elif "nature_of_harm" in case_data:
        return "Harassment — Protection Order"
    elif "grounds" in case_data:
        return "Family Dispute — " + case_data.get("grounds", "Divorce Petition")
    elif "contract_subject" in case_data:
        return "Breach of Contract — " + case_data.get("contract_subject", "Recovery")
    elif "share_claimed" in case_data:
        return "Partition of Joint Property"
    elif "estate_details" in case_data:
        return "Succession Certificate / Probate"
    elif "cyber_crime_type" in case_data:
        return "Cybercrime Complaint — " + case_data.get("cyber_crime_type", "Online Fraud")
    elif "custody_type" in case_data:
        return "Child Custody — " + case_data.get("custody_type", "Custody Petition")
    elif "policy_number" in case_data:
        return "Insurance Claim Recovery"
    elif "defamation_type" in case_data:
        return "Defamation — Compensation & Injunction"
    elif "public_issue" in case_data:
        return "Public Interest Litigation"
    elif "service_issue" in case_data:
        return "Government Service Dispute — " + case_data.get("service_issue", "Service Matter")
    elif "demand_amount" in case_data:
        return "Tax Assessment Appeal"
    else:
        return workflow.get("title", "General Civil Dispute")


def build_facts(case_data: dict, workflow: dict) -> list[str]:
    facts = []
    plaintiff = case_data.get("user_name", "The plaintiff")
    court     = case_data.get("court", "this court")

    if "deposit_amount" in case_data:
        facts = [
            f"The plaintiff paid a security deposit of ₹{case_data.get('deposit_amount', 'the said amount')} to the defendant for renting the property located at {case_data.get('property_address', 'the said property')}.",
            f"The plaintiff vacated the premises on {case_data.get('vacated_date', 'the said date')} but the defendant has failed to return the deposit.",
            f"Despite repeated requests, the defendant has wrongfully retained the security deposit of ₹{case_data.get('deposit_amount', 'the said amount')}.",
            f"The plaintiff has suffered financial loss and mental agony due to the wrongful retention of the deposit by the defendant.",
        ]
    elif "amount_due" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, was employed by {case_data.get('employer_name', 'the defendant')} as {case_data.get('designation', 'an employee')} at {case_data.get('employer_address', 'the said establishment')}.",
            f"The plaintiff's last working day was {case_data.get('last_working_day', 'the said date')}.",
            f"The defendant has failed to pay dues amounting to ₹{case_data.get('amount_due', 'the said amount')} which include salary, notice pay, and other statutory dues.",
            f"Despite repeated requests and representations, the defendant has not settled the outstanding dues.",
        ]
    elif "amount_paid" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, purchased {case_data.get('product_service', 'the product/service')} from {case_data.get('company_name', 'the defendant')} on {case_data.get('purchase_date', 'the said date')} for ₹{case_data.get('amount_paid', 'the said amount')}.",
            f"The said product/service was defective / not delivered as promised by the defendant.",
            f"The plaintiff duly informed the defendant but no corrective action has been taken.",
            f"The plaintiff has suffered financial loss due to the unfair trade practice of the defendant.",
        ]
    elif "cheque_amount" in case_data:
        facts = [
            f"The defendant, {case_data.get('accused_name', 'the defendant')}, issued a cheque for ₹{case_data.get('cheque_amount', 'the said amount')} dated {case_data.get('cheque_date', 'the said date')} in favour of the plaintiff.",
            f"The said cheque was presented for encashment and was dishonoured by the bank on {case_data.get('bounce_date', 'the said date')} due to insufficient funds.",
            f"A legal demand notice was duly served upon the defendant demanding payment within 15 days.",
            f"Despite receipt of the notice, the defendant has failed to make payment of the said amount.",
        ]
    elif "contract_subject" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, entered into a contract / agreement with {case_data.get('opponent_name', 'the defendant')} on {case_data.get('contract_date', 'the said date')} regarding {case_data.get('contract_subject', 'the said subject matter')}.",
            f"The defendant has breached the terms of the said contract by {case_data.get('breach_details', 'failing to fulfil the agreed obligations')}.",
            f"Despite repeated requests and legal notice, the defendant has failed to remedy the breach or pay the damages amounting to ₹{case_data.get('claim_amount', 'the said amount')}.",
            f"The plaintiff has suffered financial loss and hardship due to the breach of contract by the defendant.",
        ]
    elif "share_claimed" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, is a co-owner / legal heir of the property situated at {case_data.get('property_address', 'the said property')}.",
            f"The other co-owners include {case_data.get('coowner_names', 'the defendants')}.",
            f"The plaintiff is entitled to a share of {case_data.get('share_claimed', 'the said share')} in the said property.",
            f"Despite amicable efforts, the defendants have refused to agree to a fair partition of the property.",
            f"The plaintiff is therefore compelled to seek partition through this Hon'ble Court.",
        ]
    elif "estate_details" in case_data:
        facts = [
            f"The deceased, {case_data.get('deceased_name', 'the deceased')}, passed away on {case_data.get('death_date', 'the said date')}.",
            f"The plaintiff, {plaintiff}, is the {case_data.get('relationship', 'legal heir')} of the deceased.",
            f"The estate of the deceased includes {case_data.get('estate_details', 'the said assets')}.",
            f"The plaintiff requires a {'Probate of Will' if case_data.get('has_will', '').lower() == 'yes' else 'Succession Certificate'} to claim the assets of the deceased.",
        ]
    elif "cyber_crime_type" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, is a victim of cybercrime of the nature: {case_data.get('cyber_crime_type', 'online fraud')}.",
            f"The incident occurred on {case_data.get('incident_date', 'the said date')}.",
            f"The plaintiff has suffered a financial loss of ₹{case_data.get('financial_loss', 'the said amount')} due to the said cybercrime.",
            f"Evidence including {case_data.get('evidence_summary', 'digital records and screenshots')} has been preserved.",
            f"The plaintiff has filed / is filing a complaint with the Cyber Crime Cell for investigation.",
        ]
    elif "custody_type" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, is the parent of the minor child {case_data.get('child_name', 'the child')}, aged {case_data.get('child_age', 'minor')}.",
            f"The defendant, {case_data.get('spouse_name', 'the other parent')}, is the other parent of the said child.",
            f"The plaintiff seeks {case_data.get('custody_type', 'custody')} custody of the child on the following grounds: {case_data.get('grounds_custody', 'welfare and best interest of the child')}.",
            f"The plaintiff is financially stable and capable of providing a safe and nurturing environment for the child.",
        ]
    elif "policy_number" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, holds an insurance policy (Policy No. {case_data.get('policy_number', 'N/A')}) with {case_data.get('insurer_name', 'the defendant insurance company')}.",
            f"The plaintiff filed a legitimate claim for ₹{case_data.get('claim_amount', 'the said amount')} under the said policy.",
            f"The defendant insurance company has rejected / delayed the claim citing the reason: {case_data.get('rejection_reason', 'not specified')}.",
            f"The plaintiff contends that the rejection is arbitrary and contrary to the terms of the policy.",
            f"The plaintiff has exhausted the grievance redressal mechanism of the insurer without resolution.",
        ]
    elif "defamation_type" in case_data:
        facts = [
            f"The defendant, {case_data.get('defamer_name', 'the defendant')}, published / stated defamatory content about the plaintiff on {case_data.get('publication_date', 'the said date')}.",
            f"The defamatory statement was: \"{case_data.get('statement_details', 'the said defamatory statement')}\".",
            f"The defamation was of the nature: {case_data.get('defamation_type', 'written / spoken')}.",
            f"The plaintiff's reputation has been severely damaged, causing personal, professional, and financial harm.",
            f"The plaintiff claims compensation of ₹{case_data.get('damages_claimed', 'the said amount')} for the damage caused.",
        ]
    elif "public_issue" in case_data:
        facts = [
            f"The petitioner, {plaintiff}, brings this Public Interest Litigation for the benefit of the public at large.",
            f"The issue concerns: {case_data.get('public_issue', 'the said public interest matter')}.",
            f"The government body / authority involved is {case_data.get('authority_name', 'the concerned authority')}.",
            f"The affected area / community is {case_data.get('affected_area', 'the said area')}.",
            "The petitioner seeks the following relief: " + case_data.get('relief_description', 'appropriate directions from this Honourable Court') + ".",
        ]
    elif "service_issue" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, is a government employee serving as {case_data.get('designation', 'the said post')} in {case_data.get('department_name', 'the said department')}.",
            f"The nature of the dispute is: {case_data.get('service_issue', 'the said service matter')}.",
            f"The impugned order dated {case_data.get('order_date', 'the said date')} is arbitrary, illegal, and in violation of service rules.",
            f"The plaintiff filed a representation / grievance with the department but no relief was granted.",
            f"The plaintiff is therefore compelled to approach this Hon'ble Tribunal for redressal.",
        ]
    elif "demand_amount" in case_data:
        facts = [
            f"The plaintiff, {plaintiff}, is an assessee under the {case_data.get('tax_authority', 'the said tax authority')}.",
            f"The tax authority has raised a demand of ₹{case_data.get('demand_amount', 'the said amount')} for the assessment year {case_data.get('assessment_year', 'the said period')}.",
            f"The plaintiff contends that the assessment is erroneous on the following grounds: {case_data.get('dispute_grounds', 'the said grounds')}.",
            f"The plaintiff has duly filed all returns and paid applicable taxes.",
            f"The plaintiff seeks quashing / modification of the impugned assessment order.",
        ]
    else:
        facts = [
            f"The plaintiff, {plaintiff}, brings this petition before this Hon'ble Court seeking relief as detailed herein.",
            "The facts of the matter are as set out in the accompanying affidavit.",
        ]
    return facts


def build_relief(case_data: dict, workflow: dict) -> list[str]:
    amount_key = next((k for k in ["deposit_amount","amount_due","amount_paid","cheque_amount","claim_amount","financial_loss","damages_claimed","demand_amount"] if k in case_data), None)
    amount = case_data.get(amount_key, "the disputed amount") if amount_key else "the disputed amount"

    # Special relief for non-monetary cases
    if "share_claimed" in case_data:
        return [
            f"Direct partition of the property and allotment of the plaintiff's rightful share of {case_data.get('share_claimed', 'the said share')}.",
            "If partition in kind is not possible, direct sale of the property and distribution of proceeds.",
            "Award costs of this petition to the plaintiff.",
            "Pass such other and further orders as this Hon'ble Court deems fit and proper in the interest of justice.",
        ]
    elif "estate_details" in case_data:
        cert_type = "Probate of Will" if case_data.get("has_will", "").lower() == "yes" else "Succession Certificate"
        return [
            f"Grant {cert_type} in favour of the plaintiff for the estate of the deceased.",
            "Direct the concerned authorities / banks to release the assets of the deceased to the plaintiff.",
            "Pass such other and further orders as this Hon'ble Court deems fit and proper in the interest of justice.",
        ]
    elif "custody_type" in case_data:
        return [
            f"Grant {case_data.get('custody_type', 'custody')} custody of the minor child to the plaintiff.",
            "Direct appropriate visitation rights for the non-custodial parent.",
            "Direct the defendant to pay child maintenance as deemed appropriate.",
            "Pass such other and further orders as this Hon'ble Court deems fit and proper in the interest of justice.",
        ]
    elif "public_issue" in case_data:
        return [
            f"Issue appropriate directions to the concerned authorities regarding: {case_data.get('public_issue', 'the said matter')}.",
            "Direct the authorities to file a status report / action taken report.",
            "Pass such other and further orders as this Hon'ble Court deems fit and proper in the interest of justice.",
        ]
    elif "service_issue" in case_data:
        return [
            f"Quash / set aside the impugned order dated {case_data.get('order_date', 'the said date')}.",
            "Direct the department to grant the rightful relief to the plaintiff.",
            "Award costs of this petition to the plaintiff.",
            "Pass such other and further orders as this Hon'ble Tribunal deems fit and proper in the interest of justice.",
        ]
    elif "demand_amount" in case_data:
        return [
            f"Set aside / modify the impugned assessment order raising demand of ₹{amount}.",
            "Direct refund of any excess tax paid with applicable interest.",
            "Pass such other and further orders as this Hon'ble Tribunal deems fit and proper in the interest of justice.",
        ]
    else:
        return [
            f"Recovery of ₹{amount} with applicable interest.",
            "Award costs of this petition to the plaintiff.",
            "Pass such other and further orders as this Hon'ble Court deems fit and proper in the interest of justice.",
        ]


# ─── Case Database (JSON file) ───────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_PATH = os.path.join(OUTPUT_DIR, "case_database.json")

def load_db() -> dict:
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            return json.load(f)
    return {"cases": []}

def save_db(db: dict):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def create_case(case_data: dict, workflow: dict, court: str) -> str:
    db = load_db()
    case_id = f"SC-{1000 + len(db['cases']) + 1}"
    filing_date  = datetime.date.today()
    deadline     = filing_date + datetime.timedelta(days=30)
    hearing_date = filing_date + datetime.timedelta(days=45)

    entry = {
        "case_id":       case_id,
        "phone":         case_data.get("phone", "N/A"),
        "user_name":     case_data.get("user_name", "Unknown"),
        "case_type":     workflow["title"],
        "court":         court,
        "filing_date":   str(filing_date),
        "next_deadline": str(deadline),
        "deadline_label":"Evidence Submission",
        "hearing_date":  str(hearing_date),
        "status":        "Filed",
        "case_data":     case_data,
    }
    db["cases"].append(entry)
    save_db(db)
    return case_id


def check_reminders():
    db = load_db()
    today = datetime.date.today()
    reminders = []
    for case in db["cases"]:
        deadline = datetime.date.fromisoformat(case["next_deadline"])
        days_left = (deadline - today).days
        if days_left <= 7:
            reminders.append((case, days_left))
    return reminders


def display_case_tracker(case_id: str):
    db = load_db()
    for case in db["cases"]:
        if case["case_id"] == case_id:
            header(f"📋 CASE TRACKER — {case_id}")
            print(f"  {'Case ID':<22}: {C.BOLD}{case['case_id']}{C.RESET}")
            print(f"  {'Case Type':<22}: {case['case_type']}")
            print(f"  {'Court':<22}: {case['court']}")
            print(f"  {'Status':<22}: {C.GREEN}{case['status']}{C.RESET}")
            print(f"  {'Filing Date':<22}: {case['filing_date']}")
            print(f"  {'Next Deadline':<22}: {C.YELLOW}{case['next_deadline']}{C.RESET}  ({case['deadline_label']})")
            print(f"  {'Hearing Date':<22}: {case['hearing_date']}")
            print()
            return
    print(f"  {C.RED}Case {case_id} not found.{C.RESET}")


# ─── Main Bot Flow ────────────────────────────────────────────────────────────
def run_bot():
    os.system("clear" if os.name == "posix" else "cls")

    # ── WELCOME ──────────────────────────────────────────────────────────────
    print(f"\n  {C.BOLD}{C.BLUE}{'═' * 66}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}  ⚖️   LEGAL AID BOT — Citizen Legal Assistance System{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}  📱  Terminal Prototype (WhatsApp Backend Simulation){C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}{'═' * 66}{C.RESET}")
    print()
    info("This system provides procedural guidance only — not legal advice.")
    info("Type 'quit' at any prompt to exit.\n")

    # Check for pending reminders
    reminders = check_reminders()
    if reminders:
        print(f"  {C.YELLOW}{'─' * 66}{C.RESET}")
        print(f"  {C.YELLOW}🔔  PENDING REMINDERS{C.RESET}")
        for case, days_left in reminders:
            urgency = C.RED if days_left <= 3 else C.YELLOW
            print(f"  {urgency}  Case {case['case_id']}: {case['deadline_label']} in {days_left} day(s) — {case['next_deadline']}{C.RESET}")
        print(f"  {C.YELLOW}{'─' * 66}{C.RESET}\n")

    # ── STEP 1: User sends message ────────────────────────────────────────────
    step_banner(1, "Message Received")
    bot(
        "Hello! I'm your Legal Aid Assistant. 👋\n\n"
        "I can help you understand legal procedures for disputes like:\n"
        "• Security deposit / rent recovery\n"
        "• Employment / salary disputes\n"
        "• Consumer complaints\n"
        "• Cheque bounce / loan recovery\n"
        "• Contract disputes\n"
        "• Partition suits\n"
        "• Succession / probate\n"
        "• Cybercrime complaints\n"
        "• Child custody\n"
        "• Insurance disputes\n"
        "• Defamation suits\n"
        "• Public interest litigation\n"
        "• Government service / tax disputes\n"
        "• And more...\n\n"
        "Please describe your legal problem in your own words."
    )

    user_name = user_input("Your name")
    if user_name.lower() == "quit": return
    phone_sim = "91" + "9" * 10  # Simulated phone

    user_message = user_input("Describe your problem")
    if user_message.lower() == "quit": return

    # ── STEP 2: AI Classification ─────────────────────────────────────────────
    step_banner(2, "AI Dispute Classification 🧠")
    thinking("Classifying your dispute")

    category, process, court = classify_dispute(user_message)
    workflow = get_workflow(category)

    print(f"\n  {C.CYAN}Classification Results:{C.RESET}")
    print(f"  {'Dispute Category':<24}: {C.BOLD}{category}{C.RESET}")
    print(f"  {'Legal Process':<24}: {C.BOLD}{process}{C.RESET}")
    print(f"  {'Recommended Court':<24}: {C.BOLD}{court}{C.RESET}")
    print()

    # ── STEP 3: Legal Workflow ────────────────────────────────────────────────
    step_banner(3, "Legal Workflow Retrieved 📚")
    bot(
        f"I can help you with: {workflow['title']}\n\n"
        "DISCLAIMER: This system provides procedural guidance only\n"
        "and does not constitute legal advice.\n\n"
        "Here is the step-by-step legal process:\n\n" +
        "\n".join(f"  Step {i}: {s}" for i, s in enumerate(workflow["steps"], 1)) +
        f"\n\n⏱  Estimated time: {workflow['time_estimate']}"
    )

    # ── STEP 4: Confirm proceeding ────────────────────────────────────────────
    step_banner(4, "First Response 💬")
    bot(
        "Do you have the key documents needed for this case?\n\n"
        "Required documents:\n" +
        "\n".join(f"  • {d}" for d in workflow["documents_needed"]) +
        "\n\nReply:\n  1 — Yes, I have them\n  2 — No / Some are missing"
    )

    doc_reply = user_input("Your reply (1 or 2)")
    if doc_reply.lower() == "quit": return

    if doc_reply.strip() == "2":
        warning("You are missing some documents. You can still proceed but")
        warning("missing documents may weaken your case.")
        bot(
            "⚠️  WARNING\n\n"
            "Cases without key documents may face scrutiny during filing.\n"
            "Try to obtain the following before filing:\n\n" +
            "\n".join(f"  ⚠ {d}" for d in workflow["documents_needed"]) +
            "\n\nYou can upload document photos via WhatsApp in the real app.\n"
            "We will continue with your available information."
        )

    # ── STEP 5 & 6: Collect case information ─────────────────────────────────
    step_banner(5, "Document Evidence Collection 📄")
    bot(
        "Please enter the following case details.\n"
        "(Press Enter to skip optional fields)"
    )

    case_data = {
        "user_name": user_name,
        "phone":     phone_sim,
        "court":     court,
        "city":      "Chennai",  # default — can be collected
    }

    for field_key, field_label in workflow["questions"]:
        val = user_input(field_label)
        if val.lower() == "quit": return
        if val:
            case_data[field_key] = val

    # ── STEP 7: Document Generation ───────────────────────────────────────────
    step_banner(7, "Document Generator ⚙️")
    thinking("Generating legal petition document")

    safe_name = user_name.replace(" ", "_")
    txt_filename = f"Legal_Petition_{safe_name}.txt"
    pdf_filename = f"Legal_Petition_{safe_name}.pdf"
    txt_path = os.path.join(OUTPUT_DIR, txt_filename)
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    # Always generate text first
    success_gen = generate_text_document(case_data, workflow, txt_path)

    # Then convert text to PDF
    pdf_gen = False
    if success_gen:
        success(f"Text document generated: {txt_filename}")
        thinking("Converting to PDF")
        pdf_gen = txt_to_pdf(txt_path, pdf_path)
        if pdf_gen:
            success(f"PDF generated: {pdf_filename}")

    output_filename = pdf_filename if pdf_gen else txt_filename

    if success_gen:
        file_list = f"  Text: {txt_filename}"
        if pdf_gen:
            file_list += f"\n  PDF:  {pdf_filename}"
        bot(
            "Your legal petition draft is ready!\n\n"
            + file_list + "\n\n"
            "Next steps:\n"
            "  1. Download and review the document carefully\n"
            "  2. Fill in any missing details\n"
            "  3. Get it verified by a local advocate if possible\n"
            "  4. Print 3 copies before filing\n\n"
            "The documents have been saved to your outputs folder."
        )
    else:
        warning("Document generation failed.")

    # ── STEP 8: Procedural Guidance ───────────────────────────────────────────
    step_banner(8, "Procedural Guidance 🧭")
    bot(
        f"📋 NEXT STEPS — Filing in {court}\n\n"
        "1. Print the complaint document (3 copies)\n"
        "2. Attach all supporting documents:\n" +
        "\n".join(f"     • {d}" for d in workflow["documents_needed"]) +
        f"\n3. Court filing fee: {workflow['court_fee']}\n"
        "4. Visit the court registry during working hours\n"
        "   (usually 10 AM – 1 PM on weekdays)\n"
        "5. Submit documents and obtain filing number\n"
        "6. Keep all receipts and acknowledgements safely"
    )

    # ── STEP 9: Case Tracker ──────────────────────────────────────────────────
    step_banner(9, "Case Tracker Creation 📅")
    bot(
        "Would you like to create a case tracking entry?\n\n"
        "This will:\n"
        "  ✅ Track your deadlines\n"
        "  ✅ Send reminders before important dates\n"
        "  ✅ Prepare you for hearings\n\n"
        "Reply:\n  1 — Yes, track my case\n  2 — No thanks"
    )

    track_reply = user_input("Your reply (1 or 2)")
    if track_reply.lower() == "quit": return

    case_id = None
    if track_reply.strip() == "1":
        thinking("Creating case entry in database")
        case_id = create_case(case_data, workflow, court)
        success(f"Case created with ID: {case_id}")
        display_case_tracker(case_id)

        # ── STEP 10: Reminders ────────────────────────────────────────────────
        step_banner(10, "Reminder System 🔔")
        deadline_dt = datetime.date.today() + datetime.timedelta(days=30)
        hearing_dt  = datetime.date.today() + datetime.timedelta(days=45)

        bot(
            "🔔 AUTOMATIC REMINDERS SCHEDULED\n\n"
            f"📌 Evidence Submission Deadline: {deadline_dt.strftime('%d %B %Y')}\n"
            f"   → Reminder: 3 days before ({(deadline_dt - datetime.timedelta(days=3)).strftime('%d %B %Y')})\n\n"
            f"📌 First Hearing: {hearing_dt.strftime('%d %B %Y')}\n"
            f"   → Reminder: 2 days before ({(hearing_dt - datetime.timedelta(days=2)).strftime('%d %B %Y')})\n\n"
            "In the WhatsApp version, you would receive automatic\n"
            "reminders directly on your phone."
        )

        # ── STEP 11: Hearing Preparation ──────────────────────────────────────
        step_banner(11, "Hearing Preparation 📋")
        bot(
            "📋 HEARING PREPARATION CHECKLIST\n\n"
            "Documents to bring on the hearing day:\n"
            "  ☐ Filed complaint / petition copy\n" +
            "".join(f"  ☐ {d}\n" for d in workflow["documents_needed"]) +
            "  ☐ Government ID proof\n"
            "  ☐ Any correspondence with the respondent\n\n"
            "In the courtroom:\n"
            "  • Speak clearly and respectfully to the judge\n"
            "  • Present facts briefly and stick to the point\n"
            "  • Submit evidence when the judge requests\n"
            "  • Do not interrupt the opposing party\n"
            "  • Request an interpreter if needed"
        )

    # ── STEP 12: Error Prevention ─────────────────────────────────────────────
    step_banner(12, "Error Prevention Check ⚠️")
    thinking("Running document completeness check")

    missing = []
    if "deposit_amount" in case_data or "amount_due" in case_data:
        if not case_data.get("property_address") and not case_data.get("employer_address"):
            missing.append("Respondent Address")
    if not case_data.get("user_name"):
        missing.append("Complainant Name")

    if missing:
        warning("Some details may be incomplete:")
        for m in missing:
            print(f"  {C.YELLOW}  ⚠ Missing: {m}{C.RESET}")
        bot(
            "⚠️  COMPLETENESS WARNING\n\n"
            "The following may need to be added before filing:\n" +
            "\n".join(f"  ⚠ {m}" for m in missing) +
            "\n\nPlease review your petition before submitting."
        )
    else:
        success("All required fields are present. Document looks complete!")

    # ── FINAL SUMMARY ─────────────────────────────────────────────────────────
    header("🎉 SESSION COMPLETE — SUMMARY")
    print(f"  {C.BOLD}User        :{C.RESET} {user_name}")
    print(f"  {C.BOLD}Dispute     :{C.RESET} {category}")
    print(f"  {C.BOLD}Process     :{C.RESET} {process}")
    print(f"  {C.BOLD}Court       :{C.RESET} {court}")
    print(f"  {C.BOLD}Document    :{C.RESET} {output_filename}")
    if case_id:
        print(f"  {C.BOLD}Case ID     :{C.RESET} {C.GREEN}{case_id}{C.RESET}")
    print()
    bot(
        "✅ You have completed the legal guidance session.\n\n"
        "Your next action:\n"
        "  → Review and print the generated petition\n"
        f"  → Visit {court} during filing hours\n"
        "  → Carry all supporting documents\n\n"
        "Important: This is procedural guidance. For legal\n"
        "representation, consult a qualified advocate.\n\n"
        "Good luck with your case! ⚖️"
    )

    # Final file summary
    print(f"\n  {C.DIM}{'─' * 66}")
    print(f"  📁 Output files saved to: /mnt/user-data/outputs/")
    print(f"  📄 Petition    : {output_filename}")
    if case_id:
        print(f"  📊 Case DB     : case_database.json")
    print(f"  {'─' * 66}{C.RESET}\n")

    return output_path, case_id


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        result = run_bot()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Session ended by user.{C.RESET}\n")