from bs4 import BeautifulSoup
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy

class ExampleComStrategy(PageScrapingStrategy):
  def get_url(self) -> str:
    return "/"

  def parse(self, soup: BeautifulSoup) -> dict:
    title = soup.title.string.strip() if soup.title else "No title"
    heading = soup.find("h1").text.strip() if soup.find("h1") else "No heading"

    return {
        "title": title,
        "heading": heading
    }