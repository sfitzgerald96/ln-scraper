import pdb

try:
    from scraper import *
    from settings import *
except:
    from ln_scraper.scraper import *
    from ln_scraper.settings import *

import glob


def run():
    # Find the settings file
    settings_file = None
    for filename in glob.iglob('**/md_land_settings.yaml', recursive=True):
        print("Found settings file in: %s" % filename)
        settings_file = filename
        break

    if settings_file is None:
        print("Failed to find settings file")
        return false

    # Read the settings
    sp = SettingsParser()
    settings = sp.get_settings(settings_file)

    # Scrape the data
    scraper = Scraper(settings)
    scraper.run_scrape_job()


if __name__ == "__main__":
    run()
