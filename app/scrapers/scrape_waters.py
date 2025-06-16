from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.waters_strategy import WatersStrategy
from collections import defaultdict

def main():

  # Defines a mapping from New Brunswick regions to their constituent counties.
  # This is used to associate scraped water bodies with the correct regions.
  new_brunswick_region_to_counties = {
    "Restigouche": ["Restigouche"],
    "Chaleur": ["Gloucester", "Restigouche"],
    "Miramichi": ["Northumberland"],
    "Southeast": ["Kent", "Westmorland", "Albert"],
    "Inner Bay of Fundy": ["Saint John", "Kings", "Albert"],
    "Lower Saint John": ["Carleton", "York", "Sunbury", "Saint John"],
    "Southwest": ["Charlotte"],
    "Upper Saint John": ["Madawaska", "Victoria", "Carleton"]
  }

  # Creates a reverse mapping from counties to regions.
  # This allows for efficient lookup of regions based on a county.
  county_to_regions = defaultdict(list)
  for region, counties in new_brunswick_region_to_counties.items():
    for c in counties:
        county_to_regions[c].append(region)

  # Initializes the UnintrusivePageScraper with the base URL for Wikipedia.
  # This scraper is designed to fetch web content without overloading the server.
  scraper = UnintrusivePageScraper('https://en.wikipedia.org')
  # Initializes the WatersStrategy, which defines how to extract water body data from Wikipedia pages.
  waters_strategy = WatersStrategy()
  waters = scraper.scrape(waters_strategy)

  results = []

  # Process the scraped water body data.
  for water in waters:

    # Filter out water bodies that are not lakes or rivers.
    if water['type_1'].lower().strip() not in ['lake', 'river']:
      continue

    # Create a base dictionary for the water body's data.
    water_data = {
      'name': water['name'],
      'water_type': 'lakes, ponds and reservoirs' if water['type_1'] == 'lake' else 'rivers, brooks and streams'
    }

    # Determine the regions associated with the water body, handling potential duplicates.
    # It uses the start and end counties of the water body to find all relevant regions.
    # The 'removesuffix' and slicing are used to clean up county names before lookup.
    regions = set(county_to_regions[water['start_county'].removesuffix(' County')] + county_to_regions[water['end_county'][:-7]])

    # Create a separate entry in the results list for each region the water body belongs to.
    # This ensures that if a water body spans multiple regions, it's listed under each.
    for region in regions:
      results.append(water_data | {
        'region': region
      })

  # Convert the list of dictionaries into a list of lists (tabular data) for printing.
  # Each inner list represents a row with name, water type, and region.
  rows = [[result['name'], result['water_type'], result['region']] for result in results]
  print(rows)

if __name__ == '__main__':
    main()
