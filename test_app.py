import unittest
from flask import json
from app import app, extract_urls, fetch_metadata

class TestFlaskIntegration(unittest.TestCase):

    def setUp(self):
        """Set up test client for Flask app"""
        self.app = app.test_client()
        self.app.testing = True

    def test_extract_urls(self):
        """Test URL extraction from text"""
        text = "Check this out: https://example.com and https://another-site.com"
        extracted_urls = extract_urls(text)
        expected_urls = ["https://example.com", "https://another-site.com"]
        self.assertEqual(extracted_urls, expected_urls)

    def test_fetch_metadata(self):
        """Test metadata fetching from a URL"""
        url = "https://www.example.com"
        metadata = fetch_metadata(url)

        # We can't predict real metadata, so check if keys exist
        self.assertIn("title", metadata)
        self.assertIn("description", metadata)
        self.assertIn("image", metadata)
        self.assertIn("url", metadata)

    def test_preview_no_url(self):
        """Test /preview endpoint with no URLs"""
        response = self.app.post("/preview", json={"message": "Hello, world!"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Hello, world!")
        self.assertEqual(data["previews"], [])

    def test_preview_with_url(self):
        """Test /preview endpoint with a valid URL"""
        response = self.app.post("/preview", json={"message": "Check this: https://example.com"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Check this: https://example.com")
        self.assertGreater(len(data["previews"]), 0)  # At least one preview

    def test_integration_json(self):
        """Test /integration.json endpoint"""
        response = self.app.get("/integration.json")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["descriptions"]["app_name"], "Link Preview Generator")

if __name__ == "__main__":
    unittest.main()
