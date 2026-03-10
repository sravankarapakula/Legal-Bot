"""
Document Generator — PDF and text petition generation.
"""

import os
import datetime
import textwrap

# ─── PDF Generation (using ReportLab) ────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ─── Subject / Facts / Relief builders ───────────────────────────────────────

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


# ─── Defendant key helpers ───────────────────────────────────────────────────

_DEFENDANT_NAME_KEYS = [
    "landlord_name", "employer_name", "company_name",
    "accused_name", "harasser_name", "spouse_name", "opponent_name",
]
_DEFENDANT_ADDR_KEYS = [
    "landlord_address", "employer_address", "company_address",
    "accused_address", "harasser_address", "spouse_address", "opponent_address",
]


def _resolve_defendant(case_data: dict):
    key = next((k for k in _DEFENDANT_NAME_KEYS if k in case_data), None)
    return case_data.get(key, "[Defendant Name]") if key else "[Defendant Name]"


def _resolve_defendant_address(case_data: dict):
    key = next((k for k in _DEFENDANT_ADDR_KEYS if k in case_data), None)
    return case_data.get(key, "") if key else ""


# ─── PDF Document ─────────────────────────────────────────────────────────────

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

        title_style   = ParagraphStyle("LBTitle", parent=styles["Heading1"],
                                       fontSize=14, alignment=TA_CENTER,
                                       spaceAfter=6, textColor=navy)
        sub_style     = ParagraphStyle("LBSub", parent=styles["Normal"],
                                       fontSize=10, alignment=TA_CENTER,
                                       spaceAfter=4, textColor=dark)
        body_style    = ParagraphStyle("LBBody", parent=styles["Normal"],
                                       fontSize=11, leading=16,
                                       alignment=TA_JUSTIFY, spaceAfter=8)
        label_style   = ParagraphStyle("LBLabel", parent=styles["Normal"],
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
        story.append(Paragraph("<b>Plaintiff:</b>", label_style))
        story.append(Paragraph(f"{plaintiff}", body_style))
        story.append(Spacer(1, 0.05 * inch))

        defendant = _resolve_defendant(case_data)
        story.append(Paragraph("<b>Defendant:</b>", label_style))
        story.append(Paragraph(f"{defendant}", body_style))

        defendant_addr = _resolve_defendant_address(case_data)
        if defendant_addr:
            story.append(Paragraph(f"<b>Address:</b>  {defendant_addr}", body_style))

        story.append(Spacer(1, 0.1 * inch))

        # ── Subject ──
        subject = build_subject(case_data, workflow)
        story.append(Paragraph("<b>Subject:</b>", label_style))
        story.append(Paragraph(f"{subject}", body_style))
        story.append(Spacer(1, 0.1 * inch))

        # ── Facts ──
        story.append(Paragraph("FACTS", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))
        for fact in build_facts(case_data, workflow):
            story.append(Paragraph(fact, body_style))
        story.append(Spacer(1, 0.1 * inch))

        # ── Relief Requested ──
        story.append(Paragraph("RELIEF REQUESTED", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))
        for i, r in enumerate(build_relief(case_data, workflow), 1):
            story.append(Paragraph(f"{i}. {r}", body_style))
        story.append(Spacer(1, 0.1 * inch))

        # ── Documents Enclosed ──
        story.append(Paragraph("DOCUMENTS ENCLOSED", heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=silver))
        story.append(Spacer(1, 0.05 * inch))
        for i, d in enumerate(workflow["documents_needed"], 1):
            story.append(Paragraph(f"{i}. {d}", body_style))

        story.append(Spacer(1, 0.3 * inch))

        # ── Signature ──
        story.append(Paragraph(f"Date: {today}", body_style))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("______________________________", body_style))
        story.append(Paragraph("Signature of Plaintiff", body_style))
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
    except Exception:
        return generate_text_document(case_data, workflow, output_path.replace(".pdf", ".txt"))


# ─── Text Document ────────────────────────────────────────────────────────────

def generate_text_document(case_data: dict, workflow: dict, output_path: str) -> bool:
    """Fallback: generate a plain-text legal petition."""
    today     = datetime.date.today().strftime("%d %B %Y")
    court     = case_data.get("court", "Small Causes Court")
    city      = case_data.get("city", "Chennai")
    plaintiff = case_data.get("user_name", "[Plaintiff Name]")
    defendant = _resolve_defendant(case_data)
    defendant_address = _resolve_defendant_address(case_data)
    subject   = build_subject(case_data, workflow)

    lines = [
        "=" * 66,
        f"        IN THE {court.upper()}",
        f"                AT {city.upper()}",
        "=" * 66,
        "",
        "Plaintiff:",
        f"{plaintiff}",
        "",
        "Defendant:",
        f"{defendant}",
    ]
    if defendant_address:
        lines.append(f"Address: {defendant_address}")
    lines += [
        "",
        "Subject:",
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
        "Signature of Plaintiff",
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


# ─── TXT → PDF Converter ─────────────────────────────────────────────────────

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
        grey   = HexColor("#666666")
        silver = HexColor("#888888")

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

            if stripped and all(c in separator_chars for c in stripped):
                story.append(HRFlowable(width="100%", thickness=1.5 if "=" in stripped else 0.5, color=navy if "=" in stripped else silver))
                story.append(Spacer(1, 0.05 * inch))
                continue

            if not stripped:
                story.append(Spacer(1, 0.1 * inch))
                continue

            if stripped.startswith("IN THE ") or stripped.startswith("AT "):
                story.append(Paragraph(stripped, court_header))
                continue

            if stripped.isupper() and len(stripped) > 3 and not stripped.startswith("("):
                story.append(Paragraph(stripped, section_title))
                continue

            if ":" in stripped and stripped.split(":")[0].strip() in (
                "Plaintiff", "Defendant", "Subject", "Address", "Date"
            ):
                parts = stripped.split(":", 1)
                label = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                story.append(Paragraph(f"<b>{label}:</b>  {value}", label_style))
                continue

            if stripped.startswith("___"):
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph(stripped, body_style))
                continue

            if "DISCLAIMER" in stripped or "procedural guidance" in stripped:
                story.append(Paragraph(f"<i>{stripped}</i>", small_style))
                continue

            story.append(Paragraph(stripped, body_style))

        doc.build(story)
        return True

    except Exception as e:
        print(f"  Error converting to PDF: {e}")
        return False
