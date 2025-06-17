import unittest
import re
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.wikipedia_gdp_text_strategy import WikipediaGdpTextStrategy

class TestScrapeWikipediaGdpText(unittest.TestCase):

    def test_scrape_gdp_text_strategy(self):
        # This test performs a live HTTP request and depends on the page structure.
        # For more robust CI/CD, consider using mock HTML content or a dedicated test server.
        print("\nRunning live test for WikipediaGdpTextStrategy...")
        print("This test will make a live HTTP request to Wikipedia.")

        scraper = UnintrusivePageScraper('https://en.wikipedia.org')
        strategy = WikipediaGdpTextStrategy()

        result = scraper.scrape(strategy)
        print(f"Scraping result: {result}")

        self.assertIsInstance(result, dict, "Scraper should return a dictionary.")

        self.assertIn("country", result, "Result should contain 'country' key.")
        self.assertIn("gdp", result, "Result should contain 'gdp' key.")

        # Check for presence of an error key and if it has a value
        error_message = result.get("error")
        if error_message: # If error key exists and is not empty or None
            # This allows the test to pass if the error is an expected one (e.g., "Could not find country marker")
            # but will provide information about the failure.
            # For a stricter test, one might fail immediately:
            # self.fail(f"Scraping error reported: {error_message} with debug info: {result.get('debug_info')}")
            print(f"Warning: Scraping strategy reported an error: '{error_message}'. Debug info: {result.get('debug_info')}")
            # Depending on what errors are acceptable, we might return or assert specific error conditions.
            # For this test, if an error is reported, we won't check country/GDP values further.
            # However, the strategy is currently expected to succeed for "United States".
            # So, an error here IS a failure of the current expectation.
            self.fail(f"Scraping error reported: {error_message}. Debug: {result.get('debug_info')}")


        self.assertEqual(result.get("country"), "United States", "Country should be 'United States'.")

        gdp_value = result.get("gdp")
        self.assertIsInstance(gdp_value, str, "GDP value should be a string.")
        self.assertTrue(len(gdp_value) > 0, "GDP value should not be empty if no error was reported.")

        # Check if GDP value consists of digits and commas only
        self.assertTrue(re.match(r"^[0-9,]+$", gdp_value), f"GDP value '{gdp_value}' should consist of digits and commas.")

        # Check if there's at least one comma, implying a number in thousands or more
        self.assertIn(",", gdp_value, "GDP value should contain a comma for large numbers.")

        # Check if there's at least one digit
        self.assertTrue(any(char.isdigit() for char in gdp_value), "GDP value must contain digits.")


if __name__ == '__main__':
    # This allows running the test directly via `python tests/test_scrape_wikipedia_gdp_text.py`
    unittest.main()
