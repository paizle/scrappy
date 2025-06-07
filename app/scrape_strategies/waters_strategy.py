from bs4 import BeautifulSoup
from app.unintrusive_scraper.scraper import ScrapingStrategy

class WatersStrategy(ScrapingStrategy):
  def get_url(self) -> str:
    return "/wiki/List_of_bodies_of_water_of_New_Brunswick"

  def parse(self, soup: BeautifulSoup) -> dict:
    table = soup.find("table", {"class": "wikitable"})
    rows = table.find_all("tr")

    data = []
    # header row has <th>, skip it
    for row in rows[1:]:
        cols = row.find_all(["td"])
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