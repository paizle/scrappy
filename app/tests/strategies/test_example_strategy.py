import unittest
from bs4 import BeautifulSoup
from app.scrape_strategies.example_strategy import ExampleComStrategy
import logging

# Suppress logging within tests for cleaner output, unless specifically testing log messages
logging.disable(logging.CRITICAL)

class TestExampleComStrategy(unittest.TestCase):
    def setUp(self):
        """Set up an instance of ExampleComStrategy for each test."""
        self.strategy = ExampleComStrategy()

    def test_get_url(self):
        """Test that get_url() returns the correct path."""
        self.assertEqual(self.strategy.get_url(), "/")

    def test_parse_successful(self):
        """Test parsing with typical example.com HTML."""
        html_content = """
        <!doctype html>
        <html>
        <head>
            <title>Example Domain</title>
            <meta charset="utf-8" />
            <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
        </head>
        <body>
        <div>
            <h1>Example Domain</h1>
            <p>This domain is for use in illustrative examples in documents. You may use this
            domain in literature without prior coordination or asking for permission.</p>
            <p><a href="https://www.iana.org/domains/example">More information...</a></p>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        expected_data = {"title": "Example Domain", "heading": "Example Domain"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_no_title_text(self):
        """Test parsing when the title tag is empty."""
        html_content = "<html><head><title></title></head><body><h1>Heading</h1></body></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        # The strategy returns "No title found" if title.string is empty
        expected_data = {"title": "No title found", "heading": "Heading"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_no_title_tag(self):
        """Test parsing when the title tag is missing entirely."""
        html_content = "<html><head></head><body><h1>Heading</h1></body></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        # The strategy returns "No title found" if soup.title is None
        expected_data = {"title": "No title found", "heading": "Heading"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_no_h1(self):
        """Test parsing when the H1 tag is missing."""
        html_content = "<html><head><title>A Title</title></head><body><p>Some text.</p></body></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        # The strategy returns "No heading found"
        expected_data = {"title": "A Title", "heading": "No heading found"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_empty_html(self):
        """Test parsing with completely empty HTML."""
        html_content = ""
        soup = BeautifulSoup(html_content, "html.parser")
        # The strategy returns defaults for both when elements are missing
        expected_data = {"title": "No title found", "heading": "No heading found"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_only_html_tags(self):
        """Test parsing with just <html> tags."""
        html_content = "<html></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        expected_data = {"title": "No title found", "heading": "No heading found"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_html_with_only_head(self):
        """Test parsing HTML with only a head tag (no body)."""
        html_content = "<html><head><title>Only Head Title</title></head></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        expected_data = {"title": "Only Head Title", "heading": "No heading found"}
        self.assertEqual(self.strategy.parse(soup), expected_data)

if __name__ == "__main__":
    unittest.main()
