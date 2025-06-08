import pytest
from bs4 import BeautifulSoup

from app.scrape_strategies.example_strategy import ExampleComStrategy
from app.scrape_strategies.waters_strategy import WatersStrategy
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy # For type hinting if needed

# --- Tests for ExampleComStrategy ---

class TestExampleComStrategy:
    def test_get_url(self):
        strategy = ExampleComStrategy()
        assert strategy.get_url() == "/"

    def test_parse_example_com_html(self):
        strategy = ExampleComStrategy()
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
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = {
            "title": "Example Domain",
            "heading": "Example Domain"
        }
        assert strategy.parse(soup) == expected_data

    def test_parse_example_com_html_no_title(self):
        strategy = ExampleComStrategy()
        html_content = """
        <html><head></head>
        <body><h1>Example Domain</h1></body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = {
            "title": "No title", # Default value
            "heading": "Example Domain"
        }
        assert strategy.parse(soup) == expected_data

    def test_parse_example_com_html_no_heading(self):
        strategy = ExampleComStrategy()
        html_content = """
        <html><head><title>Example</title></head>
        <body><p>Some text</p></body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = {
            "title": "Example",
            "heading": "No heading" # Default value
        }
        assert strategy.parse(soup) == expected_data

    def test_parse_example_com_empty_html(self):
        strategy = ExampleComStrategy()
        html_content = ""
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = {
            "title": "No title",
            "heading": "No heading"
        }
        assert strategy.parse(soup) == expected_data


# --- Tests for WatersStrategy ---

class TestWatersStrategy:
    def test_get_url(self):
        strategy = WatersStrategy()
        assert strategy.get_url() == "/wiki/List_of_bodies_of_water_of_New_Brunswick"

    def test_parse_waters_html_basic_table(self):
        strategy = WatersStrategy()
        html_content = """
        <html><body>
        <table class="wikitable">
          <tbody>
            <tr>
              <th>Name</th><th>Type 1</th><th>Type 2</th><th>Tributary of</th><th>Start County</th><th>End County</th>
            </tr>
            <tr>
              <td><a href="/wiki/Lake_A">Lake A</a></td><td>Lake</td><td>Freshwater</td><td>River X</td><td>County 1</td><td>County 1</td>
            </tr>
            <tr>
              <td>River B</td><td>River</td><td></td><td>Lake Y</td><td>County 2</td><td>County 3</td>
            </tr>
          </tbody>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = [
            {
                "name": "Lake A", "type_1": "Lake", "type_2": "Freshwater",
                "parent": "River X", "start_county": "County 1", "end_county": "County 1"
            },
            {
                "name": "River B", "type_1": "River", "type_2": "",
                "parent": "Lake Y", "start_county": "County 2", "end_county": "County 3"
            }
        ]
        # Note: WatersStrategy.parse returns a list, which violates PageScrapingStrategy's type hint (dict)
        assert strategy.parse(soup) == expected_data

    def test_parse_waters_html_empty_table(self):
        strategy = WatersStrategy()
        html_content = """
        <html><body>
        <table class="wikitable">
          <tbody>
            <tr>
              <th>Name</th><th>Type 1</th><th>Type 2</th><th>Tributary of</th><th>Start County</th><th>End County</th>
            </tr>
          </tbody>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = []
        assert strategy.parse(soup) == expected_data

    def test_parse_waters_html_no_table(self):
        strategy = WatersStrategy()
        html_content = "<html><body><p>No table here</p></body></html>"
        soup = BeautifulSoup(html_content, 'html.parser')
        # The strategy's parse method will raise an AttributeError if the table is not found
        # table = soup.find("table", {"class": "wikitable"}) -> table will be None
        # rows = table.find_all("tr") -> AttributeError: 'NoneType' object has no attribute 'find_all'
        with pytest.raises(AttributeError):
            strategy.parse(soup)

    def test_parse_waters_html_table_missing_columns(self):
        strategy = WatersStrategy()
        # Table with fewer than expected columns in a row
        html_content = """
        <html><body>
        <table class="wikitable">
          <tbody>
            <tr><th>Name</th><th>Type 1</th></tr>
            <tr><td>Lake Z</td><td>Lake</td></tr>
          </tbody>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # cols = row.find_all(["td"]) -> will have 2 items
        # Accessing cols[2] onwards will raise IndexError
        with pytest.raises(IndexError):
            strategy.parse(soup)

    def test_parse_waters_html_no_tbody_in_table(self):
        # This case might be implicitly handled if find_all('tr') still works on table.
        # Let's assume a more direct path for rows if tbody is missing.
        # The current implementation is table.find_all("tr"), which should search all descendants.
        strategy = WatersStrategy()
        html_content = """
        <html><body>
        <table class="wikitable">
            <tr>
              <th>Name</th><th>Type 1</th><th>Type 2</th><th>Tributary of</th><th>Start County</th><th>End County</th>
            </tr>
            <tr>
              <td><a href="/wiki/Lake_A">Lake A</a></td><td>Lake</td><td>Freshwater</td><td>River X</td><td>County 1</td><td>County 1</td>
            </tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        expected_data = [
            {
                "name": "Lake A", "type_1": "Lake", "type_2": "Freshwater",
                "parent": "River X", "start_county": "County 1", "end_county": "County 1"
            }
        ]
        assert strategy.parse(soup) == expected_data
