"""
Example scraper script.

This script defines a function `run_example_scraper_logic` that demonstrates
how to use the UnintrusivePageScraper with the ExampleComStrategy to scrape
a simple webpage.
"""
import logging
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrape_strategies.example_strategy import ExampleComStrategy

logger = logging.getLogger(__name__)


def run_example_scraper_logic(
    base_url: str,
    cache_dir: str,
    default_delay: int,
    max_retries: int,
    retry_backoff_factor: int,
):
    """
    Runs the main logic for the example scraper.

    Args:
        base_url (str): The base URL for the example site (e.g., "https://example.com").
        cache_dir (str): Directory to use for caching scraped pages.
        default_delay (int): Default delay between scrape attempts.
        max_retries (int): Maximum number of retries for requests.
        retry_backoff_factor (int): Factor for exponential backoff on retries.
    """
    logger.info(
        f"Initializing UnintrusivePageScraper for example with base_url: {base_url}, "
        f"cache_dir: {cache_dir}, delay: {default_delay}, retries: {max_retries}, "
        f"backoff_factor: {retry_backoff_factor}"
    )
    # Note: ExampleComStrategy currently provides the full URL path ("/"),
    # so base_url here is mainly for consistency in UnintrusivePageScraper instantiation.
    scraper = UnintrusivePageScraper(
        base_url=base_url,
        cache_dir=cache_dir,
        default_delay=default_delay,
        max_retries=max_retries,
        retry_backoff_factor=retry_backoff_factor,
    )
    strategy = ExampleComStrategy()

    logger.info(f"Starting scrape for example site: {base_url}...")
    result = scraper.scrape(strategy)

    if result:
        logger.info(f"Example scraper result: {result}")
        # For demonstration, printing the result as this is an example script.
        print("Example Scraper Result:")
        print(result)
    else:
        logger.warning("Example scraper did not return any result.")

    return result

# If you wanted to make this script runnable by itself for testing:
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] - %(message)s")
#     # Example default values for direct execution
#     run_example_scraper_logic(
#         base_url="https://example.com", # This should match what ExampleComStrategy expects or uses
#         cache_dir="scraper_cache_test_example",
#         default_delay=1,
#         max_retries=1, # Example: less retries for the example
#         retry_backoff_factor=2
#     )
