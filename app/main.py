"""
This is the main entry point for the web scraping application.

This script is responsible for importing and running different scrapers.
To add a new scraper:
1. Define a new scraping strategy in `app/scrapers/scrape_strategies/`.
2. Create a new scraper module in `app/scrapers/` that utilizes this strategy.
3. Import and call the main function of your new scraper module below.
"""

#from app.scrapers import scrape_example
#scrape_example.main()
import sys

# from app.scrapers import scrape_waters # Commented out for now
# scrape_waters.main()
# from app.scrapers import scrape_gdp
# scrape_gdp.main()

def run_gdp_scraper():
    from app.scrapers import scrape_gdp
    print("Running GDP Scraper...")
    scrape_gdp.main()

def run_test_bs_scraper():
    from app.scrapers import scrape_test_bs
    print("Running BeautifulSoup Test Scraper...")
    scrape_test_bs.main()

def run_gdp_text_scraper():
    from app.scrapers import scrape_gdp_text
    print("Running GDP Text Scraper for United States...")
    scrape_gdp_text.main()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'test_bs':
            run_test_bs_scraper()
        elif command == 'gdp':
            run_gdp_scraper()
        elif command == 'gdp_text':
            run_gdp_text_scraper()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: 'gdp', 'test_bs', 'gdp_text'")
    else:
        # Default behavior if no argument is provided, e.g., run GDP scraper
        print("No command provided, defaulting to GDP scraper.")
        run_gdp_scraper()