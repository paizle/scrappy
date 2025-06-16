"""
This script serves as an example or template for creating new scraper modules.
It demonstrates how to:
1. Import the UnintrusivePageScraper (or its commented version).
2. Import a specific scraping strategy (e.g., ExampleComStrategy or its commented version).
3. Instantiate the scraper with a base URL.
4. Instantiate the strategy.
5. Call the scraper's scrape method with the strategy.
6. Process or print the results.

To create a new scraper, you can copy this file and modify it to use
your custom strategy and target URL. Remember to adjust imports if you
are using commented versions of scraper or strategy files (e.g., _2.py versions).
"""
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper # Or page_scraper_2.py if using that
from app.scrapers.scrape_strategies.example_strategy import ExampleComStrategy # Or example_strategy_2.py

def main():
    """
    Main function to demonstrate scraping example.com.
    Initializes the scraper and strategy, then scrapes and prints the result.
    This function can be adapted for new scrapers.
    """
    # Initialize the scraper with the base URL of the target website.
    # Ensure the correct scraper class is used if you have multiple versions.
    scraper = UnintrusivePageScraper('https://example.com')
    # Initialize the specific strategy for the target page.
    # Ensure the correct strategy class is used.
    strategy = ExampleComStrategy()
    # Perform the scrape operation using the selected strategy.
    result = scraper.scrape(strategy)
    # Print or otherwise process the extracted data.
    print(result)

if __name__ == '__main__':
    # This standard Python construct ensures main() is called only when
    # the script is executed directly (not when imported as a module).
    main()
