"""
This module provides an example or template for creating new scraping strategies.
A scraping strategy defines how to:
1. Specify the exact URL path to be scraped (relative to a base URL defined in the main scraper script).
2. Parse the HTML content of that page to extract the desired data.

To create a new strategy:
1. Copy this file (e.g., to `my_new_strategy.py`).
2. Rename the class `ExampleComStrategy` to something descriptive for your target
   (e.g., `MyWebsiteArticleStrategy`).
3. Implement the `get_url` method to return the specific path of the page you want to scrape.
   This path is usually relative to the base URL passed to the `UnintrusivePageScraper`.
4. Implement the `parse` method to extract the specific data you need from the page's HTML structure.
   This typically involves using BeautifulSoup methods to find tags, attributes, and text.
"""
from bs4 import BeautifulSoup
# Ensure you import PageScrapingStrategy from the correct scraper file,
# especially if you are using a commented version like page_scraper_2.py
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy # Or page_scraper_2.py

class ExampleComStrategy(PageScrapingStrategy):
  """
  An example strategy for scraping basic information (title and h1 heading)
  from a generic webpage, illustrated with example.com.
  This class can be copied and adapted for new scraping tasks.
  """
  def get_url(self) -> str:
    """
    Returns the path for the target page on the website.
    For example.com, the main page is at the root path "/".
    For other sites, this might be "/articles/my-article" or similar.
    """
    return "/"

  def parse(self, soup: BeautifulSoup) -> dict:
    """
    Parses the HTML soup of the target page to extract desired information.
    This example extracts the page title and the text of the first H1 heading.

    Args:
      soup: A BeautifulSoup object representing the parsed HTML of the page.

    Returns:
      A dictionary containing the extracted data. In this example, it includes
      'title' and 'heading'. The structure of this dictionary will vary
      depending on the data being scraped.
      Returns "No title" or "No heading" as fallbacks if elements are not found.
    """
    # Extract the page title from the <title> tag.
    # .string gets the inner text of the tag. .strip() removes leading/trailing whitespace.
    # A conditional expression handles cases where the <title> tag might be missing.
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"

    # Find the first <h1> tag and extract its text content.
    # .text gets all child text concatenated. .strip() removes whitespace.
    # A conditional expression handles cases where no <h1> tag is found.
    heading_tag = soup.find("h1")
    heading = heading_tag.text.strip() if heading_tag else "No heading found"

    return {
        "title": title,
        "heading": heading
    }
