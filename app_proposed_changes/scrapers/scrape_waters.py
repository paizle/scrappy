from app.unintrusive_scraper.scraper import UnintrusiveScraper
from app.scrape_strategies.waters_strategy import WatersStrategy
from collections import defaultdict

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

def transform_and_filter_water_data(waters_data, county_to_regions_map):
    results = []
    for water in waters_data:

      # only lakes and rivers
      if water['type_1'].lower().strip() not in ['lake', 'river']:
        continue

      # base data
      water_data = {
        'name': water['name'],
        'water_type': 'lakes, ponds and reservoirs' if water['type_1'] == 'lake' else 'rivers, brooks and streams'
        }

      # no duplicate regions
      start_county_cleaned = water['start_county'].replace(" County", "")
      end_county_cleaned = water['end_county'].replace(" County", "")
      regions = set(county_to_regions_map[start_county_cleaned] + county_to_regions_map[end_county_cleaned])

      # one water entry for each region
      for region in regions:
        results.append(water_data | {
          'region': region
        })
    return results

scraper = UnintrusiveScraper('https://en.wikipedia.org')
waters_strategy = WatersStrategy()
waters = scraper.scrape(waters_strategy)

processed_results = transform_and_filter_water_data(waters, county_to_regions)

# convert to tabular data
rows = [[result['name'], result['water_type'], result['region']] for result in processed_results]
print(rows)
