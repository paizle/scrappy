from bs4 import BeautifulSoup
from app.unintrusive_scraper.scraper import ScrapingStrategy

class ExampleComStrategy(ScrapingStrategy):
  def get_url(self) -> str:
    return "https://example.com"

  def parse(self, soup: BeautifulSoup) -> dict:
    title = soup.title.string.strip() if soup.title else "No title"
    heading = soup.find("h1").text.strip() if soup.find("h1") else "No heading"

    return {
        "title": title,
        "heading": heading
    }