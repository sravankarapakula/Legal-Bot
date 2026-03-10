#!/usr/bin/env python3
"""
Legal Aid Bot — Terminal Prototype
A citizen legal assistant that guides users through legal procedures,
generates documents, tracks cases, and sends deadline reminders.

Run with:  python main.py
"""

import os
import datetime

from utils.ui import C, bot, user_input, header, step_banner, info, success, warning, thinking
from core.classifier import classify_dispute, get_workflow
from core.document_generator import generate_text_document, txt_to_pdf
from core.tracker import OUTPUT_DIR, create_case, check_reminders, display_case_tracker


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
        "city":      "Chennai",
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
    print(f"  📁 Output files saved to: {OUTPUT_DIR}")
    print(f"  📄 Petition    : {output_filename}")
    if case_id:
        print(f"  📊 Case DB     : case_database.json")
    print(f"  {'─' * 66}{C.RESET}\n")

    return output_filename, case_id


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        result = run_bot()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Session ended by user.{C.RESET}\n")
