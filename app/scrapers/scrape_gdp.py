from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.wikipedia_gdp_strategy import WikipediaGdpStrategy

def main():
    """
    Main function to scrape GDP data from Wikipedia.
    Initializes the scraper, uses the WikipediaGdpStrategy, and prints the results.
    """
    # Initialize the UnintrusivePageScraper with the base URL for Wikipedia.
    scraper = UnintrusivePageScraper('https://en.wikipedia.org')

    # Initialize the WikipediaGdpStrategy.
    gdp_strategy = WikipediaGdpStrategy()

    # Scrape the data using the strategy.
    # The scrape method in UnintrusivePageScraper will call get_url() and parse()
    # from the gdp_strategy.
    gdp_data = scraper.scrape(gdp_strategy)

    # Process and print the scraped GDP data.
    if gdp_data:
        print("Successfully scraped GDP data:")
        for item in gdp_data:
            print(f"Country: {item.get('country')}, GDP: {item.get('gdp')}")
    else:
        print("No GDP data was scraped. The result was empty or an error occurred.")

if __name__ == '__main__':
    main()
