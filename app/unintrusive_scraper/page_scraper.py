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
    @abstractmethod
    def get_url(self) -> str:
        """Return the root URL to scrape."""
        pass

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> dict:
        """Extract data from the page and return it as a dictionary."""
        pass

class UnintrusivePageScraper:
    def __init__(self, base_url, cache_dir='scraper_cache'):
        """
        Initializes the scraper with a base URL and a User-Agent.

        Args:
            base_url (str): The base URL of the website to scrape.
            user_agent (str):  A custom User-Agent string.
        """
        self.base_url = base_url
        self.user_agent = "MyWebScraper/1.0 (contact: example@email.com)"
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(f"{base_url}/robots.txt")
        try:
            self.robot_parser.read()  # Download and parse robots.txt
        except Exception as e:
            logging.warning(f"Could not read robots.txt: {e}")
        self.delay = 1  # Initial delay between requests (seconds)
        self.max_retries = 3  # Maximum number of retries for failed requests
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)  # Create cache directory if it doesn't exist


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

        # Check robots.txt
        if not self.can_fetch(url):
            logging.warning(f" robots.txt disallows fetching: {url}")
            return None

        # Check Cache
        PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        CACHE_DIR = os.path.join(PARENT_DIR, self.cache_dir)

        cache_path = os.path.join(CACHE_DIR, url.replace('/', '_').replace(':', '_') + ".html")  # Create a safe filename
        if os.path.exists(cache_path):
            logging.info(f"Using cached version: {url}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

        headers = {'User-Agent': self.user_agent}

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers)
                # Save to cache before returning
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                return response.text

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {url} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.delay * (2 ** attempt)  # Exponential backoff
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay + random.uniform(0, 1)) # add a bit of randomness for politeness
                else:
                    logging.error(f"Failed to fetch {url} after {self.max_retries} retries.")
                    return None
            finally:
                time.sleep(self.delay + random.uniform(0, 1)) # Delay after each attempt

    
    def scrape(self, strategy: PageScrapingStrategy) -> dict:
        """Perform the scraping using the given strategy."""

        html_content = self.get_page_content(self.base_url + strategy.get_url())
        
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        return strategy.parse(soup)
    