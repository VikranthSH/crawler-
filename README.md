# Nifty Index Scraper

A robust Python web scraper for downloading **index constituent files** from NSE (National Stock Exchange) Nifty indices. This tool automatically scrapes and downloads CSV files containing constituent stocks for various Nifty sectoral and broad market indices.

## 📋 Overview

The Nifty Index Scraper automates the process of downloading index constituent data from [niftyindices.com](https://www.niftyindices.com). It handles multiple indices with intelligent fallback mechanisms, error handling, and batch processing capabilities.

### Supported Indices

**Sectoral Indices:**
- Nifty IT
- Nifty Realty
- Nifty PSU Bank
- Nifty PSE (Public Sector Enterprises)
- Nifty Pharma
- Nifty Oil & Gas
- Nifty Metal
- Nifty Media

## 🎯 Features

- ✅ **Multiple Download Strategies**: 5 different fallback mechanisms to locate download links
- ✅ **Batch Processing**: Scrape multiple indices in one run
- ✅ **Rate Limiting**: Configurable delays between requests to be respectful to servers
- ✅ **Error Handling**: Robust exception handling and retry logic
- ✅ **Organized Output**: Option to organize downloads by category
- ✅ **Summary Reports**: Generates CSV reports of scraping results
- ✅ **Logging**: Detailed logging to both file and console
- ✅ **Browser Simulation**: Uses realistic HTTP headers to avoid being blocked

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory:**
```bash
cd crawler
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

This will install:
- `requests` - HTTP library for making web requests
- `beautifulsoup4` - HTML parsing library
- `lxml` - XML/HTML parser (backend for BeautifulSoup)

## 📦 Project Structure

```
crawler/
├── batch_scraper.py          # Batch processor for multiple indices
├── index_scraper.py          # Core scraping engine
├── config.py                 # Configuration & URL lists
├── requirements.txt          # Project dependencies
├── README.md                 # This file
├── scraper.log              # Activity log
├── downloads/               # Downloaded files (auto-created)
│   ├── broad_market_indices/
│   └── sectoral_indices/
│       ├── nifty-it_constituents.csv
│       ├── nifty-pharma_constituents.csv
│       ├── nifty-metal_constituents.csv
│       ├── nifty-realty_constituents.csv
│       ├── nifty-media_constituents.csv
│       └── ...
```

## 💻 Usage

### Option 1: Batch Scraping (Recommended)

Run all configured indices in one go:

```bash
python batch_scraper.py
```

This will:
- Scrape all indices defined in `config.py`
- Organize files into category folders
- Generate a summary report (`scraping_summary.csv`)
- Log all activity to `scraper.log`

### Option 2: Single Index Scraping

Scrape a single index:

```bash
python index_scraper.py
```

By default, this scrapes the Nifty IT index. To modify, edit the `test_url` in the `main()` function.

### Programmatic Usage

```python
from index_scraper import IndexScraper

# Initialize scraper
scraper = IndexScraper(download_dir="downloads")

# Scrape a single index
url = "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-pharma"
success = scraper.scrape_and_download(url)

# Scrape multiple indices
urls = [
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it",
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-pharma"
]
results = scraper.scrape_multiple(urls, delay=2.0)
```

## ⚙️ Configuration

Edit `config.py` to customize the scraper:

### Index URLs
```python
NIFTY_SECTORAL_INDICES = [
    "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it",
    # Add more indices here
]

NIFTY_BROAD_INDICES = [
    # Add broad market indices here
]
```

### Scraper Settings
```python
SCRAPER_CONFIG = {
    'download_dir': 'downloads',      # Where to save files
    'request_delay': 2.0,              # Delay between requests (seconds)
    'timeout': 30,                     # Request timeout (seconds)
    'max_retries': 3,                  # Number of retry attempts
    'retry_delay': 5.0,                # Delay between retries (seconds)
}
```

### Output Settings
```python
OUTPUT_CONFIG = {
    'create_summary': True,            # Generate summary report
    'timestamp_files': False,          # Add timestamp to filenames
    'organize_by_category': True,      # Create category subdirectories
}
```

## 📊 Output Files

### Downloaded CSVs
Each scrape downloads a CSV file containing:
- Stock symbols (ISIN)
- Company names
- Sector information
- Weightage in index
- Last updated date

Example: `nifty-it_constituents.csv`

### Summary Report
`scraping_summary.csv` contains:
| category | url | success | timestamp |
|----------|-----|---------|-----------|
| Sectoral Indices | https://... | True | 2024-01-15T10:30:45 |

### Logs
`scraper.log` - Detailed activity log for debugging and monitoring

## 🔧 How It Works

### 1. **Link Detection** (5 Strategies)
   - Strategy 1: Direct CSV links with 'constituent' in text/URL
   - Strategy 2: Download section search
   - Strategy 3: Data attributes (data-url, etc.)
   - Strategy 4: JavaScript embedded links
   - Strategy 5: Pattern matching with known formats

### 2. **Download Process**
   - Fetches the index page
   - Parses HTML with BeautifulSoup
   - Locates the constituent file link
   - Downloads with progress tracking
   - Validates file integrity

### 3. **Error Handling**
   - Automatic retry on failure
   - Graceful fallback mechanisms
   - Detailed error logging
   - Continues batch processing even if one index fails

## 🛡️ Best Practices

1. **Rate Limiting**: The default 2-second delay between requests is respectful. Increase if you encounter rate limiting.

2. **Network**: Ensure stable internet connection during batch runs.

3. **Storage**: Ensure sufficient disk space in the `downloads` directory.

4. **Logging**: Check `scraper.log` for any issues or failures.

5. **User Agent**: The scraper uses realistic browser headers to avoid being blocked.

## 📝 Example Output

```
2024-01-15 10:30:45,123 - INFO - ======================================================================
2024-01-15 10:30:45,124 - INFO - STARTING BATCH SCRAPING
2024-01-15 10:30:45,125 - INFO - ======================================================================
2024-01-15 10:30:45,126 - INFO - 
2024-01-15 10:30:45,127 - INFO - ======================================================================
2024-01-15 10:30:45,128 - INFO - CATEGORY: Sectoral Indices
2024-01-15 10:30:45,129 - INFO - ======================================================================
2024-01-15 10:30:45,130 - INFO - Total URLs: 8
2024-01-15 10:30:46,234 - INFO - Processing 1/8
2024-01-15 10:30:46,235 - INFO - ============================================================
2024-01-15 10:30:46,236 - INFO - Processing: https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it
2024-01-15 10:30:47,456 - INFO - ✓ Successfully downloaded: downloads/sectoral_indices/nifty-it_constituents.csv
```

## ❓ Troubleshooting

### Issue: "Connection timeout" errors
- **Solution**: Increase `timeout` in `SCRAPER_CONFIG`

### Issue: "Could not find Index Constituent download link"
- **Solution**: The website structure may have changed. Check if the link is located differently or contact maintainer.

### Issue: Downloaded file is empty
- **Solution**: The link may be broken. Check the website directly for the resource.

### Issue: Rate limited (429 errors)
- **Solution**: Increase `request_delay` in `SCRAPER_CONFIG`

## 🤝 Contributing

To add more indices:

1. Find the correct URL on niftyindices.com
2. Add to `NIFTY_SECTORAL_INDICES` or `NIFTY_BROAD_INDICES` in `config.py`
3. Run the batch scraper

## 📄 License

This project is provided as-is for personal and educational use.

## ⚠️ Disclaimer

This tool is designed for authorized use only. Please ensure you have permission to scrape data from niftyindices.com. Respect the website's terms of service and robots.txt file.

---

**Last Updated:** February 2026
