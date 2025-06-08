import pytest
import requests
import io
import contextlib
import ast
import importlib
from unittest import mock

# Import the actual UnintrusivePageScraper for monkeypatching its method
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrape_strategies.example_strategy import ExampleComStrategy
# Import the module to be reloaded
import app.scrape_strategies.scrape_waters


# --- Test for ExampleComStrategy (Full Scraping Process) ---

@pytest.mark.integration
@pytest.mark.network
def test_example_com_strategy_full_scrape():
    """
    Tests the full scraping process using UnintrusivePageScraper and ExampleComStrategy
    by making a real HTTP request to example.com.
    """
    # Using http:// to avoid potential SSL issues in some test environments if example.com redirects
    scraper = UnintrusivePageScraper(base_url='http://example.com')
    strategy = ExampleComStrategy()

    expected_data = {
        "title": "Example Domain",
        "heading": "Example Domain"
    }

    try:
        actual_data = scraper.scrape(strategy)
        assert actual_data == expected_data
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Network request to example.com failed: {e}")
    except Exception as e:
        pytest.fail(f"Scraping example.com produced an unexpected exception: {e}")

# --- Data for WatersStrategy Processing Test ---

MOCK_RAW_WATERS_DATA = [
    {
        "name": "Lake Alpha", "type_1": "Lake", "type_2": "Freshwater",
        "parent": "River X", "start_county": "County 1", "end_county": "County 1"
    },
    {
        "name": "River Beta", "type_1": "River", "type_2": "",
        "parent": "Lake Y", "start_county": "County 2", "end_county": "County 3"
    },
    { # This one should be filtered out by type
        "name": "Swamp Gamma", "type_1": "Swamp", "type_2": "Wetland",
        "parent": "", "start_county": "County 4", "end_county": "County 4"
    },
    { # This one has a start_county that maps to multiple regions
        "name": "Lake Delta", "type_1": "lake", # Explicitly lowercase for testing
        "parent": "Mountain Z", "start_county": "Restigouche County", "end_county": "Gloucester County"
    }
]

# Expected processed output from the original scrape_waters.py script logic
EXPECTED_PROCESSED_WATERS_ROWS = [
    ['Lake Delta', 'lakes, ponds and reservoirs', 'Restigouche'],
    ['Lake Delta', 'lakes, ponds and reservoirs', 'Chaleur'],
]

# --- Test for WatersStrategy Data Processing Logic ---

@pytest.mark.integration
def test_scrape_waters_processing_logic_with_mock_scraper(monkeypatch, capsys):
    """
    Tests the data processing logic of app/scrape_strategies/scrape_waters.py
    by mocking the UnintrusivePageScraper.scrape method using monkeypatch.
    """

    def mock_scrape_method(self_arg, strategy_arg):
        return MOCK_RAW_WATERS_DATA

    # Patch the scrape method on the UnintrusivePageScraper class where it's defined
    # so that when scrape_waters.py imports and uses it, it gets the patched version.
    monkeypatch.setattr('app.unintrusive_scraper.page_scraper.UnintrusivePageScraper.scrape', mock_scrape_method)

    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        importlib.reload(app.scrape_strategies.scrape_waters)

    stdout_str = captured_output.getvalue().strip()

    if not stdout_str:
        pytest.fail("Stdout from scrape_waters.py was empty. Expected a list of lists.")

    try:
        actual_rows = ast.literal_eval(stdout_str)
    except (ValueError, SyntaxError) as e:
        pytest.fail(f"Could not parse stdout from scrape_waters.py: {e}\nStdout was:\n{stdout_str}")

    # Sort actual and expected rows to handle potential order differences in regions
    actual_rows.sort(key=lambda x: (str(x[0]), str(x[2])))
    # Create a sorted copy for assertion to avoid modifying the global constant
    expected_rows_sorted = sorted(EXPECTED_PROCESSED_WATERS_ROWS, key=lambda x: (str(x[0]), str(x[2])))

    assert actual_rows == expected_rows_sorted
