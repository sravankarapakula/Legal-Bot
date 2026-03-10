"""
Case Tracker — MySQL-backed case creation, reminders, display.
"""

import os
import datetime

from utils.ui import C, header
from database.db import get_connection


# ─── Paths ────────────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_THIS_DIR)
OUTPUT_DIR = os.path.join(_PROJECT_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─── Case CRUD ────────────────────────────────────────────────────────────────

def _next_case_id() -> str:
    """Generate a sequential case ID like SC-1001, SC-1002, ..."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cases")
        count = cur.fetchone()[0]
        cur.close()
        return f"SC-{1000 + count + 1}"
    finally:
        conn.close()


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
    """Display case information from the database."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT case_id, phone_number, category, court,
                   filing_date, hearing_date, pdf_path, status
            FROM cases WHERE case_id = %s
            """,
            (case_id,),
        )
        row = cur.fetchone()
        cur.close()

        if row:
            header(f"📋 CASE TRACKER — {case_id}")
            print(f"  {'Case ID':<22}: {C.BOLD}{row[0]}{C.RESET}")
            print(f"  {'Case Type':<22}: {row[2]}")
            print(f"  {'Court':<22}: {row[3]}")
            print(f"  {'Status':<22}: {C.GREEN}{row[7]}{C.RESET}")
            print(f"  {'Filing Date':<22}: {row[4]}")
            print(f"  {'Hearing Date':<22}: {C.YELLOW}{row[5]}{C.RESET}")
            print()
            return
    print(f"  {C.RED}Case {case_id} not found.{C.RESET}")


def get_case_tracker_text(case_id: str) -> str:
    """Return case tracker info as a plain-text string (for Telegram)."""
    db = load_db()
    for case in db["cases"]:
        if case["case_id"] == case_id:
            return (
                f"📋 CASE TRACKER — {case_id}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Case ID:       {case['case_id']}\n"
                f"📂 Case Type:     {case['case_type']}\n"
                f"🏛 Court:         {case['court']}\n"
                f"✅ Status:        {case['status']}\n"
                f"📅 Filing Date:   {case['filing_date']}\n"
                f"⏰ Next Deadline: {case['next_deadline']}  ({case['deadline_label']})\n"
                f"📆 Hearing Date:  {case['hearing_date']}"
            )
    return f"❌ Case {case_id} not found."
