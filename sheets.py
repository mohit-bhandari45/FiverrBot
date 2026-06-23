import os
import gspread
from gspread.exceptions import WorksheetNotFound

from ai_enrich import detect_website_from_image


def extract_sheet_rows(reviews):

    rows = []

    # REMOVE [:1] WHEN READY
    for review in reviews:

        image_url = (
            review.get("work_sample")
            or review.get("work_sample_preview_url")
            or ""
        )

        site_data = {
            "website_url": "",
            "likely_urls": [],
            "website_name": "",
            "organization": "",
            "website_type": "",
            "confidence": "",
            "description": "",
            "visible_text": "",
            "visual_clues": "",
            "entities": "",
            "reasoning": "",
        }

        if image_url:
            try:
                site_data = detect_website_from_image(
                    image_url
                )

                print("\n========== SITE DATA ==========")
                print(site_data)
                print("================================\n")

            except Exception as e:
                print(
                    f"⚠️ Website detection failed: {e}"
                )

        rows.append([
            review.get("username", ""),
            image_url,
            review.get("order_duration", ""),
            review.get("value", ""),
            review.get("price_range_start", ""),

            site_data.get("website_url", ""),

            ", ".join(
                site_data.get("likely_urls", [])
            ),

            site_data.get("website_name", ""),
            site_data.get("organization", ""),
            site_data.get("website_type", ""),
            site_data.get("confidence", ""),
            site_data.get("description", ""),
            site_data.get("visible_text", ""),
            site_data.get("visual_clues", ""),
            site_data.get("entities", ""),
            site_data.get("reasoning", ""),
        ])

    return rows


def export_to_google_sheet(rows):

    if not rows:
        print("⚠️ No rows to export.")
        return False

    sheet_id = os.getenv(
        "GOOGLE_SHEET_ID",
        ""
    )

    worksheet_name = os.getenv(
        "GOOGLE_WORKSHEET_NAME",
        "Reviews"
    )

    service_account_file = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        ""
    )

    if not sheet_id:
        print(
            "⚠️ GOOGLE_SHEET_ID is not set."
        )
        return False

    if not service_account_file:
        print(
            "⚠️ GOOGLE_SERVICE_ACCOUNT_FILE is not set."
        )
        return False

    headers = [
        "username",
        "work_sample",
        "order_duration",
        "rating",
        "price_range_start",

        "website_url",
        "likely_urls",

        "website_name",
        "organization",
        "website_type",
        "confidence",
        "description",
        "visible_text",
        "visual_clues",
        "entities",
        "reasoning",
    ]

    values = [headers] + rows

    try:

        client = gspread.service_account(
            filename=service_account_file
        )

        spreadsheet = client.open_by_key(
            sheet_id
        )

        try:

            worksheet = spreadsheet.worksheet(
                worksheet_name
            )

        except WorksheetNotFound:

            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=str(
                    max(
                        len(values) + 100,
                        1000
                    )
                ),
                cols=str(
                    len(headers)
                ),
            )

        worksheet.clear()

        worksheet.update(
            "A1",
            values
        )

        print(
            f"✅ Exported {len(rows)} rows to Google Sheet: {worksheet_name}"
        )

        return True

    except Exception as e:

        print(
            f"❌ Error exporting to Google Sheet: {e}"
        )

        return False