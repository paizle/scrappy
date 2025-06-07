from bs4 import BeautifulSoup
from app.unintrusive_scraper.scraper import ScrapingStrategy
import logging # Added import

class WatersStrategy(ScrapingStrategy):
  def get_url(self) -> str:
    return "/wiki/List_of_bodies_of_water_of_New_Brunswick"

  def parse(self, soup: BeautifulSoup) -> list: # Changed return type hint
    data = [] # Initialize data here
    try:
        table = soup.find("table", {"class": "wikitable"})
        if not table:
            logging.warning("Could not find the wikitable in waters_strategy.")
            return []

        rows = table.find_all("tr")
        if not rows or len(rows) < 2: # Check if rows exist and there's at least one data row
            logging.warning("No data rows found in the wikitable in waters_strategy.")
            return []

        for row in rows[1:]: # Skip header (already handled by rows[1:])
            try:
                cols = row.find_all(["td"])
                if len(cols) < 6: # Ensure enough columns
                    logging.warning(f"Skipping row with insufficient columns: {row.get_text(strip=True)}")
                    continue

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
            except Exception as e_row:
                logging.warning(f"Error parsing a specific row in waters_strategy: {row.get_text(strip=True)}. Exception: {e_row}")
                continue # Skip to next row

    except Exception as e_table:
        logging.error(f"Major error parsing the table structure in waters_strategy: {e_table}")
        return [] # Return empty list on major table parsing error

    return data
