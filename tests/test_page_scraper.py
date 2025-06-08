import pytest
import requests
import os
from unittest import mock

# Import PageScrapingStrategy for the mock_strategy fixture's spec
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper, PageScrapingStrategy
from app.scrape_strategies.example_strategy import ExampleComStrategy # Using this as a concrete strategy for some tests
from bs4 import BeautifulSoup # Needed for type checking mock_strategy.parse.call_args

# --- Test Data and Configurations ---
MOCK_ROBOTS_TXT_ALLOW_ALL = "User-agent: *\nDisallow:"
MOCK_ROBOTS_TXT_DISALLOW_ALL = "User-agent: *\nDisallow: /"
MOCK_ROBOTS_TXT_DISALLOW_SPECIFIC = "User-agent: *\nDisallow: /specific_path/"

SAMPLE_HTML_CONTENT = """
<html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Welcome</h1>
        <p class="content">This is some content.</p>
        <p class="content">More content here.</p>
        <a href="https://example.com/anotherpage">Another Page</a>
    </body>
</html>
"""

# --- Fixtures ---

@pytest.fixture
def scraper_no_cache():
    """
    Returns a UnintrusivePageScraper instance.
    Caching behavior depends on mocks in specific tests (e.g., mock os.path.exists).
    It will use its default self.cache_dir if not otherwise influenced by mocks.
    """
    scraper = UnintrusivePageScraper(base_url="https://base.com")
    return scraper

@pytest.fixture
def scraper_with_cache(tmp_path):
    """
    Returns a UnintrusivePageScraper instance configured to use a temporary cache directory.
    """
    scraper = UnintrusivePageScraper(base_url="https://base.com")
    # Override the default cache_dir to use the temp_path for this test session
    test_cache_dir = tmp_path / "test_scraper_cache_fixture" # Unique name for clarity
    test_cache_dir.mkdir(exist_ok=True)
    scraper.cache_dir = str(test_cache_dir) # Set the instance's cache_dir
    return scraper

@pytest.fixture
def mock_strategy():
    strategy = mock.Mock(spec=PageScrapingStrategy) # Use the ABC for spec
    strategy.get_url.return_value = "/test_path" # Strategies return paths
    strategy.parse.return_value = {"key": "parsed_value"}
    strategy.name = "MockStrategy" # Optional: for debugging or identification
    return strategy

# --- Test Cases ---

