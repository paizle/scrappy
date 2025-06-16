from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.robotparser
import logging
import os

# Configure logging (important for debugging and monitoring)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PageScrapingStrategy(ABC):
    """
    Abstract base class defining the interface for a page scraping strategy.
    A strategy encapsulates the logic for how to get a URL and parse content
    from a specific type of page. This promotes a clear separation of concerns,
    allowing the main scraper to be agnostic of the specific details of
    individual websites or page structures.
    """
    @abstractmethod
    def get_url(self) -> str:
        """
        Return the specific URL path (relative to a base URL) or full URL to scrape.
        This method must be implemented by concrete strategies to target specific pages.

        Returns:
            str: The URL to be scraped by the strategy.
        """
        pass

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> dict:
        """
        Extracts data from the parsed HTML (BeautifulSoup object) of a page.
        This method must be implemented by concrete strategies to handle the
        specific structure of the page being scraped.

        Args:
            soup (BeautifulSoup): A BeautifulSoup object representing the HTML
                                  content of the page.

        Returns:
            dict: A dictionary containing the extracted data. The structure of
                  this dictionary is defined by the implementing strategy.
        """
        pass

class UnintrusivePageScraper:
    """
    A web scraper designed to be respectful to web servers.
    Key features:
    - Adheres to robots.txt rules to ensure allowed scraping paths.
    - Implements caching to avoid redundant requests for the same content.
    - Uses a clear User-Agent string to identify the scraper.
    - Introduces delays between requests and uses exponential backoff for retries
      to avoid overloading servers.
    """
    def __init__(self, base_url, cache_dir='scraper_cache'):
        """
        Initializes the UnintrusivePageScraper.

        Args:
            base_url (str): The base URL of the website to scrape (e.g., "https://en.wikipedia.org").
                            This is used for resolving relative URLs from strategies and for robots.txt.
            cache_dir (str): The directory name to store cached HTML pages.
                             This directory will be created relative to the project's root if it doesn't exist.
                             The path to this directory is stored in `self.abs_cache_dir`.
        """
        self.base_url = base_url
        # Sets a descriptive User-Agent to identify the scraper and provide contact information.
        self.user_agent = "MyWebScraper/1.0 (contact: example@email.com)"
        self.robot_parser = urllib.robotparser.RobotFileParser()
        # Constructs the full URL for robots.txt and attempts to read it.
        self.robot_parser.set_url(f"{base_url}/robots.txt")
        try:
            self.robot_parser.read()  # Download and parse robots.txt
            logging.info(f"Successfully read robots.txt for {base_url}")
        except Exception as e:
            logging.warning(f"Could not read robots.txt for {base_url}: {e}")
        # Initial delay (in seconds) between requests. This helps prevent overwhelming the server.
        self.delay = 1
        # Maximum number of times to retry a failed HTTP request.
        self.max_retries = 3
        # Name of the directory to store cached files.
        self.cache_dir = cache_dir
        # Determine the parent directory of the 'app' folder (project root)
        # and create the absolute path to the cache directory.
        # __file__ refers to page_scraper.py (or page_scraper_2.py in this case)
        # os.path.dirname(__file__) is unintrusive_scraper/
        # os.path.dirname(os.path.dirname(__file__)) is app/
        # os.path.dirname(os.path.dirname(os.path.dirname(__file__))) is the project root
        PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.abs_cache_dir = os.path.join(PARENT_DIR, self.cache_dir)
        # Create the cache directory if it doesn't already exist.
        os.makedirs(self.abs_cache_dir, exist_ok=True)
        logging.info(f"Cache directory set to: {self.abs_cache_dir}")


    def can_fetch(self, url):
        """
        Checks if the scraper is allowed to fetch a given URL according to the parsed robots.txt file.
        This is a crucial part of respectful scraping.

        Args:
            url (str): The absolute URL to check.

        Returns:
            bool: True if fetching the URL is allowed by robots.txt, False otherwise.
        """
        allowed = self.robot_parser.can_fetch(self.user_agent, url)
        if not allowed:
            logging.info(f"robots.txt disallows fetching for URL: {url} with User-Agent: {self.user_agent}")
        return allowed

    def get_page_content(self, url):
        """
        Fetches the HTML content of a webpage, implementing unintrusive scraping practices.

        Practices include:
        1. robots.txt check: Verifies if scraping the URL is permitted before any request.
        2. Caching: Returns cached content if available to avoid redundant server requests.
           Cache files are named based on a sanitized version of the URL.
        3. User-Agent: Sends a defined User-Agent header with the HTTP request.
        4. Delays & Retries: Implements delays between requests and retries with exponential backoff
           in case of network issues or server errors to avoid aggressive scraping.

        Args:
            url (str): The absolute URL of the page to fetch.

        Returns:
            str: The HTML content of the page as a string. Returns None if the request
                 fails after all retries, if disallowed by robots.txt, or if any other
                 critical error occurs during fetching.
        """

        # 1. Check robots.txt before making any request.
        if not self.can_fetch(url):
            # Log already happens in can_fetch
            return None

        # 2. Check Cache:
        # Create a safe filename from the URL for caching (replace common URL characters).
        cache_filename = url.replace('/', '_').replace(':', '_').replace('?', '_').replace('=', '_').replace('&', '_') + ".html"
        cache_path = os.path.join(self.abs_cache_dir, cache_filename)

        if os.path.exists(cache_path):
            logging.info(f"Cache hit: Using cached version for URL: {url} from path: {cache_path}")
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Error reading from cache file {cache_path}: {e}")
                # Proceed to fetch from network if cache read fails

        logging.info(f"Cache miss: Fetching URL from network: {url}")
        # 3. Prepare headers for the HTTP request.
        headers = {'User-Agent': self.user_agent}

        # 4. Attempt to fetch the page with retries and delays.
        for attempt in range(self.max_retries):
            try:
                # Introduce a delay before making the actual request.
                # This base delay is applied to be polite, even if not a retry.
                # Add a small jitter to the delay.
                time.sleep(self.delay + random.uniform(0, 0.5))

                logging.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{self.max_retries})")
                response = requests.get(url, headers=headers, timeout=10) # Timeout for the request
                response.raise_for_status() # Raise HTTPError for bad responses (4XX or 5XX)

                # Save to cache before returning
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logging.info(f"Successfully fetched and cached: {url} at {cache_path}")
                return response.text

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {url} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff: delay increases with each retry.
                    # Also adds a small random jitter.
                    current_retry_delay = self.delay * (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"Retrying in {current_retry_delay:.2f} seconds...")
                    time.sleep(current_retry_delay)
                else:
                    logging.error(f"Failed to fetch {url} after {self.max_retries} retries.")
                    return None

    def scrape(self, strategy: PageScrapingStrategy) -> list[dict]:
        """
        Performs the scraping operation for a single page using a given strategy.

        It constructs the full URL using the scraper's base_url and the strategy's get_url() method.
        Then, it fetches the page content using `get_page_content` (which includes caching and
        unintrusive measures) and uses the strategy's `parse()` method to extract data.

        Args:
            strategy: An instance of PageScrapingStrategy that defines which URL
                      to scrape (relative to base_url) and how to parse its content.

        Returns:
            A list of dictionaries containing the scraped data, as returned by the
            strategy's parse method. Returns an empty list if fetching or parsing fails,
            or if the URL is disallowed by robots.txt.
        """
        # Construct the full URL to scrape.
        # Assumes strategy.get_url() returns a relative path.
        relative_url = strategy.get_url()
        if not relative_url.startswith('/'):
            # Ensure leading slash if strategy URL is just a path segment
            relative_url = '/' + relative_url
        target_url = self.base_url + relative_url # Example: "https://en.wikipedia.org" + "/wiki/Some_Page"

        logging.info(f"Attempting to scrape URL: {target_url} using strategy: {strategy.__class__.__name__}")

        html_content = self.get_page_content(target_url)

        if not html_content:
            logging.warning(f"No HTML content received for {target_url}. Scraping aborted for this URL.")
            return [] # Return empty list if page content couldn't be fetched

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Delegate parsing to the provided strategy.
            data = strategy.parse(soup)
            logging.info(f"Successfully parsed data from {target_url} using {strategy.__class__.__name__}.")
            return data
        except Exception as e:
            logging.error(f"Error parsing content from {target_url} with strategy {strategy.__class__.__name__}: {e}")
            return [] # Return empty list in case of parsing error
