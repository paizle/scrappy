"""
Defines an example scraping strategy, typically for a simple site like "example.com".
This serves as a basic illustration of how to implement a PageScrapingStrategy.
"""
import logging # Added logging
from bs4 import BeautifulSoup, Tag
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy

logger = logging.getLogger(__name__)


class ExampleComStrategy(PageScrapingStrategy):
    """
    An example scraping strategy for extracting basic information (title and
    main heading) from a webpage. It's designed to work with simple pages,
    such as "http://example.com".
    """

    def get_url(self) -> str:
        """
        Returns the root path ("/"), suitable for a base domain like "example.com".

        Returns:
            str: The URL path component, which is "/" for the root page.
        """
        return "/"

    def parse(self, soup: BeautifulSoup) -> dict[str, str] | None:
        """
        Parses the HTML content to extract the page title and the text of the
        first H1 heading.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the parsed
                                  HTML of the page.

        Returns:
            dict[str, str] | None: A dictionary containing:
                                - "title": The text of the <title> tag.
                                - "heading": The text of the first <h1> tag.
                                Returns None if a critical parsing error occurs.
                                Returns dictionary with "not found" values for missing elements.
        """
        try:
            title_tag = soup.title
            title = title_tag.string.strip() if title_tag and title_tag.string else "No title found"

            heading_tag = soup.find("h1")
            heading = heading_tag.text.strip() if heading_tag and isinstance(heading_tag, Tag) else "No heading found"

            return {"title": title, "heading": heading}

        except AttributeError as e:
            logger.error(f"Error parsing example page (likely missing expected elements): {e}", exc_info=True)
            # Return default values if there's an attribute error (e.g. soup.title is None)
            return {"title": "Error: No title found", "heading": "Error: No heading found"}
        except Exception as e:
            logger.error(f"Unexpected error parsing example page: {e}", exc_info=True)
            # For any other unexpected error, returning None might be safer
            return None
