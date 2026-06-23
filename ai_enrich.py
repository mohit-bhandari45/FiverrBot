import os
import json
import requests
from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def detect_website_from_image(image_url: str):

    default_response = {
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

    if not image_url:
        return default_response

    try:

        print(f"\n🔍 Analyzing: {image_url}")

        img_response = requests.get(
            image_url,
            timeout=30
        )

        img_response.raise_for_status()

        image_bytes = img_response.content

        content_type = img_response.headers.get(
            "content-type",
            "image/png"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                """
You are an elite OSINT analyst, website investigator, and screenshot identification expert.

Your objective is to identify the exact website shown in a screenshot using OCR, visual analysis, entity resolution, and web verification.

You MUST prioritize accuracy over completeness.

━━━━━━━━━━━━━━━━━━━━━━
MISSION
━━━━━━━━━━━━━━━━━━━━━━

Given a screenshot:

1. Extract all visible information.
2. Identify organizations, brands, logos, and products.
3. Search for real-world matches.
4. Verify candidate websites.
5. Return only evidence-backed conclusions.

Never guess domains.

━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — OCR EXTRACTION
━━━━━━━━━━━━━━━━━━━━━━

Extract every visible text element.

Include:

- Titles
- Headers
- Subtitles
- Navigation items
- Buttons
- Links
- Form labels
- Placeholders
- IDs
- Usernames
- Error messages
- Footer text
- Watermarks

Preserve exact spelling.

Store as:

visible_text (pipe-separated string)

━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — VISUAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━

Identify:

- Logos
- Crests
- School emblems
- Company marks
- Product branding
- Favicons
- UI style
- Color schemes
- Layout patterns

Store as:

visual_clues (pipe-separated string)

Example: "green shield crest | school alumni portal layout | membership login form"

━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — ENTITY EXTRACTION
━━━━━━━━━━━━━━━━━━━━━━

Extract possible entities.

Examples:

- Company
- School
- Alumni association
- Government agency
- SaaS product
- Startup
- Community

Store:

entities (pipe-separated string)

━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — WEBSITE CLASSIFICATION
━━━━━━━━━━━━━━━━━━━━━━

Determine:

- Alumni Portal
- Membership Portal
- Dashboard
- SaaS
- LMS
- CRM
- Ecommerce
- Government Portal
- Banking Portal
- Landing Page
- Internal Tool

Store:

website_type

━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — WEB RESEARCH
━━━━━━━━━━━━━━━━━━━━━━

Search using:

- Exact titles
- Exact subtitles
- Organization names
- Slogans
- IDs
- Unique wording

Search examples:

"Amanfoɔ '97 Senior Portal"

"Private access for Verified Amanfoɔ '97 Seniors"

Search for:

- Official websites
- Alumni networks
- Membership systems
- Login portals
- Organization websites

━━━━━━━━━━━━━━━━━━━━━━
STEP 6 — CANDIDATE DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━

Build candidate list ONLY from:

- Search results
- Verified websites
- Official organization domains

NEVER create domains from names.

FORBIDDEN:

"Amanfoo" -> amanfoo.com

"Acme School" -> acmeschool.org

"XYZ Portal" -> xyzportal.com

These are hallucinations.

Every candidate URL must originate from:

- Search results
- Official directories
- Verified references

━━━━━━━━━━━━━━━━━━━━━━
STEP 7 — MATCH SCORING
━━━━━━━━━━━━━━━━━━━━━━

For every candidate score:

Text Match (0-30)

- Title match
- Subtitle match
- Organization match

Visual Match (0-30)

- Logo similarity
- Crest similarity
- Colors
- Layout

Organization Match (0-20)

- Same institution
- Same community
- Same alumni group

Portal Match (0-20)

- Same portal purpose
- Same login flow

Total Score:

0-100

━━━━━━━━━━━━━━━━━━━━━━
STEP 8 — URL VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━

A URL may be marked VERIFIED only if:

- Official website found
AND
- Organization matches
AND
- Screenshot evidence supports it

Confidence:

HIGH

- Exact organization match
- Exact branding match
- Strong supporting evidence

MEDIUM

- Organization verified
- Branding partially matches

LOW

- Only weak evidence exists

━━━━━━━━━━━━━━━━━━━━━━
CRITICAL ANTI-HALLUCINATION RULES
━━━━━━━━━━━━━━━━━━━━━━

Never invent URLs.

Never generate domains from names.

Never fabricate subdomains.

If URL cannot be verified:

website_url = ""

If evidence is weak:

confidence = "low"

If no verified URL exists:

likely_urls = []

Do not fill fields with guesses.

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON.

{
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
"reasoning": ""
}

FINAL RULE:

If you cannot prove a URL exists,
leave website_url empty.

Evidence beats guessing.
""",
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=content_type
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=2500,
            ),
        )

        result = response.text.strip()

        print("\n====================")
        print("RAW RESPONSE:")
        print(result)
        print("====================\n")

        # Gemini frequently wraps JSON in markdown
        if result.startswith("```json"):
            result = result.replace("```json", "")
            result = result.replace("```", "")
            result = result.strip()

        elif result.startswith("```"):
            result = result.replace("```", "")
            result = result.strip()

        try:
            data = json.loads(result)
        except Exception as parse_error:

            print(f"⚠️ JSON parse failed: {parse_error}")
            start = result.find("{")
            end = result.rfind("}")

            if start == -1 or end == -1:
                print("❌ Could not find JSON object")
                return default_response

            try:
                fixed_json = result[start:end + 1]
                data = json.loads(fixed_json)
            except Exception as second_error:

                print(f"❌ Recovery parse failed: {second_error}")
                return default_response

        print("\n========== PARSED DATA ==========")
        print(json.dumps(data, indent=2))
        print("==================================\n")

        for key in default_response:
            if key not in data:
                data[key] = default_response[key]

        if isinstance(data.get("visible_text"), list):
            data["visible_text"] = " | ".join(
                map(str, data["visible_text"])
            )

        if isinstance(data.get("visual_clues"), list):
            data["visual_clues"] = " | ".join(
                map(str, data["visual_clues"])
            )

        if isinstance(data.get("entities"), list):
            data["entities"] = " | ".join(
                map(str, data["entities"])
            )

        return data

    except Exception as e:

        print(f"⚠️ AI detection failed for {image_url}")
        print(e)

        return default_response