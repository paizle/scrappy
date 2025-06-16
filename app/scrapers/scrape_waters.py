"""
Script to scrape New Brunswick water body data from Wikipedia and process it.

This script defines a function `run_waters_scraper_logic` that utilizes the
UnintrusivePageScraper with the WatersStrategy to fetch data from Wikipedia.
It then filters this data for lakes and rivers, maps them to predefined
New Brunswick regions based on counties, and formats the results into a
tabular structure.
"""
import logging
from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrape_strategies.waters_strategy import WatersStrategy
from collections import defaultdict
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Defines the mapping of New Brunswick tourism regions to their constituent counties.
new_brunswick_region_to_counties = {
    "Restigouche": ["Restigouche"],
    "Chaleur": ["Gloucester", "Restigouche"],
    "Miramichi": ["Northumberland"],
    "Southeast": ["Kent", "Westmorland", "Albert"],
    "Inner Bay of Fundy": ["Saint John", "Kings", "Albert"],
    "Lower Saint John": ["Carleton", "York", "Sunbury", "Saint John"],
    "Southwest": ["Charlotte"],
    "Upper Saint John": ["Madawaska", "Victoria", "Carleton"],
}

# Invert the mapping for easier lookup: county -> list of regions it belongs to.
county_to_regions = defaultdict(list)
for region, counties in new_brunswick_region_to_counties.items():
    for county_name in counties:
        county_to_regions[county_name].append(region)


def _process_waters_data(scraped_waters_data: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Processes the raw scraped water data: filters, maps to regions, etc.
    """
    results = []
    if scraped_waters_data is None:
        logger.error("Scraping returned None. No data to process.")
        return results
    if not isinstance(scraped_waters_data, list):
        logger.error(
            f"Expected a list from scraper, but got {type(scraped_waters_data)}. "
            "No data to process."
        )
        return results

    logger.info(f"Processing {len(scraped_waters_data)} initial water entries.")
    for i, water_entry in enumerate(scraped_waters_data):
        try:
            if not isinstance(water_entry, dict):
                logger.warning(f"Skipping item #{i} as it's not a dictionary: {water_entry}")
                continue

            water_type_1_raw = water_entry.get("type_1", "")
            if not isinstance(water_type_1_raw, str):
                logger.warning(
                    f"Skipping item #{i} ('{water_entry.get('name', 'Unknown')}') "
                    f"due to non-string type_1: {water_type_1_raw}"
                )
                continue
            water_type_1 = water_type_1_raw.lower().strip()

            if water_type_1 not in ["lake", "river"]:
                continue

            water_name = water_entry.get("name", "Unknown Name")
            if not isinstance(water_name, str):
                logger.warning(
                    f"Item #{i} has non-string name: {water_name}. "
                    "Using 'Unknown Name (processed)'."
                )
                water_name = "Unknown Name (processed)"

            water_type_description = (
                "lakes, ponds and reservoirs"
                if water_type_1 == "lake"
                else "rivers, brooks and streams"
            )
            water_data = {
                "name": water_name,
                "water_type": water_type_description,
            }

            start_county_raw = water_entry.get("start_county", "")
            end_county_raw = water_entry.get("end_county", "")

            if not isinstance(start_county_raw, str) or not isinstance(end_county_raw, str):
                logger.warning(
                    f"Skipping item '{water_name}' due to non-string county data. "
                    f"Start: '{start_county_raw}', End: '{end_county_raw}'"
                )
                continue

            county_suffix = " County"
            county_suffix_len = len(county_suffix)

            start_county_cleaned = (
                start_county_raw[:-county_suffix_len]
                if start_county_raw.endswith(county_suffix)
                else start_county_raw
            )
            end_county_cleaned = (
                end_county_raw[:-county_suffix_len]
                if end_county_raw.endswith(county_suffix)
                else end_county_raw
            )

            associated_regions = set()
            if start_county_cleaned and start_county_cleaned in county_to_regions:
                associated_regions.update(county_to_regions[start_county_cleaned])
            if end_county_cleaned and end_county_cleaned in county_to_regions:
                associated_regions.update(county_to_regions[end_county_cleaned])

            if not associated_regions:
                logger.debug(
                    f"No regions found for water body '{water_name}' with cleaned counties "
                    f"'{start_county_cleaned}' (from '{start_county_raw}'), "
                    f"'{end_county_cleaned}' (from '{end_county_raw}')"
                )
                continue

            for region_name in associated_regions:
                final_entry = water_data.copy() # Use copy to avoid modifying base water_data dict
                final_entry["region"] = region_name
                results.append(final_entry)

        except TypeError as e:
            logger.error(
                f"TypeError processing water entry #{i}: {water_entry}. Error: {e}",
                exc_info=True,
            )
            continue
        except Exception as e:
            logger.error(
                f"Unexpected error processing water entry #{i}: {water_entry}. Error: {e}",
                exc_info=True,
            )
            continue
    logger.info(f"Processed into {len(results)} entries after filtering and region mapping.")
    return results


def run_waters_scraper_logic(
    base_url: str,
    cache_dir: str,
    default_delay: int,
    max_retries: int,
    retry_backoff_factor: int,
):
    """
    Runs the main logic for scraping and processing New Brunswick water bodies.
    """
    logger.info(
        f"Initializing UnintrusivePageScraper with base_url: {base_url}, "
        f"cache_dir: {cache_dir}, delay: {default_delay}, retries: {max_retries}, "
        f"backoff_factor: {retry_backoff_factor}"
    )
    scraper = UnintrusivePageScraper(
        base_url=base_url,
        cache_dir=cache_dir,
        default_delay=default_delay,
        max_retries=max_retries,
        retry_backoff_factor=retry_backoff_factor,
    )
    waters_strategy = WatersStrategy()

    logger.info("Starting scrape for New Brunswick water bodies...")
    scraped_waters_data = scraper.scrape(waters_strategy) # This is List[Dict[str,str]] | None

    # Call the processing function
    processed_results = _process_waters_data(scraped_waters_data)

    if not processed_results:
        logger.warning("No results to output after processing scraped data.")

    # Convert the list of result dictionaries into a tabular format (list of lists) for output.
    output_rows = [
        [result.get("name", ""), result.get("water_type", ""), result.get("region", "")]
        for result in processed_results # Use processed_results here
    ]

    logger.info(f"Final processed data (for output) contains {len(output_rows)} rows.")
    # print(output_rows) # Example: if direct output is desired by this function
    return output_rows
