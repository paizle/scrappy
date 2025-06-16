import unittest
import tempfile
import shutil
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.example_strategy import ExampleComStrategy

class TestScrapeExample(unittest.TestCase):
    
  def setUp(self):
    self.temp_dir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.temp_dir)

  def test_scrape_example_dot_com(self):
    url = "https://example.com"
    scraper = UnintrusivePageScraper(url, cache_dir=self.temp_dir)
    strategy = ExampleComStrategy()

    result = scraper.scrape(strategy)

    # Assert the expected values
    self.assertEqual(result["title"], "Example Domain")
    self.assertEqual(result["heading"], "Example Domain")

if __name__ == '__main__':
    unittest.main()
