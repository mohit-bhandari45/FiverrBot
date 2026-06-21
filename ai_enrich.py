import os
import requests
import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def detect_website_from_image(image_url: str) -> str:
    """Download a work_sample image and ask an AI vision model what website it shows."""
    if not image_url:
        return ""

    try:
        img_response = requests.get(image_url, timeout=10)
        img_response.raise_for_status()
        b64_image = base64.b64encode(img_response.content).decode("utf-8")

        response = client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is a screenshot of a website. Identify the website's name or URL. "
                            "Reply with ONLY the URL or domain name, nothing else. "
                            "If you cannot determine it, reply with 'unknown'."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                    }
                ]
            }]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ AI detection failed for {image_url}: {e}")
        return ""