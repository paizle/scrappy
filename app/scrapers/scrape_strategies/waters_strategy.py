from bs4 import BeautifulSoup
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy

class WatersStrategy(PageScrapingStrategy):
  """
  Implements a PageScrapingStrategy for extracting information about bodies of water
  from a specific Wikipedia page.
  """
  def get_url(self) -> str:
    """
    Returns the URL path for the Wikipedia page listing bodies of water in New Brunswick.
    This path is relative to the base URL provided to the UnintrusivePageScraper.
    """
    return "/wiki/List_of_bodies_of_water_of_New_Brunswick"

  def parse(self, soup: BeautifulSoup) -> list[dict]:
    """
    Parses the HTML content of the Wikipedia page to extract water body data.

    Args:
      soup: A BeautifulSoup object representing the parsed HTML of the page.

    Returns:
      A list of dictionaries, where each dictionary represents a body of water
      and contains extracted information like name, type, and location.
    """
    # Find the main data table on the page.
    table = soup.find("table", {"class": "wikitable"})
    rows = table.find_all("tr")

    data = []
    # Iterate over table rows, skipping the header row (index 0).
    for row in rows[1:]:
        cols = row.find_all(["td"])
        # Extract text from each cell in the row.
        name = cols[0].get_text(strip=True)
        type1 = cols[1].get_text(strip=True)
        type2 = cols[2].get_text(strip=True)
        tributary_of = cols[3].get_text(strip=True)
        start_county = cols[4].get_text(strip=True)
        end_county = cols[5].get_text(strip=True)
        data.append({
            "name": name,
            "type_1": type1,
            "type_2": type2,
            "parent": tributary_of,
            "start_county": start_county,
            "end_county": end_county
        })

    return data