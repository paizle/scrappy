from bs4 import BeautifulSoup
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy
# import logging # Logger could be useful if available and configured
# logger = logging.getLogger(__name__)

class WikipediaGdpStrategy(PageScrapingStrategy):
    """
    Scraping strategy for extracting GDP data from a Wikipedia page.
    """

    def get_url(self) -> str:
        """
        Returns the URL path for the Wikipedia page listing countries by GDP (nominal).
        """
        return "/wiki/List_of_countries_by_GDP_(nominal)"

    def parse(self, html_content: str) -> list[dict]:
        """
        Parses the HTML content of the Wikipedia page to extract country names and GDP values.

        Args:
            html_content: The HTML content of the page.

        Returns:
            A list of dictionaries, where each dictionary represents a country and its GDP.
            Example: {'country': 'United States', 'gdp': '30,507,217'}
        """
        # Using 'lxml' as it was tested as an alternative to 'html.parser'.
        # The underlying 'NoneType object is not callable' error persisted with both.
        soup = BeautifulSoup(html_content, 'lxml')
        results = []

        # Find the main data table. Wikipedia tables often use 'wikitable sortable'.
        # The first such table is usually the main one for this page.
        table = soup.find('table', class_="wikitable sortable")

        if table is None:
            # Fallback: if the specific table isn't found, try any 'wikitable'.
            all_wikitables = soup.find_all('table', class_="wikitable")
            if all_wikitables:
                # logger.info(f"Found {len(all_wikitables)} wikitables, taking the first one.")
                table = all_wikitables[0]
            else:
                # logger.warning("No wikitable found on the page.")
                return []

        if table is None: # Should be redundant if above logic is correct, but as a safeguard.
            # logger.warning("Table object is None even after fallbacks.")
            return []

        rows = table.find_all('tr')

        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])

            if len(cells) < 2: # Ensure at least two cells for country and GDP
                continue

            if cells[0].name == 'th': # Skip header rows
                continue

            country_cell = cells[0]
            gdp_cell = cells[1]

            country_text = country_cell.get_text(strip=True)
            gdp_text = gdp_cell.get_text(strip=True)

            if not country_text or not gdp_text: # Skip if essential text is missing
                continue

            country = country_text.split('[')[0].strip()
            gdp = gdp_text.split('[')[0].strip()

            if not country or not gdp: # Skip if empty after stripping/splitting
                continue

            lowercase_country = country.lower()
            # Filter out common aggregate/header-like entries
            if lowercase_country in ['country', 'world', 'european union', 'euro zone'] or 'rank' in lowercase_country:
                continue

            # Basic check to see if GDP value looks plausible (e.g., starts with a digit)
            if not gdp or not gdp[0].isdigit():
                continue

            results.append({'country': country, 'gdp': gdp})

        return results
