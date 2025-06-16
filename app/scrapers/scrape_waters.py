from app.unintrusive_scraper.page_scraper import UnintrusivePageScraper
from app.scrapers.scrape_strategies.waters_strategy import WatersStrategy
from collections import defaultdict

def main():

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

  # reverse the keys
  county_to_regions = defaultdict(list)
  for region, counties in new_brunswick_region_to_counties.items():
    for c in counties:
        county_to_regions[c].append(region)

  scraper = UnintrusivePageScraper('https://en.wikipedia.org')
  waters_strategy = WatersStrategy()
  waters = scraper.scrape(waters_strategy)

  results = []

  for water in waters:

    # only lakes and rivers
    if water['type_1'].lower().strip() not in ['lake', 'river']:
      continue

    # base data
    water_data = {
      'name': water['name'],
      'water_type': 'lakes, ponds and reservoirs' if water['type_1'] == 'lake' else 'rivers, brooks and streams'
    }

    # no duplicate regions
    regions = set(county_to_regions[water['start_county'].removesuffix(' County')] + county_to_regions[water['end_county'][:-7]])

    # one water entry for each region
    for region in regions:
      results.append(water_data | {
        'region': region
      })

  # convert to tabular data
  rows = [[result['name'], result['water_type'], result['region']] for result in results]
  print(rows)

if __name__ == '__main__':
    main()

