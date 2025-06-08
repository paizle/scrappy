import pytest
import io
import contextlib
import ast
import runpy
from unittest import mock # Still needed for other mock features if any, or can be removed if not.
import importlib
import app.scrape_strategies.scrape_waters # For reloading

# Import the class to be monkeypatched
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper

# --- Test Data ---
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
    {
        "name": "Lake Delta", "type_1": "lake", # Using lowercase "lake" to match integration test
        "parent": "Mountain Z", "start_county": "Restigouche County", "end_county": "Gloucester County"
    }
]

EXPECTED_PROCESSED_WATERS_ROWS = [
    ['Lake Delta', 'lakes, ponds and reservoirs', 'Restigouche'],
    ['Lake Delta', 'lakes, ponds and reservoirs', 'Chaleur'],
]

# --- Functional Test ---

@pytest.mark.functional
# Removed @mock.patch, will use monkeypatch
def test_main_application_output_with_mock_scraper(monkeypatch): # Added monkeypatch
    """
    Tests the main application entry point (app.main) with a mocked scraper.
    app.main imports app.scrape_strategies.scrape_waters, which then executes.
    The UnintrusivePageScraper.scrape method is monkeypatched.
    """

    # This inner function will be our mock for UnintrusivePageScraper.scrape
    def mock_scrape_method(self_arg, strategy_arg):
        return MOCK_RAW_WATERS_DATA

    # Patch the .scrape() method on the UnintrusivePageScraper class where it's defined.
    monkeypatch.setattr('app.unintrusive_scraper.page_scraper.UnintrusivePageScraper.scrape', mock_scrape_method)

    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        # Reload scrape_waters to ensure its top-level code runs with the mock
        importlib.reload(app.scrape_strategies.scrape_waters)

        try:
            # When app.main runs, it imports the reloaded (and thus re-executed)
            # app.scrape_strategies.scrape_waters, which will use the monkeypatched scraper.
            runpy.run_module('app.main', run_name='__main__')
        except ImportError as e:
            pytest.fail(f"ImportError when running app.main: {e}. Check sys.path and package structure.")
        except Exception as e:
            pytest.fail(f"An unexpected error occurred when running app.main: {e}")

    stdout_str = captured_output.getvalue().strip()

    if not stdout_str:
        pytest.fail("Stdout was empty. Expected a list of lists.")

    try:
        actual_rows = ast.literal_eval(stdout_str)
    except (ValueError, SyntaxError) as e:
        pytest.fail(f"Could not parse stdout from app.main execution: {e}\nStdout was:\n{stdout_str}")

    # Sort actual and expected rows
    actual_rows.sort(key=lambda x: (str(x[0]), str(x[2])))
    expected_rows_sorted = sorted(EXPECTED_PROCESSED_WATERS_ROWS, key=lambda x: (str(x[0]), str(x[2])))

    assert actual_rows == expected_rows_sorted
    # Verification of specific mock calls (like assert_called_once_with) is less direct
    # with this style of monkeypatching. The primary check is the output.
    # If needed, flags or counters could be added to mock_scrape_method.
