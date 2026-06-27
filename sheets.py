import os
import gspread
from gspread.exceptions import WorksheetNotFound

def extract_sheet_rows(reviews):
    """Extract username, work_sample, order_duration, value, price_range_start from reviews."""
    rows = []
    for review in reviews:
        work_sample = review.get("work_sample") or review.get("work_sample_preview_url")
        if not work_sample:
            continue

        rows.append([
            review.get("username", ""),
            work_sample,
            review.get("order_duration", ""),
            review.get("value", ""),
            review.get("price_range_start", ""),
        ])

    return rows

def export_to_google_sheet(rows, gig_id):
    """Export extracted rows to Google Sheet."""
    if not rows:
        print("⚠️ No rows to export.")
        return False

    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    worksheet_name = f"Gig_Reviews_{gig_id}"

    if not sheet_id:
        print("⚠️ GOOGLE_SHEET_ID is not set.")
        return False

    if not service_account_file:
        print("⚠️ GOOGLE_SERVICE_ACCOUNT_FILE is not set.")
        return False

    headers = ["username", "work_sample", "order_duration", "rating", "price_range_start"]
    values = [headers] + rows

    try:
        client = gspread.service_account(filename=service_account_file)
        spreadsheet = client.open_by_key(sheet_id)

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=str(max(len(values) + 10, 100)),
                cols=str(len(headers)),
            )

        worksheet.clear()
        worksheet.update("A1", values)

        print(f"✅ Exported {len(rows)} rows to Google Sheet: {worksheet_name}")
        return True
    except Exception as e:
        print(f"❌ Error exporting to Google Sheet: {e}")
        return False