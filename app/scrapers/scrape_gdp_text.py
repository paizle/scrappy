from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.wikipedia_gdp_text_strategy import WikipediaGdpTextStrategy
import json # For pretty printing the dictionary

def main():
    """
    Main function to scrape GDP data for the United States from Wikipedia
    using the WikipediaGdpTextStrategy.
    """
    scraper = UnintrusivePageScraper('https://en.wikipedia.org')
    gdp_text_strategy = WikipediaGdpTextStrategy()

    print(f"Attempting to scrape GDP for 'United States' using text strategy from {scraper.base_url + gdp_text_strategy.get_url()}")

    scraped_data = scraper.scrape(gdp_text_strategy)

    if scraped_data:
        print("Scraping result:")
        print(json.dumps(scraped_data, indent=2))
    else:
        # The UnintrusivePageScraper might return None if fetching content fails before parsing
        print("No data was returned from the scraper. This might indicate a fetch error or that the strategy returned None.")

if __name__ == '__main__':
    main()
