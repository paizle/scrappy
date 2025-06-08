import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrape_strategies.example_strategy import ExampleComStrategy


scraper = UnintrusivePageScraper('https://example.com')
strategy = ExampleComStrategy()
result = scraper.scrape(strategy)

print(result)