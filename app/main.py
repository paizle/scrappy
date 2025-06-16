"""
Main entry point for the application.

This script provides a command-line interface to run different scraping tasks
based on the arguments provided. It loads configuration from a .env file,
and then can trigger a scraper for New Brunswick water bodies or an example scraper.
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Configure logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Import scraper functions after load_dotenv is potentially called
# This is a stylistic choice; they could be imported at the top.
# from app.scrapers.scrape_waters import run_waters_scraper_logic
# from app.examples.scrape_example import run_example_scraper_logic


def get_scraper_config() -> dict:
    """Loads scraper configurations from environment variables with defaults."""
    config = {
        "cache_dir": os.getenv("SCRAPER_CACHE_DIR", "scraper_cache"), # Default if not in .env
        "default_delay": int(os.getenv("SCRAPER_DEFAULT_DELAY", "1")),
        "max_retries": int(os.getenv("SCRAPER_MAX_RETRIES", "3")),
        "retry_backoff_factor": int(os.getenv("SCRAPER_RETRY_BACKOFF_FACTOR", "2")),
    }
    logger.debug(f"Loaded scraper config: {config}")
    return config

def run_waters_scraper_command():
    """Loads config and runs the New Brunswick waters scraper."""
    logger.info("Executing 'waters' command...")
    from app.scrapers.scrape_waters import run_waters_scraper_logic # Import here

    base_url = os.getenv("WATERS_BASE_URL", "https://en.wikipedia.org")
    scraper_config = get_scraper_config()

    logger.info(f"Target base URL for waters: {base_url}")
    run_waters_scraper_logic(
        base_url=base_url,
        cache_dir=scraper_config["cache_dir"],
        default_delay=scraper_config["default_delay"],
        max_retries=scraper_config["max_retries"],
        retry_backoff_factor=scraper_config["retry_backoff_factor"],
    )
    logger.info("New Brunswick waters scraper command finished.")


def run_example_scraper_command():
    """Loads config and runs the example scraper."""
    logger.info("Executing 'example' command...")
    from app.examples.scrape_example import run_example_scraper_logic # Import here

    base_url = os.getenv("EXAMPLE_BASE_URL", "https://example.com")
    scraper_config = get_scraper_config()

    logger.info(f"Target base URL for example: {base_url}")
    run_example_scraper_logic(
        base_url=base_url,
        cache_dir=scraper_config["cache_dir"],
        default_delay=scraper_config["default_delay"],
        max_retries=scraper_config["max_retries"],
        retry_backoff_factor=scraper_config["retry_backoff_factor"],
    )
    logger.info("Example scraper command finished.")


def print_usage():
    """Prints the usage message for the command-line interface."""
    print("Usage: python run.py [waters|example]")
    print("  waters   : Run the scraper for New Brunswick water bodies.")
    print("  example  : Run the example scraper.")


def main():
    """
    Parses command-line arguments and executes the corresponding scraper.
    Loads .env file for configurations.
    """
    # Load environment variables from .env file if it exists.
    # load_dotenv() should be called before accessing os.getenv() for .env variables.
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Assuming .env is in project root
    # If app/main.py is in /app/app/main.py, then os.path.dirname(__file__) is /app/app
    # Then '..' gives /app. If .env is in /app, this is correct.
    # If run.py is in /app and .env is in /app, then this path for .env is fine.
    # Let's assume .env is at the project root, and run.py is also at the project root.
    # If main.py is in app/ directory, then '..' is project root.
    # If main.py is in app/app directory, then '../..' is project root.
    # Given typical project structure where run.py is at root and imports app.main,
    # and .env is at root:
    # If main.py is /app/app/main.py, .env is at /app/.env
    # Then path should be os.path.join(os.path.dirname(__file__), '..', '.env')
    # If main.py is /app/main.py, .env is at /app/.env
    # Then path should be os.path.join(os.path.dirname(__file__), '.env')
    # Let's assume main.py is in 'app' directory, and .env is in project root.
    # So, if project structure is:
    # project_root/
    #   .env
    #   run.py
    #   app/
    #     main.py
    #     scrapers/
    #     ...
    # Then .env is one level up from app/main.py's directory.
    # So, path for load_dotenv: os.path.join(os.path.dirname(__file__), '..', '.env')
    # If main.py is in app/app/main.py, then it's '../../.env'.
    # The current `ls()` output shows `app/main.py`. So `..` is correct for project root.

    # Simplified: load_dotenv() searches for .env in current dir or parent dirs by default.
    # So a simple load_dotenv() might be enough if .env is in root and script is run from root.
    # However, explicitly providing path is more robust.
    # If run.py is `python /app/run.py` and run.py calls app.main.main(),
    # os.getcwd() will be /app. So load_dotenv() will find /app/.env
    # This means .env should be in /app, or we give load_dotenv path to /app/.env

    # Let's assume .env is in the same directory as run.py, which is the project root.
    # And that run.py changes CWD or Python path so app.main can be imported.
    # load_dotenv() will search for .env. If run.py is at root, CWD is root, .env found.
    load_dotenv()
    logger.info(".env file loaded if present.")


    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "waters":
            run_waters_scraper_command()
        elif command == "example":
            run_example_scraper_command()
        else:
            logger.error(f"Unknown command: {sys.argv[1]}")
            print_usage()
            sys.exit(1)
    else:
        logger.warning("No command provided.")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
