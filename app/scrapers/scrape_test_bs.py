from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.test_bs_strategy import TestBsStrategy
import json # For pretty printing the dictionary

def main():
    """
    Main function to test BeautifulSoup functionality using TestBsStrategy
    on https://example.com.
    """
    # Initialize the UnintrusivePageScraper with the base URL for example.com.
    # The TestBsStrategy.get_url() returns "/", so the target is https://example.com/
    scraper = UnintrusivePageScraper('https://example.com')

    # Initialize the TestBsStrategy.
    test_strategy = TestBsStrategy()

    # Scrape the data using the strategy.
    scraped_data = scraper.scrape(test_strategy)

    # Process and print the scraped data.
    if scraped_data:
        print("Successfully scraped data from example.com:")
        # Output the dictionary directly, perhaps pretty-printed
        print(json.dumps(scraped_data, indent=2))
    else:
        print("No data was scraped from example.com. The result was empty or an error occurred.")

if __name__ == '__main__':
    main()
