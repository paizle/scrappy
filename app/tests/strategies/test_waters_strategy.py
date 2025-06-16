import unittest
from bs4 import BeautifulSoup
from app.scrape_strategies.waters_strategy import WatersStrategy
import logging

# Suppress logging within tests for cleaner output
logging.disable(logging.CRITICAL)

class TestWatersStrategy(unittest.TestCase):
    def setUp(self):
        """Set up an instance of WatersStrategy for each test."""
        self.strategy = WatersStrategy()

    def test_get_url(self):
        """Test that get_url() returns the correct Wikipedia path."""
        self.assertEqual(
            self.strategy.get_url(), "/wiki/List_of_bodies_of_water_of_New_Brunswick"
        )

    def test_parse_successful_rows(self):
        """Test parsing with a couple of valid rows in the Wikipedia table structure."""
        html_content = """
        <table class="wikitable">
          <tbody>
            <tr><th>Header1</th><th>Header2</th><th>Header3</th><th>Header4</th><th>Header5</th><th>Header6</th></tr>
            <tr>
              <td><a href="/wiki/Lake_1" title="Lake 1">Lake Alpha</a></td>
              <td>Lake</td>
              <td>Freshwater</td>
              <td>River Beta</td>
              <td>North County</td>
              <td>South County</td>
            </tr>
            <tr>
              <td>River Gamma</td>
              <td>River</td>
              <td>Tidal</td>
              <td>Bay Delta</td>
              <td>East County</td>
              <td>West County</td>
            </tr>
          </tbody>
        </table>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        expected_data = [
            {
                "name": "Lake Alpha",
                "type_1": "Lake",
                "type_2": "Freshwater",
                "parent": "River Beta",
                "start_county": "North County",
                "end_county": "South County",
            },
            {
                "name": "River Gamma",
                "type_1": "River",
                "type_2": "Tidal",
                "parent": "Bay Delta",
                "start_county": "East County",
                "end_county": "West County",
            },
        ]
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_table_not_found(self):
        """Test parsing when the 'wikitable' is missing."""
        html_content = "<div><p>No table here.</p></div>"
        soup = BeautifulSoup(html_content, "html.parser")
        # Expected to return None as per updated error handling in WatersStrategy
        self.assertIsNone(self.strategy.parse(soup))

    def test_parse_table_malformed_no_tbody_or_rows(self):
        """Test parsing a table that exists but has no tbody or tr."""
        html_content = '<table class="wikitable"></table>'
        soup = BeautifulSoup(html_content, "html.parser")
        # Expected to return an empty list as it finds the table but no rows to parse
        self.assertEqual(self.strategy.parse(soup), [])

    def test_parse_row_unexpected_column_count(self):
        """Test a row with fewer columns than expected; it should be skipped."""
        html_content = """
        <table class="wikitable">
          <tbody>
            <tr><th>H1</th><th>H2</th><th>H3</th><th>H4</th><th>H5</th><th>H6</th></tr>
            <tr><td>Valid Name</td><td>Lake</td><td>Type</td><td>Parent</td><td>Start</td><td>End</td></tr>
            <tr><td>Too few cols</td><td>River</td><td>Type</td><td>Parent</td><td>Start</td></tr> {/* Missing one col */}
            <tr><td>Another Valid</td><td>River</td><td>Type2</td><td>Parent2</td><td>Start2</td><td>End2</td></tr>
          </tbody>
        </table>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        parsed_data = self.strategy.parse(soup)
        self.assertIsNotNone(parsed_data) # Should not be None
        self.assertEqual(len(parsed_data), 2) # Only two valid rows should be parsed
        self.assertEqual(parsed_data[0]["name"], "Valid Name")
        self.assertEqual(parsed_data[1]["name"], "Another Valid")
        # The row "Too few cols" should have been skipped and logged by the strategy

    def test_parse_row_with_empty_cells(self):
        """Test a row where some cells might be empty but structure is valid."""
        html_content = """
        <table class="wikitable">
          <tbody>
            <tr><th>H1</th><th>H2</th><th>H3</th><th>H4</th><th>H5</th><th>H6</th></tr>
            <tr>
              <td>Lake Epsilon</td>
              <td>Lake</td>
              <td></td> {/* Empty type_2 */}
              <td>River Zeta</td>
              <td></td> {/* Empty start_county */}
              <td>Central County</td>
            </tr>
          </tbody>
        </table>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        expected_data = [
            {
                "name": "Lake Epsilon",
                "type_1": "Lake",
                "type_2": "", # Empty string as per get_text(strip=True)
                "parent": "River Zeta",
                "start_county": "", # Empty string
                "end_county": "Central County",
            }
        ]
        self.assertEqual(self.strategy.parse(soup), expected_data)

    def test_parse_row_with_non_tag_cols(self):
        """Test a row where some td elements might be missing or are NavigableStrings."""
        # This scenario is tricky; BeautifulSoup usually doesn't put bare strings directly in find_all('td') like this.
        # However, if a cell was malformed, e.g. `<td>Name</td> text_outside_td <td>Lake</td>...`
        # The strategy's `isinstance(cols[j], Tag)` should handle it.
        # For this test, let's simulate a row where find_all might return mixed content if not careful,
        # though the current strategy's `cols = row.find_all("td")` is robust.
        # The check `isinstance(cols[x], Tag)` is what we rely on.
        html_content = """
        <table class="wikitable">
          <tbody>
            <tr><th>H1</th><th>H2</th><th>H3</th><th>H4</th><th>H5</th><th>H6</th></tr>
            <tr>
              <td>Valid Lake</td><td>Lake</td><td>Type</td><td>Parent</td><td>Start</td><td>End</td>
            </tr>
            <tr>
              <td>Problem Lake</td>
              <!-- Imagine a cell that's not a proper Tag somehow, or missing -->
              <td>River</td><td>Type</td><td>Parent</td><td>Start</td>
              <!-- Missing last cell -->
            </tr>
          </tbody>
        </table>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        parsed_data = self.strategy.parse(soup)
        self.assertIsNotNone(parsed_data)
        self.assertEqual(len(parsed_data), 1) # "Problem Lake" row has 5 `td`s, so it's skipped.
        self.assertEqual(parsed_data[0]["name"], "Valid Lake")

    def test_parse_empty_table(self):
        """Test parsing an empty table (only headers)."""
        html_content = """
        <table class="wikitable">
          <tbody>
            <tr><th>Header1</th><th>Header2</th><th>Header3</th><th>Header4</th><th>Header5</th><th>Header6</th></tr>
          </tbody>
        </table>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        self.assertEqual(self.strategy.parse(soup), [])

if __name__ == "__main__":
    unittest.main()
