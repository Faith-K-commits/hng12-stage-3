from flask import Flask, request, jsonify
import requests, json
from bs4 import BeautifulSoup
import re

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Regular expression to extract URLs from messages
url_pattern = re.compile(r"https?://[\w\.-]+\.[a-z]{2,6}[\w\./?&=-]*")


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

@app.route("/integration", methods=["GET"])
def get_integration_data():
    with open("integration.json", "r") as file:
        data = json.load(file)
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
