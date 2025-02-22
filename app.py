from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from flask_cors import CORS
import html

app = Flask(__name__)
CORS(app)

# Regular expression to extract URLs from messages
url_pattern = re.compile(r"https?://[\w\.-]+\.[a-z]{2,6}[\w\./?&=-]*")

# Integration JSON Data
integration_data = {
    "data": {
        "date": {
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d")
        },
        "descriptions": {
            "app_name": "Link Preview Generator",
            "app_description": "Extracts URLs from messages and generates previews with metadata.",
            "app_logo": "data:image/png;base64,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",
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
        "author": "Faith Kariuki",
        "settings": [
            {
                "label": "Enable Link Previews",
                "type": "boolean",
                "required": True,
                "default": True
            }
        ],
        "target_url": "https://telexpreview.onrender.com/webhook",
        "endpoints": [
            {
                "path": "/webhook",
                "method": "POST",
                "description": "Process messages and generate link previews"
            },
            {
                "path": "/preview",
                "method": "POST",
                "description": "Test endpoint for generating previews"
            },
            {
                "path": "/test",
                "method": "POST",
                "description": "Basic test endpoint"
            }
        ]
    }
}


def extract_urls(text):
    """Extract URLs from text content"""
    return url_pattern.findall(text)


def fetch_metadata(url):
    """Fetch metadata from the given URL using Open Graph tags."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = (
                soup.find("meta", property="og:title") or
                soup.find("title") or
                soup.find("meta", {"name": "title"})
        )

        description = (
                soup.find("meta", property="og:description") or
                soup.find("meta", {"name": "description"})
        )

        image = (
                soup.find("meta", property="og:image") or
                soup.find("meta", {"name": "image"})
        )

        metadata = {
            "title": title.get("content", title.text) if title else "No Title",
            "description": description["content"] if description and description.has_attr(
                "content") else "No Description",
            "image": image["content"] if image and image.has_attr("content") else None,
            "url": url
        }

        return metadata

    except requests.exceptions.RequestException as e:
        return {"error": str(e), "url": url}


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming messages from Telex channels"""
    try:
        data = request.json
        original_message = data.get("message", "")

        # Extract URLs from the message
        urls = extract_urls(original_message)

        if not urls:
            return jsonify({
                "status": "success",
                "message": original_message
            })

        # Generate preview for the first URL only to avoid duplicates
        metadata = fetch_metadata(urls[0])

        # Combine original message with preview card
        preview_html = f'{original_message}\n\n'  # Keep original message as-is

        # Add preview card below
        preview_html += '<div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0; max-width: 600px;">'

        # Title with link
        preview_html += f'<a href="{html.escape(metadata["url"])}" style="text-decoration: none; color: #1a0dab;">'
        preview_html += f'<h3 style="margin: 0 0 10px 0;">{html.escape(metadata["title"])}</h3></a>'

        # Description
        preview_html += f'<p style="color: #4d5156; margin: 0 0 15px 0;">{html.escape(metadata["description"])}</p>'

        # Image (if available)
        if metadata.get('image'):
            preview_html += f'<img src="{html.escape(metadata["image"])}" alt="Preview" style="max-width: 100%; height: auto; border-radius: 4px;">'

        preview_html += '</div>'

        return jsonify({
            "status": "success",
            "message": preview_html,
            "content_type": "text/html"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        }), 500


@app.route("/preview", methods=["POST"])
def preview():
    """Test endpoint for preview generation"""
    try:
        data = request.json
        message = data.get("message", "")
        urls = extract_urls(message)

        if not urls:
            return jsonify({
                "message": message,
                "previews": []
            })

        previews = [fetch_metadata(url) for url in urls]

        return jsonify({
            "message": message,
            "previews": previews
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/test", methods=["POST"])
def test():
    """Basic test endpoint"""
    data = request.json
    return jsonify({
        "status": "success",
        "message": f"{data}"
    })


@app.route("/integration.json", methods=["GET"])
def get_integration():
    """Returns the integration JSON"""
    return jsonify(integration_data)


if __name__ == "__main__":
    app.run(port=5000)