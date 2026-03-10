"""
Case Tracker — JSON database, case creation, reminders, display.
"""

import os
import json
import datetime

from utils.ui import C, header


# ─── Paths ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Legal-Bot", "outputs")
# Fallback: use the directory of this file's parent
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_THIS_DIR)
OUTPUT_DIR = os.path.join(_PROJECT_DIR, "outputs")
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


def create_case(case_data: dict, workflow: dict, court: str,
                deadline_date: str, deadline_label: str,
                hearing_date: str) -> str:
    """Create a new case entry with user-provided court dates."""
    db = load_db()
    case_id = f"SC-{1000 + len(db['cases']) + 1}"
    filing_date = datetime.date.today()

    entry = {
        "case_id":       case_id,
        "phone":         case_data.get("phone", "N/A"),
        "user_name":     case_data.get("user_name", "Unknown"),
        "case_type":     workflow["title"],
        "court":         court,
        "filing_date":   str(filing_date),
        "next_deadline": deadline_date,
        "deadline_label": deadline_label,
        "hearing_date":  hearing_date,
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
