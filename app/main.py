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
from app.scrapers import scrape_waters
scrape_waters.main()