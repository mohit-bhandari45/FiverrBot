import requests
import json
import time
import re
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# LOAD FROM .env
# ─────────────────────────────────────────────
COOKIE     = os.getenv("COOKIE", "")
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")
GIG_URL    = os.getenv("GIG_URL", "")
GIG_ID     = os.getenv("GIG_ID", "")

if not COOKIE or not CSRF_TOKEN:
    print("❌ Session missing. Run: python session.py first")
    sys.exit(1)

HEADERS = {
    "accept":           "application/json",
    "user-agent":       "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "x-csrf-token":     CSRF_TOKEN,
    "referer":          "https://www.fiverr.com",
    "sec-fetch-mode":   "cors",
    "sec-fetch-site":   "same-origin",
    "cookie":           COOKIE,
}

# ─────────────────────────────────────────────
# EXTRACT GIG ID FROM URL
# ─────────────────────────────────────────────
def extract_gig_id(url):
    match = re.search(r"/fetch_reviews/(\d+)", url)
    if match:
        return match.group(1)
    match = re.match(r"https://www\.fiverr\.com/([^/?]+)/([^/?]+)", url)
    if match:
        return match.group(2)
    return None

# ─────────────────────────────────────────────
# FETCH ALL REVIEWS
# ─────────────────────────────────────────────
def fetch_all_reviews(gig_id):
    all_reviews         = []
    page                = 1
    last_star_rating_id = None
    last_review_id      = None
    last_score          = None

    print(f"\n🚀 Fetching reviews for: {gig_id}\n")

    while True:
        params = {
            "gig_id":    gig_id,
            "sort_by":   "relevant",
            "page_size": 5,
        }
        if last_review_id:
            params["last_star_rating_id"] = last_star_rating_id
            params["last_review_id"]      = last_review_id
            params["last_score"]          = last_score

        url = f"https://www.fiverr.com/gig_page/api/fetch_reviews/{gig_id}"
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            print(f"❌ Error on page {page}: HTTP {res.status_code}")
            print(res.text[:200])
            break

        data    = res.json()
        reviews = data.get("reviews", [])

        if not reviews:
            print("✅ No more reviews.")
            break

        print(f"   Page {page}: {len(reviews)} reviews | Total: {len(all_reviews) + len(reviews)}")
        all_reviews.extend(reviews)

        last                = reviews[-1]
        last_star_rating_id = last["id"]
        last_review_id      = last["id"]
        last_score          = last["score"]

        if not data.get("has_next"):
            print("✅ No more pages.")
            break

        page += 1
        time.sleep(1.5)

    return all_reviews

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Priority: GIG_ID from .env > GIG_URL from .env > ask user
    if GIG_ID:
        gig_id = GIG_ID
        print(f"📌 Using Gig ID from .env: {gig_id}")
    elif GIG_URL:
        gig_id = extract_gig_id(GIG_URL)
        print(f"📌 Using URL from .env: {GIG_URL}")
    else:
        url    = input("Enter Fiverr gig URL: ").strip()
        gig_id = extract_gig_id(url)

    if not gig_id:
        print("❌ Could not determine gig ID")
        sys.exit(1)

    reviews  = fetch_all_reviews(gig_id)
    out_file = f"reviews_{gig_id}.json"

    with open(out_file, "w") as f:
        json.dump(reviews, f, indent=2)

    print(f"\n📊 Total reviews : {len(reviews)}")
    print(f"💾 Saved to      : {out_file}")