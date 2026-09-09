import re
from datetime import datetime
from pathlib import Path

import win32com.client as win32
from openpyxl import Workbook

TARGET_FOLDER = Path(
    r"C:\Users\shreya.lingam\Mediolanum International Funds\Multi Management - Travel&Conference"
)
OUTPUT_FILE = TARGET_FOLDER / "MM_events_mailbox.xlsx"
MAILBOX_NAME = "MM_events"


def normalize_text(value):
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\xa0", " ")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("\r", "")
    return " ".join(text.split()).strip()


def find_mm_events_inbox(namespace):
    for account_folder in namespace.Folders:
        if MAILBOX_NAME.lower() in (account_folder.Name or "").lower():
            try:
                return account_folder.Folders["Inbox"]
            except Exception:
                pass

        try:
            for child in account_folder.Folders:
                if MAILBOX_NAME.lower() in (child.Name or "").lower():
                    try:
                        return child.Folders["Inbox"]
                    except Exception:
                        pass
        except Exception:
            pass

    raise RuntimeError("MM_events mailbox Inbox not found in the loaded Outlook profile.")


def extract_time(text):
    if not text:
        return ""

    patterns = [
        r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
        r"\b\d{1,2}\s*(?:am|pm)\b",
        r"\b\d{1,2}:\d{2}\s*(?:-|–|to)\s*\d{1,2}:\d{2}\s*(?:am|pm)?\b",
        r"\b\d{1,2}\s*(?:am|pm)\s*(?:-|–|to)\s*\d{1,2}\s*(?:am|pm)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(0)
    return ""


def extract_dates(subject, body=""):
    combined = " ".join(part for part in [normalize_text(subject), normalize_text(body)] if part)
    if not combined:
        return ""

    # Remove Outlook metadata lines like From/Sent/To/Received so we do not accidentally
    # treat message delivery timestamps as event dates.
    cleaned = re.sub(r"(?im)^(?:from|sent|to|cc|subject|received|date received|sent on|received on)\s*[:\-].*$", " ", combined)
    cleaned = re.sub(r"(?im)^\s*---.*$", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return ""

    month_names = "January|February|March|April|May|June|July|August|September|October|November|December"

    patterns = [
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s*(?:-|–|to)\s*\d{{1,2}}(?:st|nd|rd|th)?\s*(?:of\s+)?({month_names})\s*(?:\d{{4}})?\b",
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s*(?:of\s+)?({month_names})\s*(?:\d{{4}})?\b",
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s*(?:-|/)\s*\d{{1,2}}(?:st|nd|rd|th)?\s*(?:-|/)\s*\d{{4}}\b",
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s*(?:of\s+)?({month_names})\b",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, cleaned, flags=re.I):
            date_text = match.group(0)
            left = cleaned[max(0, match.start() - 80): match.start()]
            right = cleaned[match.end(): match.end() + 80]
            context = (left + " " + right).lower()

            if re.search(r"\b(?:sent|received|mail|email|message)\b", context):
                continue

            time_text = extract_time(cleaned)
            if time_text and time_text not in date_text:
                return f"{date_text}, {time_text}"
            return date_text

    fallback = re.search(r"(?:date|dates|date/time|datetime)\s*[:\-]?\s*([A-Za-z0-9, -]+\d{4})", cleaned, flags=re.I)
    if fallback:
        date_text = fallback.group(1).strip()
        context = cleaned.lower()
        if re.search(r"\b(?:sent|received|mail|email|message)\b", context):
            return ""
        time_text = extract_time(cleaned)
        if time_text and time_text not in date_text:
            return f"{date_text}, {time_text}"
        return date_text

    # Never infer a date from the email received timestamp. If no real event date exists, leave blank.
    return ""


def extract_event_rows():
    outlook = win32.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = find_mm_events_inbox(namespace)

    rows = []
    for item in inbox.Items:
        if getattr(item, "Class", None) != 43:
            continue

        sender = normalize_text(getattr(item, "SenderName", ""))
        subject = normalize_text(getattr(item, "Subject", ""))
        body = normalize_text(getattr(item, "Body", ""))

        if not sender and not subject:
            continue

        rows.append(
            {
                "Sender": sender,
                "Subject": subject,
                "Dates": extract_dates(subject, body),
            }
        )

    return rows


def write_excel(rows):
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Conferences"
    ws.append(["Sender", "Subject", "Dates"])

    for row in rows:
        ws.append([
            row["Sender"],
            row["Subject"],
            row["Dates"],
        ])

    ws.freeze_panes = "A2"
    for col in ["A", "B", "C"]:
        ws.column_dimensions[col].width = 24
    ws.auto_filter.ref = ws.dimensions

    wb.save(OUTPUT_FILE)
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows written: {len(rows)}")


if __name__ == "__main__":
    rows = extract_event_rows()
    write_excel(rows)
