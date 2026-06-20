import re
import sys

def parse_curl(curl_str):
    cookie     = ""
    csrf_token = ""
    gig_url    = ""
    gig_id     = ""

    # Extract cookie from -b
    cookie_match = re.search(r"-b '(.+?)'(?:\s+-H|\s*\\|\s*$)", curl_str, re.DOTALL)
    if cookie_match:
        cookie = cookie_match.group(1).strip()

    # Extract x-csrf-token
    csrf_match = re.search(r"-H 'x-csrf-token:\s*(.+?)'", curl_str)
    if csrf_match:
        csrf_token = csrf_match.group(1).strip()

    # Extract gig_id from the curl URL itself
    gig_id_match = re.search(r"/fetch_reviews/(\d+)", curl_str)
    if gig_id_match:
        gig_id = gig_id_match.group(1)

    # Extract the main curl URL (first quoted URL in the command)
    gig_url_match = re.search(r"curl '(https://www\.fiverr\.com/gig_page/api/fetch_reviews/\d+)", curl_str)
    if gig_url_match:
        gig_url = gig_url_match.group(1).strip()

    return cookie, csrf_token, gig_id, gig_url


def update_env(cookie, csrf_token, gig_id, gig_url):
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    env = {}
    for line in lines:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

    if cookie:     env["COOKIE"]     = cookie
    if csrf_token: env["CSRF_TOKEN"] = csrf_token
    if gig_id:     env["GIG_ID"]     = gig_id
    if gig_url:    env["GIG_URL"]    = gig_url

    with open(".env", "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")


if __name__ == "__main__":
    print("📋 Paste your cURL command below.")
    print("   DevTools → right-click request → Copy → Copy as cURL (bash)")
    print("   When done, type END on a new line and press Enter:\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    curl_str = "\n".join(lines)
    cookie, csrf_token, gig_id, gig_url = parse_curl(curl_str)

    if not cookie or not csrf_token:
        print("❌ Could not parse cookie or CSRF token.")
        sys.exit(1)

    update_env(cookie, csrf_token, gig_id, gig_url)

    print(f"\n✅ Cookie      : {len(cookie)} chars")
    print(f"✅ CSRF token  : {csrf_token[:40]}...")
    print(f"✅ Gig ID      : {gig_id}")
    print(f"✅ Gig URL     : {gig_url}")
    print(f"\n✅ .env updated! Now run: python scraper.py")