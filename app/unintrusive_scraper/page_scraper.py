"""
Core module for web scraping functionalities.

This module defines the `PageScrapingStrategy` abstract base class for
site-specific scraping logic and the `UnintrusivePageScraper` class
for fetching and parsing web content respectfully, including features like
robots.txt adherence, caching, and request delays.
"""
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.robotparser
import logging
import os

logger = logging.getLogger(__name__)


class PageScrapingStrategy(ABC):
    """
    Abstract base class defining the contract for page scraping strategies.

    A page scraping strategy encapsulates the logic for obtaining the specific
    URL path for a website and parsing its content to extract relevant data.
    """

    @abstractmethod
    def get_url(self) -> str:
        """
        Return the specific URL path (e.g., "/path/to/page") to be appended to a base URL.
        """
        pass

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> dict | list | None:
        """
        Extract data from the provided BeautifulSoup object of a webpage.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML of the page.

        Returns:
            dict | list | None: A dictionary or list containing the extracted data.
                                The structure is defined by the implementing strategy.
                                Returns None if parsing fails critically.
        """
        pass


class UnintrusivePageScraper:
    """
    A web scraper designed to be respectful to web servers.

    It includes features such as:
    - Adherence to robots.txt rules.
    - Caching of responses to avoid redundant requests.
    - Configurable delays between requests.
    - Retries with exponential backoff for failed requests.
    - Customizable User-Agent string.
    """

    def __init__(
        self,
        base_url: str,
        cache_dir: str = "scraper_cache",
        default_delay: int = 1,
        max_retries: int = 3,
        retry_backoff_factor: int = 2,
    ):
        """
        Initializes the UnintrusivePageScraper.

        Args:
            base_url (str): The base URL of the website to scrape.
            cache_dir (str): Name of the directory to store cached responses.
                             This will be created in the directory of 'app'.
            default_delay (int): Initial delay in seconds between requests and before retries.
            max_retries (int): Maximum number of retries for failed requests.
            retry_backoff_factor (int): The base factor for exponential backoff calculation
                                        (e.g., delay * (factor**attempt)).
        """
        self.base_url = base_url.rstrip("/")
        self.user_agent = "MyWebScraper/1.0 (contact: example@email.com)"
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(f"{self.base_url}/robots.txt")
        try:
            self.robot_parser.read()
        except Exception as e:
            logger.warning(
                f"Could not read or parse robots.txt from {self.base_url}/robots.txt: {e}",
                exc_info=True,
            )

        self.delay = default_delay
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.cache_dir_name = cache_dir # Store the name, actual path resolved below

        # Determine the root of the application (assuming this file is in app/unintrusive_scraper)
        # to make cache_dir relative to the project's 'app' directory parent.
        # Project Root -> app -> scraper_cache (if cache_dir is "scraper_cache")
        # Project Root -> .cache (if cache_dir is ".cache" as in .env.example)
        # The task specified .env.example SCRAPER_CACHE_DIR=".cache" at project root.
        # So, we need to ensure the path is relative to the project root.
        # Assuming this script is at /app/app/unintrusive_scraper/page_scraper.py
        # Project root is three levels up from this script's dir.
        # Or, if run.py is at root, then os.getcwd() might be project root.
        # Let's assume the cache_dir from .env is relative to where run.py is executed (project root).
        # Thus, os.path.abspath(cache_dir) should work if execution is from project root.
        self.absolute_cache_dir = os.path.abspath(self.cache_dir_name)

        try:
            os.makedirs(self.absolute_cache_dir, exist_ok=True)
            logger.info(f"Cache directory set to: {self.absolute_cache_dir}")
        except OSError as e:
            logger.error(
                f"Could not create cache directory {self.absolute_cache_dir}: {e}",
                exc_info=True,
            )


    def can_fetch(self, url: str) -> bool:
        """
        Checks if the scraper is allowed to fetch a given URL according to robots.txt.

        Args:
            url (str): The full URL to check.

        Returns:
            bool: True if the URL is allowed to be fetched, False otherwise.
        """
        try:
            return self.robot_parser.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Error during robots.txt can_fetch check for {url}: {e}", exc_info=True)
            return False

    def get_page_content(self, url: str) -> str | None:
        """
        Fetches the content of a webpage, handling caching, robots.txt, retries, and delays.

        Args:
            url (str): The full URL of the page to fetch.

        Returns:
            str | None: The HTML content of the page as a string, or None if the
                        request fails after retries or is disallowed by robots.txt.
        """
        if not self.can_fetch(url):
            logger.warning(f"robots.txt disallows fetching: {url}")
            return None

        safe_filename = url.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "_") + ".html"
        # Ensure absolute_cache_dir is used for cache path
        cache_path = os.path.join(self.absolute_cache_dir, safe_filename)


        try:
            if os.path.exists(cache_path):
                logger.info(f"Using cached version for: {url}")
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read()
        except OSError as e:
            logger.warning(f"Error accessing cache file {cache_path}: {e}", exc_info=True)

        logger.info(f"Fetching URL: {url}")
        headers = {"User-Agent": self.user_agent}

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                try:
                    # Ensure directory exists before writing, in case it was deleted post-init
                    os.makedirs(self.absolute_cache_dir, exist_ok=True)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logger.info(f"Successfully fetched and cached: {url}")
                except OSError as e:
                    logger.warning(f"Error writing to cache file {cache_path}: {e}", exc_info=True)

                return response.text

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout while fetching {url} (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url} (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                logger.error(f"RequestException while fetching {url} (attempt {attempt + 1}/{self.max_retries}): {e}", exc_info=True)

            if attempt < self.max_retries - 1:
                # Use retry_backoff_factor in calculation
                current_delay = self.delay * (self.retry_backoff_factor**attempt) + random.uniform(0, 1)
                logger.info(f"Retrying in {current_delay:.2f} seconds...")
                time.sleep(current_delay)
            else:
                logger.error(f"Failed to fetch {url} after {self.max_retries} retries.")
                return None
        return None


    def parse_data(self, html_content: str, css_selector: str) -> list:
        """
        Parses the HTML content of a page using BeautifulSoup and extracts data
        based on a CSS selector. (Utility method, not used by main scrape flow)
        """
        if not html_content:
            return []
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            elements = soup.select(css_selector)
            data = [element.text.strip() for element in elements]
            return data
        except Exception as e:
            logger.error(f"Error parsing data with CSS selector '{css_selector}': {e}", exc_info=True)
            return []


    def scrape(self, strategy: PageScrapingStrategy) -> dict | list | None:
        """
        Perform the scraping operation using the provided strategy.
        """
        target_url_path = strategy.get_url()
        if not target_url_path:
            logger.error("Strategy returned an invalid URL path.")
            return None

        full_url = f"{self.base_url}{target_url_path}"
        html_content = self.get_page_content(full_url)

        if not html_content:
            logger.warning(f"No HTML content fetched for {full_url}, cannot parse.")
            return None

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return strategy.parse(soup)
        except Exception as e:
            logger.error(f"Unhandled exception during strategy parsing for {full_url}: {e}", exc_info=True)
            return None
