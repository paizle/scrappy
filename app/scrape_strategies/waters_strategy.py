"""
Defines the scraping strategy for extracting data about New Brunswick water bodies
from a specific Wikipedia page.
"""
import logging # Added logging
from bs4 import BeautifulSoup, Tag
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy

logger = logging.getLogger(__name__)


class WatersStrategy(PageScrapingStrategy):
    """
    A scraping strategy for extracting a list of water bodies in New Brunswick
    from the Wikipedia page "List_of_bodies_of_water_of_New_Brunswick".
    """

    def get_url(self) -> str:
        """
        Returns the specific Wikipedia path for the list of New Brunswick water bodies.

        Returns:
            str: The URL path component for the target Wikipedia page.
        """
        return "/wiki/List_of_bodies_of_water_of_New_Brunswick"

    def parse(self, soup: BeautifulSoup) -> list[dict[str, str]] | None:
        """
        Parses the HTML content of the Wikipedia page to extract water body data.

        It targets a specific table with class "wikitable" and extracts details
        for each water body listed. Problematic rows are skipped and logged.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the parsed
                                  HTML of the Wikipedia page.

        Returns:
            list[dict[str, str]] | None: A list of dictionaries, where each dictionary
                                  represents a water body and contains keys such as
                                  "name", "type_1", "type_2", "parent",
                                  "start_county", and "end_county".
                                  Returns None if the main table is not found.
                                  Returns an empty list if table is found but no rows
                                  could be parsed.
        """
        data = []
        try:
            table = soup.find("table", {"class": "wikitable"})

            if not table or not isinstance(table, Tag): # Ensure table is a Tag object
                logger.error("Could not find the 'wikitable' on the page or it's not a Tag.")
                return None # Critical failure if table not found

            rows = table.find_all("tr")
        except AttributeError as e:
            logger.error(f"Error finding table or rows in HTML structure: {e}", exc_info=True)
            return None # Critical failure

        # Iterate through rows, skipping the header row (index 0 which typically uses <th>)
        for i, row in enumerate(rows[1:], start=1): # start=1 for accurate row number in logs
            try:
                if not isinstance(row, Tag): # Ensure row is a Tag object
                    logger.warning(f"Skipping row {i+1} as it's not a valid HTML tag: {row}")
                    continue

                cols = row.find_all("td")  # Get all data cells in the current row

                # Ensure the row has the expected number of columns before attempting to access them
                if len(cols) == 6:
                    # Extract text, ensuring cols[j] is a Tag and has get_text method
                    name = cols[0].get_text(strip=True) if isinstance(cols[0], Tag) else ""
                    type1 = cols[1].get_text(strip=True) if isinstance(cols[1], Tag) else ""
                    type2 = cols[2].get_text(strip=True) if isinstance(cols[2], Tag) else ""
                    tributary_of = cols[3].get_text(strip=True) if isinstance(cols[3], Tag) else ""
                    start_county = cols[4].get_text(strip=True) if isinstance(cols[4], Tag) else ""
                    end_county = cols[5].get_text(strip=True) if isinstance(cols[5], Tag) else ""

                    data.append(
                        {
                            "name": name,
                            "type_1": type1,  # Primary classification (e.g., Lake, River)
                            "type_2": type2,  # Secondary classification (e.g., Reservoir)
                            "parent": tributary_of,  # The body of water it flows into
                            "start_county": start_county,  # County where it originates or is primarily located
                            "end_county": end_county,  # County where it ends or also located
                        }
                    )
                else:
                    logger.warning(
                        f"Skipping row {i+1} due to unexpected number of columns: {len(cols)}. Content: {row.get_text(strip=True, separator=' | ')}"
                    )
            except (AttributeError, IndexError, TypeError) as e:
                # Log the error along with the row number and its content for debugging
                row_content = row.get_text(strip=True, separator=' | ') if isinstance(row, Tag) else "Non-Tag row"
                logger.error(
                    f"Error parsing row {i+1}. Content: '{row_content}'. Error: {e}",
                    exc_info=True, # Add exception info for traceback
                )
                # Skip this problematic row and continue with the next
                continue
            except Exception as e: # Catch any other unexpected errors for a row
                row_content = row.get_text(strip=True, separator=' | ') if isinstance(row, Tag) else "Non-Tag row"
                logger.error(
                    f"Unexpected error parsing row {i+1}. Content: '{row_content}'. Error: {e}",
                    exc_info=True,
                )
                continue


        return data
