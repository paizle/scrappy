from bs4 import BeautifulSoup
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy

class TestBsStrategy(PageScrapingStrategy):
    """
    A simple strategy to test BeautifulSoup functionality by extracting
    the title and first H1 tag from a page.
    """

    def get_url(self) -> str:
        """
        Returns the URL path for the test. For example.com, the path is "/".
        """
        return "/"

    def parse(self, html_content: str) -> dict: # Changed from list[dict] to dict for single result
        """
        Parses the HTML content to extract the page title and the first H1 tag.

        Args:
            html_content: The HTML content of the page.

        Returns:
            A dictionary containing the title and h1 text.
            Example: {'title': 'Example Domain', 'h1': 'Example Domain'}
        """
        soup = BeautifulSoup(html_content, 'lxml') # Using lxml as it's installed

        title_text = 'No title'
        if soup.title and soup.title.string:
            title_text = soup.title.string.strip()

        h1_text = 'No h1'
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_text = h1_tag.text.strip()

        return {'title': title_text, 'h1': h1_text}
