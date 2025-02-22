from flask import Flask, request, jsonify
import requests, json
from bs4 import BeautifulSoup
import re

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Regular expression to extract URLs from messages
url_pattern = re.compile(r"https?://[\w\.-]+\.[a-z]{2,6}[\w\./?&=-]*")

# Integration JSON Data
integration_data = {
    "data": {
        "date": {
            "created_at": "2025-02-22",
            "updated_at": "2025-02-22"
        },
        "descriptions": {
            "app_name": "Link Preview Generator",
            "app_description": "Extracts URLs from messages and generates previews with metadata.",
            "app_logo": "https://www.google.com/url?sa=i&url=https%3A%2F%2Ficonscout.com%2Ffree-icon%2Flink-preview-2653354&psig=AOvVaw2SsFncePz3eCGroM2Meb8g&ust=1740311277460000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCNiRle6a14sDFQAAAAAdAAAAABAE",
            "app_url": "https://telexpreview.onrender.com",
            "background_color": "#ffffff"
        },
        "is_active": True,
        "integration_type": "modifier",
        "integration_category": "Communication & Collaboration",
        "key_features": [
            "Automatically detects URLs in messages",
            "Fetches and displays metadata (title, description, and thumbnail)"
        ],
        "author": "Faith",
        "settings": [
            {
                "label": "Enable Link Previews",
                "type": "boolean",
                "required": True,
                "default": True
            }
        ],
        "target_url": "https://telexpreview.onrender.com/preview",
        "tick_url": "nil"
    }
}

def extract_urls(text):
    return url_pattern.findall(text)


def fetch_metadata(url):
    """Fetch metadata from the given URL using Open Graph tags."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("meta", property="og:title") or soup.find("title")
        description = soup.find("meta", property="og:description")
        image = soup.find("meta", property="og:image")

        return {
            "title": title["content"] if title and title.has_attr("content") else "No Title",
            "description": description["content"] if description and description.has_attr(
                "content") else "No Description",
            "image": image["content"] if image and image.has_attr("content") else None,
            "url": url
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "url": url}


@app.route("/preview", methods=["POST"])
def preview():
    data = request.json
    message = data.get("message", "")
    urls = extract_urls(message)

    if not urls:
        return jsonify({"message": message, "previews": []})

    previews = [fetch_metadata(url) for url in urls]

    return jsonify({"message": message, "previews": previews})

@app.route("/integration.json", methods=["GET"])
def get_integration():
    """Returns the integration JSON"""
    return jsonify(integration_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
