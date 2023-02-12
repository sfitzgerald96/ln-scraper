try:
    from result import *
    import slack
except:
    from ln_scraper.result import *
    import ln_scraper.slack as slack

import requests
import json
import re
import pdb
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, settings):
        self.settings = settings
        self.BASE_URL = "https://www.loopnet.com"
        self.SEARCH_URL = "%s/services/search" % self.BASE_URL
        self.results = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Content-Type': 'text/html; charset=UTF-8'
        }

    def run_scrape_job(self):
        # Execute Search API call and get HTML that represents the results
        response = requests.post(self.SEARCH_URL, data=json.dumps(self.settings['LoopNet']), headers=self.headers)
        if response.status_code == 200:
            results = response.json()
            results_html = results['SearchPlacards']['Html']
        else:
            print("Last status code from requests: %s" % response.status_code)
            print("Last response from requests: %s" % response.content.decode())
            print("Failed to get search results with given settings")
            return False

        # Process the search results HTML with bs4
        soup = BeautifulSoup(results_html, features="html.parser")
        properties = soup.find_all('article')
        if len(properties) > 0:
            for property in properties:
                property_url = property.find("header").find("a").get("href")
                processed_result = self.process_search_result(property_url)
                self.results.append(processed_result)

        pdb.set_trace()
        for r in self.results:
            print("tally ho!")

    def process_search_result(self, result_url):
        result = None
        results_dict = {}
        response = requests.get(result_url, headers=self.headers)
        if response.status_code is 200:
            results_dict['PropertyURL'] = result_url
            property_html = response.text
            soup = BeautifulSoup(property_html, features="html.parser")

            # Get Property Address from title
            title_text = soup.find("title").string.strip()
            match = re.match(r'^.+[0-9]+', title_text, re.I)
            if match:
                title_text = match.group()

            results_dict['Address'] =  title_text

            # Get list of agents
            contact_form = soup.find("ul", {"id": "contact-form-contacts"})
            results_dict['Agents'] = list(map(lambda tag: tag.attrs.get("title"), contact_form.find_all("li", {"class": "contact"})))
            try:
                results_dict['Brokerage'] = contact_form.find("li", {"class": "contact-logo"}).attrs.get("title")
            except:
                results_dict['Brokerage'] = "Error"

            # Process attribute data for the result
        #     property_data_table = soup.find("table", {"class" : "property-data"})
        #     for row in property_data_table.find_all('tr'):
        #         try:
        #             cells = row.find_all('td')
        #             for i in range(len(cells)):
        #                 # The cells follow a pattern of Property Name --> Property Value
        #                 if i % 2 != 0: # Property Title 
        #                     results_dict[cells[i-1].string.strip()] = cells[i].string.strip()
        #         except:
        #             continue
        #
        #     # Process Unit Mix Information Section
        #     property_unit_mix_table = soup.find("table", {"class" : "property-data summary"})
        #     if property_unit_mix_table:
        #         unit_mix_table_headers = property_unit_mix_table.find_all("th")
        #         unit_mix_table_values = property_unit_mix_table.find_all("td")
        #         for header_index in range(len(unit_mix_table_headers)):
        #             header_name = unit_mix_table_headers[header_index].text.strip()
        #             header_value = unit_mix_table_values[header_index].text.strip()
        #             results_dict['MIX_INFO_%s' % header_name] = header_value
        #
        # else:
        #     # Failed to parse, just return None and proceed
        #     print("Failed to parse property for %s" % result_url)

        result = Result(results_dict)
        return result

    def save_result_to_sdb(self, result):
        attributes = []
        for attr_name, attr_value in result.results_dict.items():
            if attr_name is not None and attr_name is not '':
                attribute = { 'Name': attr_name, 'Value': attr_value, 'Replace': False }
                attributes.append(attribute)

        response = self.sdb_client.put_attributes(
            DomainName=self.simple_db_domain,
            ItemName=result.address,
            Attributes=attributes
        )            

    def property_exists_in_db(self, result):
        # Try to get the property from SDB
        response = self.sdb_client.get_attributes(
            DomainName=self.simple_db_domain,
            ItemName=result.address,
        )

        # If the response dictionary has an Attributes key,
        # then the property was found in the DB
        if 'Attributes' in response:
            return True
        else:
            return False
