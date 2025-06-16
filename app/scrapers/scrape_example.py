from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.example_strategy import ExampleComStrategy

def main():
    scraper = UnintrusivePageScraper('https://example.com')
    strategy = ExampleComStrategy()
    result = scraper.scrape(strategy)
    print(result)

if __name__ == '__main__':
    main()