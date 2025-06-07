from app.unintrusive_scraper.scraper import UnintrusiveScraper
from app.scrape_strategies.example_strategy import ExampleComStrategy


scraper = UnintrusiveScraper('https://example.com')
strategy = ExampleComStrategy()
result = scraper.scrape(strategy)

print(result)
