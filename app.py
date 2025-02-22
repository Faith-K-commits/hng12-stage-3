from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from flask_cors import CORS

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
            "app_logo": "https://www.google.com/url?sa=i&url=https%3A%2F%2Ficonscout.com%2Ffree-icon%2Flink-preview-2653354",
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
                "type": "text",
                "required": True,
                "default": "Yes"
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

        # Try Open Graph tags first, then fall back to regular meta tags
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

        # Generate preview for the first URL only
        metadata = fetch_metadata(urls[0])

        # Markdown approach (if Telex supports Markdown)
        preview_text = f"**{metadata['title']}**\n"
        preview_text += f"{metadata['description']}\n\n"
        preview_text += f"![Preview Image]({metadata['image']})\n\n"
        preview_text += f"[Visit Website]({metadata['url']})"

        # HTML approach (if Telex supports HTML)
        preview_html = f"""
        <strong>{metadata['title']}</strong><br>
        {metadata['description']}<br><br>
        <img src="{metadata['image']}" alt="Preview Image" style="max-width: 100%;"><br>
        <a href="{metadata['url']}">Visit Website</a>
        """

        # Choose format based on what Telex supports
        response_message = preview_text  # Change to `preview_html` if Telex supports HTML

        return jsonify({
            "status": "success",
            "message": response_message
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