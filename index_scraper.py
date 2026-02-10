"""
Index Constituent File Scraper
================================
Advanced web scraper for downloading Index Constituent files from financial websites.
Supports multiple sources with intelligent fallback mechanisms.
"""

import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging
from typing import Optional, Dict, List
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndexScraper:
    """Advanced scraper for Index Constituent files"""
    
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize the scraper
        
        Args:
            download_dir: Directory to save downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Enhanced headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def extract_index_name(self, url: str) -> str:
        """Extract index name from URL"""
        # Extract the last part of the URL path
        parts = urlparse(url).path.strip('/').split('/')
        return parts[-1] if parts else "unknown_index"
    
    def find_constituent_link(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """
        Find the Index Constituent download link using multiple strategies
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            Full URL to the constituent file or None
        """
        strategies = [
            self._strategy_direct_csv_link,
            self._strategy_download_section,
            self._strategy_data_attributes,
            self._strategy_javascript_links,
            self._strategy_pattern_matching
        ]
        
        for strategy in strategies:
            link = strategy(soup, base_url)
            if link:
                logger.info(f"Found link using {strategy.__name__}")
                return link
        
        return None
    
    def _strategy_direct_csv_link(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Strategy 1: Look for direct CSV links with 'constituent' in text or URL"""
        # Look for links with text containing "Index Constituent" or "Constituent"
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip().lower()
            href = link['href'].lower()
            
            if ('constituent' in text or 'constituent' in href) and '.csv' in href:
                return urljoin(base_url, link['href'])
        
        return None
    
    def _strategy_download_section(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Strategy 2: Look in Downloads section"""
        # Find the Downloads section
        downloads_section = soup.find('div', class_=re.compile(r'download', re.I))
        
        if downloads_section:
            for link in downloads_section.find_all('a', href=True):
                if 'constituent' in link.get_text().lower() or 'constituent' in link['href'].lower():
                    return urljoin(base_url, link['href'])
        
        return None
    
    def _strategy_data_attributes(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Strategy 3: Look for data attributes or hidden download links"""
        # Check for data-url, data-download, etc.
        for element in soup.find_all(attrs={'data-url': True}):
            url = element['data-url']
            if 'constituent' in url.lower() and '.csv' in url.lower():
                return urljoin(base_url, url)
        
        return None
    
    def _strategy_javascript_links(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Strategy 4: Extract links from JavaScript code"""
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                # Look for CSV URLs in JavaScript
                csv_urls = re.findall(r'["\']([^"\']*constituent[^"\']*\.csv)["\']', 
                                     script.string, re.I)
                if csv_urls:
                    return urljoin(base_url, csv_urls[0])
        
        return None
    
    def _strategy_pattern_matching(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Strategy 5: Use known patterns from Nifty indices"""
        # Known pattern: /IndexConstituent/ind_[indexname]list.csv
        index_patterns = [
            r'/IndexConstituent/[^"\']*\.csv',
            r'/indices/[^"\']*constituent[^"\']*\.csv',
            r'/downloads?/[^"\']*constituent[^"\']*\.csv'
        ]
        
        page_html = str(soup)
        
        for pattern in index_patterns:
            matches = re.findall(pattern, page_html, re.I)
            if matches:
                return urljoin(base_url, matches[0])
        
        return None
    
    def download_file(self, url: str, filename: Optional[str] = None) -> bool:
        """
        Download a file from URL
        
        Args:
            url: URL to download from
            filename: Optional custom filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Attempting to download: {url}")
            
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Determine filename
            if not filename:
                # Try to get from Content-Disposition header
                content_disp = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disp:
                    filename = content_disp.split('filename=')[1].strip('"\'')
                else:
                    # Extract from URL
                    filename = os.path.basename(urlparse(url).path)
            
            # Ensure .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            filepath = self.download_dir / filename
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                if total_size:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Show progress
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")
                else:
                    f.write(response.content)
            
            logger.info(f"✓ Successfully downloaded: {filepath}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to download {url}: {str(e)}")
            return False
    
    def scrape_and_download(self, url: str) -> bool:
        """
        Main method: Scrape page and download Index Constituent file
        
        Args:
            url: URL of the index page
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {url}")
            logger.info(f"{'='*60}")
            
            # Step 1: Fetch the page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Step 2: Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 3: Find constituent file link
            constituent_link = self.find_constituent_link(soup, url)
            
            if not constituent_link:
                logger.error("✗ Could not find Index Constituent download link")
                
                # Try to construct link based on known pattern
                index_name = self.extract_index_name(url)
                # Nifty pattern: ind_[name]list.csv
                potential_link = urljoin(url, f"/IndexConstituent/ind_{index_name}list.csv")
                logger.info(f"Trying constructed URL: {potential_link}")
                constituent_link = potential_link
            
            # Step 4: Download the file
            filename = f"{self.extract_index_name(url)}_constituents.csv"
            success = self.download_file(constituent_link, filename)
            
            return success
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error accessing {url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error: {str(e)}")
            return False
    
    def scrape_multiple(self, urls: List[str], delay: float = 2.0) -> Dict[str, bool]:
        """
        Scrape multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to scrape
            delay: Delay between requests in seconds
            
        Returns:
            Dictionary mapping URLs to success status
        """
        results = {}
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\nProcessing {i}/{len(urls)}")
            results[url] = self.scrape_and_download(url)
            
            # Rate limiting
            if i < len(urls):
                logger.info(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total URLs processed: {len(urls)}")
        logger.info(f"Successful: {sum(results.values())}")
        logger.info(f"Failed: {len(urls) - sum(results.values())}")
        
        return results


def main():
    """Main execution function"""
    # Initialize scraper
    scraper = IndexScraper(download_dir="downloads")
    
    # Example URL - Nifty IT
    test_url = "https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it"
    
    # Scrape and download
    success = scraper.scrape_and_download(test_url)
    
    if success:
        logger.info("\n✓ Scraping completed successfully!")
    else:
        logger.warning("\n✗ Scraping completed with errors")


if __name__ == "__main__":
    main()