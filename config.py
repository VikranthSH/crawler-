"""
Configuration file for Index Scraper
Contains all URLs and settings
"""

# Test with single URL
NIFTY_SECTORAL_INDICES = [
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-realty",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-psu-bank"
    "https://www.niftyindices.com/indices/equity/thematic-indices/nifty-pse",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-pharma",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-oil-and-gas-index",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-metal",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-media"
]

# Remove or leave empty for now
NIFTY_BROAD_INDICES = []

# Scraper Settings
SCRAPER_CONFIG = {
    'download_dir': 'downloads',
    'request_delay': 2.0,
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 5.0,
}

# Output Settings
OUTPUT_CONFIG = {
    'create_summary': True,
    'create_summary': True,
    'timestamp_files': False,
    'organize_by_category': True,
}