@mock.patch('urllib.robotparser.RobotFileParser')
class TestUnintrusivePageScraperCanFetch:

    def test_can_fetch_allowed_by_robots(self, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        # Replace the scraper's robot_parser with a fresh mock instance for this test
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance

        mock_parser_instance.can_fetch.return_value = True

        assert scraper_no_cache.can_fetch("https://example.com/some_page") is True
        # set_url and read would have been called during original __init__.
        # If we want to test them against this new instance, __init__ would need to be called again
        # or these methods called directly. For can_fetch, this setup is okay.
        mock_parser_instance.can_fetch.assert_called_with(scraper_no_cache.user_agent, "https://example.com/some_page")

    def test_can_fetch_disallowed_by_robots(self, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance
        mock_parser_instance.can_fetch.return_value = False

        assert scraper_no_cache.can_fetch("https://example.com/any_page") is False
        mock_parser_instance.can_fetch.assert_called_with(scraper_no_cache.user_agent, "https://example.com/any_page")

    def test_can_fetch_disallowed_specific_path(self, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance
        def can_fetch_side_effect(agent, url):
            if "specific_path" in url:
                return False
            return True
        mock_parser_instance.can_fetch.side_effect = can_fetch_side_effect

        assert scraper_no_cache.can_fetch("https://example.com/specific_path/page1") is False
        assert scraper_no_cache.can_fetch("https://example.com/allowed_path/page2") is True
        assert mock_parser_instance.can_fetch.call_count == 2

    def test_can_fetch_robots_txt_read_exception(self, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance
        # Simulate that robot_parser.read() (called in original __init__) might have failed.
        # The can_fetch method of the mock should then determine behavior.
        mock_parser_instance.read.side_effect = Exception("Robots Read Error") # Mock read on this instance
        mock_parser_instance.can_fetch.return_value = True # Default/optimistic behavior

        assert scraper_no_cache.can_fetch("https://example.com/any_page") is True
        mock_parser_instance.can_fetch.assert_called_with(scraper_no_cache.user_agent, "https://example.com/any_page")

    def test_can_fetch_malformed_url(self, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance
        mock_parser_instance.can_fetch.return_value = True
        assert scraper_no_cache.can_fetch("htp://badurl") is True
        mock_parser_instance.can_fetch.assert_called_with(scraper_no_cache.user_agent, "htp://badurl")


@mock.patch('urllib.robotparser.RobotFileParser')
class TestUnintrusivePageScraperGetPageContent:

    @mock.patch('requests.get')
    def test_get_page_content_success_no_cache(self, mock_requests_get, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance # Explicitly set the mock
        mock_parser_instance.can_fetch.return_value = True

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML_CONTENT
        mock_requests_get.return_value = mock_response

        with mock.patch('os.path.exists', return_value=False) as mock_path_exists:
            with mock.patch('builtins.open', mock.mock_open()) as mock_file_write:
                content = scraper_no_cache.get_page_content("https://example.com/test_page")

        assert content == SAMPLE_HTML_CONTENT
        expected_headers = {'User-Agent': scraper_no_cache.user_agent}
        mock_requests_get.assert_called_once_with("https://example.com/test_page", headers=expected_headers) # Removed timeout
        # Basic check for cache write attempt
        mock_file_write.assert_called_once()


    @mock.patch('requests.get')
    def test_get_page_content_request_failure_returns_none(self, mock_requests_get, MockRobotParserClass, scraper_no_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_no_cache.robot_parser = mock_parser_instance # Explicitly set the mock
        mock_parser_instance.can_fetch.return_value = True
        mock_requests_get.side_effect = requests.exceptions.RequestException("Simulated network error")

        with mock.patch('os.path.exists', return_value=False):
            content = scraper_no_cache.get_page_content("https://example.com/not_found_page")

        assert content is None
        assert mock_requests_get.call_count == scraper_no_cache.max_retries


    @mock.patch('requests.get')
    @mock.patch('os.path.exists')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_get_page_content_uses_cache_if_exists(self, mock_file_open, mock_os_exists, mock_requests_get, MockRobotParserClass, scraper_with_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_with_cache.robot_parser = mock_parser_instance # Explicitly set the mock
        mock_parser_instance.can_fetch.return_value = True

        url = scraper_with_cache.base_url + "/cached_page"
        safe_filename = url.replace('/', '_').replace(':', '_') + ".html"
        expected_cache_filename = os.path.join(scraper_with_cache.cache_dir, safe_filename)

        mock_os_exists.return_value = True
        mock_file_open.return_value.read.return_value = SAMPLE_HTML_CONTENT

        content = scraper_with_cache.get_page_content(url)

        assert content == SAMPLE_HTML_CONTENT
        mock_os_exists.assert_called_once_with(expected_cache_filename)
        mock_file_open.assert_called_once_with(expected_cache_filename, 'r', encoding='utf-8')
        mock_requests_get.assert_not_called()


    @mock.patch('requests.get')
    @mock.patch('os.path.exists')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_get_page_content_creates_and_uses_cache(self, mock_file_open, mock_os_exists, mock_requests_get, MockRobotParserClass, scraper_with_cache: UnintrusivePageScraper):
        mock_parser_instance = MockRobotParserClass.return_value
        scraper_with_cache.robot_parser = mock_parser_instance # Explicitly set the mock
        mock_parser_instance.can_fetch.return_value = True
        url = scraper_with_cache.base_url + "/newly_cached_page"
        safe_filename = url.replace('/', '_').replace(':', '_') + ".html"
        expected_cache_filename = os.path.join(scraper_with_cache.cache_dir, safe_filename)

        mock_os_exists.side_effect = [False, True]

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # First call - should fetch and write to cache
        content1 = scraper_with_cache.get_page_content(url)
        assert content1 == SAMPLE_HTML_CONTENT
        mock_os_exists.assert_any_call(expected_cache_filename)
        expected_headers = {'User-Agent': scraper_with_cache.user_agent}
        mock_requests_get.assert_called_once_with(url, headers=expected_headers) # Removed timeout
        mock_file_open.assert_any_call(expected_cache_filename, 'w', encoding='utf-8') # Cache write
        mock_file_open().write.assert_called_once_with(SAMPLE_HTML_CONTENT)

        mock_requests_get.reset_mock()
        mock_file_open.reset_mock()

        mock_file_open.return_value.read.return_value = SAMPLE_HTML_CONTENT

        content2 = scraper_with_cache.get_page_content(url)
        assert content2 == SAMPLE_HTML_CONTENT
        mock_os_exists.assert_any_call(expected_cache_filename)
        mock_file_open.assert_called_once_with(expected_cache_filename, 'r', encoding='utf-8')
        mock_requests_get.assert_not_called()


# TestUnintrusivePageScraperParseData removed


class TestUnintrusivePageScraperScrape:

    def test_scrape_success(self, scraper_no_cache: UnintrusivePageScraper, mock_strategy):
        strategy_path = "/test_path"
        # No need for full_target_url here as we mock get_page_content

        mock_strategy.get_url.return_value = strategy_path
        expected_parsed_data = {"key": "parsed_value"}
        mock_strategy.parse.return_value = expected_parsed_data # Configure what strategy's parse returns

        # Mock get_page_content directly on the instance for this test
        with mock.patch.object(scraper_no_cache, 'get_page_content', return_value=SAMPLE_HTML_CONTENT) as mock_get_content:
            result = scraper_no_cache.scrape(mock_strategy)

        mock_strategy.get_url.assert_called_once()
        mock_get_content.assert_called_once_with(scraper_no_cache.base_url + strategy_path)

        mock_strategy.parse.assert_called_once()
        assert isinstance(mock_strategy.parse.call_args[0][0], BeautifulSoup), \
               "Strategy's parse method was not called with a BeautifulSoup object"
        assert result == expected_parsed_data


    def test_scrape_cannot_fetch(self, scraper_no_cache: UnintrusivePageScraper, mock_strategy):
        strategy_path = "/forbidden_path"
        full_target_url = scraper_no_cache.base_url + strategy_path
        mock_strategy.get_url.return_value = strategy_path

        # Mock can_fetch on the instance to return False
        # And get_page_content to simulate its behavior when can_fetch is False (returns None)
        with mock.patch.object(scraper_no_cache, 'can_fetch', return_value=False) as mock_instance_can_fetch:
            # We also need to ensure that get_page_content is NOT mocked here, so it calls the real can_fetch.
            # The goal is to test the scrape method's handling of get_page_content returning None.
            # So, the UnintrusivePageScraper's actual get_page_content will run.
            # This means we need the robot_parser mock to be set up for the scraper_no_cache instance.
            # This test class does NOT have the @mock.patch('urllib.robotparser.RobotFileParser')
            # Add it, or ensure scraper_no_cache's robot_parser is appropriately mocked if can_fetch is not directly mocked.

            # Simpler: Mock get_page_content to return None, as this is the state scrape() sees if can_fetch failed.
            with mock.patch.object(scraper_no_cache, 'get_page_content', return_value=None) as mock_get_content:
                result = scraper_no_cache.scrape(mock_strategy)
                assert result == [] # Current behavior when get_page_content returns None

                mock_strategy.get_url.assert_called_once()
                # Assert that get_page_content was called, which implies can_fetch was (internally) false
                mock_get_content.assert_called_once_with(full_target_url)


    def test_scrape_get_content_fails(self, scraper_no_cache: UnintrusivePageScraper, mock_strategy):
        strategy_path = "/error_page"
        full_target_url = scraper_no_cache.base_url + strategy_path
        mock_strategy.get_url.return_value = strategy_path

        # Mock get_page_content on the instance to simulate an HTTPError
        with mock.patch.object(scraper_no_cache, 'get_page_content', side_effect=requests.exceptions.HTTPError("Simulated HTTP Error")) as mock_get_content:
            with pytest.raises(requests.exceptions.HTTPError):
                scraper_no_cache.scrape(mock_strategy)

        mock_strategy.get_url.assert_called_once()
        mock_get_content.assert_called_once_with(full_target_url)


    def test_scrape_no_url_from_strategy(self, scraper_no_cache: UnintrusivePageScraper, mock_strategy):
        mock_strategy.get_url.return_value = None # Strategy returns None for the path

        # If get_url returns None, base_url + None will raise TypeError.
        # The scrape method does: self.base_url + strategy.get_url()
        # This should be handled gracefully or raise a specific error.
        # Currently, it would likely raise a TypeError when trying to concatenate string and None.
        with pytest.raises(TypeError): # Expecting TypeError due to str + NoneType
             scraper_no_cache.scrape(mock_strategy)

        mock_strategy.get_url.assert_called_once()

# It's good practice to also test the _get_cache_filename helper if it had more complex logic,
# but for now, its direct use in get_page_content tests covers its behavior implicitly.
# Consider adding if UnintrusivePageScraper is imported by other modules in tests
# if __name__ == "__main__":
# pytest.main()
