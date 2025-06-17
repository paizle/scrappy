import re
from app.unintrusive_scraper.page_scraper import PageScrapingStrategy
from bs4 import BeautifulSoup # Required for type hint

class WikipediaGdpTextStrategy(PageScrapingStrategy):
    def get_url(self) -> str:
        return "/wiki/List_of_countries_by_GDP_(nominal)"

    def parse(self, soup: BeautifulSoup) -> dict:
        country_name = "United States"
        # Try a more specific marker assuming get_text(separator='\n') structure
        search_marker = "\n" + "United States" + "\n"
        debug_info = {}

        try:
            # Attempt to find the main data table to narrow down the text search
            table_element = soup.find('table', class_="wikitable sortable")

            html_text_content = ""
            if not table_element:
                debug_info["table_find_error"] = "Could not find 'wikitable sortable' element. Using full page text."
                html_text_content = soup.get_text(separator='\n') # Use newline separator
                debug_info["text_source"] = "full_soup_object"
            else:
                html_text_content = table_element.get_text(separator='\n') # Get text only from the table
                debug_info["text_source"] = "wikitable_sortable_element"

            if not isinstance(html_text_content, str):
                debug_info["html_text_content_type_error"] = f"Expected str from get_text(), got {type(html_text_content)}"
                return {"country": country_name, "gdp": "", "error": "get_text() did not return a string", "debug_info": debug_info}

            # Find the "United States" string in the (potentially table-specific) text content
            pos_country_name = html_text_content.find(search_marker)
            debug_info["pos_country_name_in_text"] = pos_country_name

            if pos_country_name == -1:
                # Fallback: if "\nUnited States\n" is not found, try original "United States"
                # This is important if the country name is at the very start/end of text or not newline separated
                search_marker = "United States" # Original marker
                pos_country_name = html_text_content.find(search_marker)
                debug_info["pos_country_name_in_text_fallback"] = pos_country_name
                if pos_country_name == -1:
                    debug_info["text_snippet_on_failure"] = html_text_content[:500]
                    return {"country": country_name, "gdp": "", "error": "Could not find country marker in text content (tried specific and plain)", "debug_info": debug_info}

            # Slice the text starting AFTER the found marker to find GDP
            start_slice_for_gdp = pos_country_name + len(search_marker)
            slice_to_search_gdp = html_text_content[start_slice_for_gdp : start_slice_for_gdp + 70]
            debug_info["slice_to_search_gdp"] = slice_to_search_gdp
            debug_info["used_search_marker"] = search_marker


            match = re.search(r"^\s*([\d,]+)", slice_to_search_gdp)

            if not match:
                return {"country": country_name, "gdp": "", "error": "GDP value not found in text slice via regex", "debug_info": debug_info}

            gdp_value = match.group(1)

            if ',' not in gdp_value:
                if gdp_value.isdigit() and len(gdp_value) <= 4:
                    return {"country": country_name, "gdp": "", "error": "Found number in text looks like a year/rank, not GDP (no comma, short)", "found_val": gdp_value, "debug_info": debug_info}
            elif not any(char.isdigit() for char in gdp_value):
                 return {"country": country_name, "gdp": "", "error": "Found GDP value has no digits", "found_val": gdp_value, "debug_info": debug_info}

            return {"country": country_name, "gdp": gdp_value, "debug_info": debug_info}

        except Exception as e:
            current_debug_info = debug_info if 'debug_info' in locals() and isinstance(debug_info, dict) else {}
            return {"country": country_name, "gdp": "", "error": str(e), "debug_info": current_debug_info}
