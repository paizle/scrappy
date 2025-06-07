from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.robotparser
import urllib.parse # Added for urljoin
import logging
import os

# Configure logging (important for debugging and monitoring)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScrapingStrategy(ABC):
    @abstractmethod
    def get_url(self) -> str:
        """Return the URL to scrape."""
        pass

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> dict:
        """Extract data from the page and return it as a dictionary."""
        pass

class UnintrusiveScraper:
    def __init__(self, base_url):
        """
        Initializes the scraper with a base URL and a User-Agent.

        Args:
            base_url (str): The base URL of the website to scrape.
        """
        self.base_url = base_url
        self.user_agent = "MyWebScraper/1.0 (contact: example@email.com)"
        self.robot_parser = urllib.robotparser.RobotFileParser()
        robots_url = urllib.parse.urljoin(self.base_url, "robots.txt")
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()  # Download and parse robots.txt
        except Exception as e:
            logging.warning(f"Could not read robots.txt from {robots_url}: {e}")
        self.delay = 1  # Initial delay between requests (seconds)
        self.max_retries = 3  # Maximum number of retries for failed requests
        self.cache_dir = "scraper_cache"  # Directory to store cached responses
        os.makedirs(self.cache_dir, exist_ok=True)


    def can_fetch(self, url):
        """
        Checks if the scraper is allowed to fetch a given URL according to robots.txt.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is allowed, False otherwise.
        """
        return self.robot_parser.can_fetch(self.user_agent, url)

    def get_page_content(self, url):
        """
        Fetches the content of a webpage, handling retries, delays, and User-Agent.
        Uses caching to avoid unnecessary requests.

        Args:
            url (str): The URL of the page to fetch.

        Returns:
            str: The HTML content of the page, or None if the request fails after retries.
        """

        # Check robots.txt with the full URL
        if not self.can_fetch(url):
            logging.warning(f"robots.txt disallows fetching: {url}") # Corrected log message
            return None

        safe_filename = url.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_') + ".html"
        cache_path = os.path.join(self.cache_dir, safe_filename)

        if os.path.exists(cache_path):
            logging.info(f"Using cached version: {url}") # Kept original log for this line
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

        headers = {'User-Agent': self.user_agent}

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10) # Added timeout
                response.raise_for_status()

                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logging.info(f"Cached new content for: {url}")
                return response.text

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {url} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay_seconds = self.delay * (2 ** attempt)
                    logging.info(f"Retrying in {delay_seconds} seconds...")
                    time.sleep(delay_seconds + random.uniform(0, 0.5))
                else:
                    logging.error(f"Failed to fetch {url} after {self.max_retries} retries.")
                    return None
            finally:
                if attempt < self.max_retries -1 :
                     time.sleep(self.delay + random.uniform(0, 0.5))


    def parse_data(self, html_content, css_selector):
        """
        Parses the HTML content of a page using BeautifulSoup and extracts data based on a CSS selector.

        Args:
            html_content (str): The HTML content of the page.
            css_selector (str): A CSS selector to identify the data to extract.

        Returns:
            list: A list of extracted text values.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.select(css_selector)
        data = [element.text.strip() for element in elements]
        return data

    def scrape(self, strategy: ScrapingStrategy) -> dict:
        """Perform the scraping using the given strategy."""

        strategy_url_path = strategy.get_url()
        full_url = urllib.parse.urljoin(self.base_url, strategy_url_path)
        logging.info(f"Attempting to scrape URL: {full_url}")
        html_content = self.get_page_content(full_url)

        if not html_content:
            logging.warning(f"No HTML content received from {full_url}. Cannot parse.")
            return {}

        soup = BeautifulSoup(html_content, 'html.parser')
        return strategy.parse(soup)

    def scrape_old(self, url, css_selector):
        """
        Combines fetching and parsing to scrape data from a URL.

        Args:
            url (str): The URL to scrape.
            css_selector (str): The CSS selector to extract data.

        Returns:
            list: A list of extracted data values.
        """
        html_content = self.get_page_content(url)
        if html_content:
            return self.parse_data(html_content, css_selector)
        else:
            return []
