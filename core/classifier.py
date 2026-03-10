"""
Classifier — Dispute classification and workflow lookup.
"""

from data.constants import DISPUTE_KEYWORDS, WORKFLOWS


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
    # No match found — return a safe generic fallback
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
