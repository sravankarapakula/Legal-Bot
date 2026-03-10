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


def create_case(case_data: dict, workflow: dict, court: str,
                deadline_date: str, deadline_label: str,
                hearing_date: str) -> str:
    """Create a new case entry in the MySQL cases table."""
    case_id = _next_case_id()
    filing_date = datetime.date.today()
    phone = case_data.get("phone", "N/A")
    category = workflow.get("title", "General")
    pdf_path = case_data.get("pdf_path", "")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cases (case_id, phone_number, category, court,
                               filing_date, hearing_date, pdf_path, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Filed')
            """,
            (case_id, phone, category, court,
             filing_date, hearing_date or None, pdf_path, ),
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    return case_id


def check_reminders():
    """Return list of (case_dict, days_left) for cases with deadline ≤ 7 days away."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT case_id, phone_number, category, court,
                   filing_date, hearing_date, pdf_path, status
            FROM cases
            WHERE hearing_date IS NOT NULL
              AND DATEDIFF(hearing_date, CURDATE()) <= 7
              AND hearing_date >= CURDATE()
            """
        )
        rows = cur.fetchall()
        cur.close()

        reminders = []
        today = datetime.date.today()
        for row in rows:
            case = {
                "case_id": row[0],
                "phone": row[1],
                "category": row[2],
                "court": row[3],
                "filing_date": str(row[4]),
                "hearing_date": str(row[5]),
                "pdf_path": row[6],
                "status": row[7],
                "deadline_label": "Hearing",
            }
            days_left = (row[5] - today).days
            reminders.append((case, days_left))
        return reminders
    finally:
        conn.close()


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
        else:
            print(f"  {C.RED}Case {case_id} not found.{C.RESET}")
    finally:
        conn.close()
