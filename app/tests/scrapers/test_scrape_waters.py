import unittest
import logging
from app.scrapers.scrape_waters import _process_waters_data # Import the refactored processing function

# Suppress logging for cleaner test output
logging.disable(logging.CRITICAL)

class TestScrapeWatersDataProcessing(unittest.TestCase):

    def test_process_empty_input(self):
        """Test processing with None or empty list as input."""
        self.assertEqual(_process_waters_data(None), [])
        self.assertEqual(_process_waters_data([]), [])

    def test_filter_by_water_type(self):
        """Test that only 'lake' and 'river' types are processed."""
        sample_data = [
            {"name": "Lake Alpha", "type_1": "Lake", "start_county": "North", "end_county": "North"}, # Assume North maps somewhere
            {"name": "River Beta", "type_1": "River", "start_county": "South", "end_county": "South"}, # Assume South maps somewhere
            {"name": "Pond Gamma", "type_1": "Pond", "start_county": "East", "end_county": "East"},
            {"name": "Ocean Delta", "type_1": "ocean", "start_county": "West", "end_county": "West"}
        ]
        # For this test to be fully isolated, we'd mock county_to_regions or use known valid counties.
        # Using actual county names from the map for more reliable results.
        sample_data_revised = [
            {"name": "Lake Alpha", "type_1": "Lake", "start_county": "Restigouche", "end_county": "Restigouche"},
            {"name": "River Beta", "type_1": "River", "start_county": "Charlotte", "end_county": "Charlotte"},
            {"name": "Pond Gamma", "type_1": "Pond", "start_county": "Kent", "end_county": "Kent"},
            {"name": "Ocean Delta", "type_1": "ocean", "start_county": "Albert", "end_county": "Albert"}
        ]
        processed = _process_waters_data(sample_data_revised)
        self.assertEqual(len(processed), 2)
        self.assertTrue(any(d['name'] == 'Lake Alpha' for d in processed))
        self.assertTrue(any(d['name'] == 'River Beta' for d in processed))

    def test_region_mapping_single_county_single_region(self):
        """Test region mapping for a water body within a single county and region."""
        sample_data = [
            {"name": "Restigouche Lake", "type_1": "Lake", "start_county": "Restigouche", "end_county": "Restigouche"},
        ]
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 1) # Restigouche county is in Restigouche & Chaleur regions. Test needs update.

        # Corrected expectation: Restigouche county is in 'Restigouche' and 'Chaleur' regions.
        # So, one entry for each region.
        self.assertEqual(len(processed), 2)
        regions_found = sorted([d['region'] for d in processed if d['name'] == "Restigouche Lake"])
        self.assertEqual(regions_found, ["Chaleur", "Restigouche"])
        for entry in processed:
            self.assertEqual(entry['water_type'], "lakes, ponds and reservoirs")


    def test_region_mapping_county_in_multiple_regions(self):
        """Test when a county belongs to multiple regions; one entry per region."""
        sample_data = [
            {"name": "Chaleur Connector River", "type_1": "River", "start_county": "Gloucester", "end_county": "Restigouche"},
        ]
        # Gloucester -> Chaleur
        # Restigouche -> Restigouche, Chaleur
        # Combined unique: Chaleur, Restigouche
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 2)
        regions_found = sorted([d['region'] for d in processed if d['name'] == "Chaleur Connector River"])
        self.assertEqual(regions_found, ["Chaleur", "Restigouche"])
        for entry in processed:
            self.assertEqual(entry['water_type'], "rivers, brooks and streams")


    def test_region_mapping_different_start_end_counties(self):
        """Test mapping when start and end counties are different and map to different/overlapping regions."""
        sample_data = [
            {"name": "Fundy Trail River", "type_1": "River", "start_county": "Albert", "end_county": "Kent"},
        ]
        # Albert -> Southeast, Inner Bay of Fundy
        # Kent -> Southeast
        # Combined unique: Southeast, Inner Bay of Fundy
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 2)
        regions_found = sorted([d['region'] for d in processed if d['name'] == "Fundy Trail River"])
        self.assertEqual(regions_found, ["Inner Bay of Fundy", "Southeast"])

    def test_county_name_cleaning(self):
        """Test that ' County' suffix is correctly handled for mapping."""
        sample_data = [
            {"name": "York River", "type_1": "River", "start_county": "York County", "end_county": "York County"},
        ]
        # York -> Lower Saint John
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]['region'], "Lower Saint John")

    def test_missing_keys_in_input_data(self):
        """Test graceful handling if some expected keys are missing from input dicts."""
        sample_data = [
            {"name": "Incomplete Lake", "type_1": "Lake"},
            {"type_1": "River", "start_county": "SomeCounty", "end_county": "OtherCounty"}
        ]
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 0)

        sample_data_2 = [
            {"name": "Partial River", "type_1": "River", "start_county": "NonExistentCounty", "end_county": "AnotherNonExistent"}
        ]
        processed_2 = _process_waters_data(sample_data_2)
        self.assertEqual(len(processed_2), 0)

    def test_non_string_data_values(self):
        """Test handling of non-string values where strings are expected."""
        sample_data = [
            # type_1 is number, will be skipped as str(123).lower() is not 'lake' or 'river'
            {"name": "Numeric Lake", "type_1": 123, "start_county": "Charlotte", "end_county": "Charlotte"},
            # name is None, will be "Unknown Name (processed)", counties map to "Southwest"
            {"name": None, "type_1": "River", "start_county": "Charlotte", "end_county": "Charlotte"},
        ]
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 1)
        if len(processed) == 1:
            self.assertEqual(processed[0]['name'], "Unknown Name (processed)")
            self.assertEqual(processed[0]['region'], "Southwest")
            self.assertEqual(processed[0]['water_type'], "rivers, brooks and streams")

    def test_data_integrity_after_processing(self):
        """Check for expected keys in the processed output."""
        sample_data = [
            {"name": "Test Lake", "type_1": "Lake", "start_county": "Charlotte", "end_county": "Charlotte"},
        ]
        processed = _process_waters_data(sample_data)
        self.assertEqual(len(processed), 1)
        entry = processed[0]
        self.assertIn("name", entry)
        self.assertIn("water_type", entry)
        self.assertIn("region", entry)
        self.assertEqual(entry["name"], "Test Lake")
        self.assertEqual(entry["water_type"], "lakes, ponds and reservoirs")
        self.assertEqual(entry["region"], "Southwest") # Charlotte county -> Southwest region

if __name__ == "__main__":
    unittest.main()
