"""
Batch Scraper for Multiple Index Constituents
==============================================
Process multiple URLs from configuration file
"""

import logging
from pathlib import Path
import csv
from datetime import datetime
from typing import List, Dict
import sys

from index_scraper import IndexScraper
from config import (
    NIFTY_SECTORAL_INDICES,
    NIFTY_BROAD_INDICES,
    SCRAPER_CONFIG,
    OUTPUT_CONFIG
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchScraper:
    """Batch processor for multiple index URLs"""
    
    def __init__(self):
        """Initialize batch scraper"""
        self.scraper = IndexScraper(
            download_dir=SCRAPER_CONFIG['download_dir']
        )
        self.results = []
        
    def scrape_category(self, urls: List[str], category_name: str) -> Dict[str, bool]:
        """
        Scrape a category of indices
        
        Args:
            urls: List of URLs to scrape
            category_name: Name of the category (for logging)
            
        Returns:
            Dictionary with results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"CATEGORY: {category_name}")
        logger.info(f"{'='*70}")
        logger.info(f"Total URLs: {len(urls)}")
        
        # Create category subfolder if configured
        if OUTPUT_CONFIG['organize_by_category']:
            category_dir = Path(SCRAPER_CONFIG['download_dir']) / category_name.lower().replace(' ', '_')
            category_dir.mkdir(parents=True, exist_ok=True)
            self.scraper.download_dir = category_dir
        
        results = self.scraper.scrape_multiple(
            urls, 
            delay=SCRAPER_CONFIG['request_delay']
        )
        
        # Store results with metadata
        for url, success in results.items():
            self.results.append({
                'category': category_name,
                'url': url,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def scrape_all(self):
        """Scrape all configured indices"""
        logger.info("\n" + "="*70)
        logger.info("STARTING BATCH SCRAPING")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # Scrape sectoral indices
        self.scrape_category(
            NIFTY_SECTORAL_INDICES,
            "Sectoral Indices"
        )
        
        # Scrape broad indices
        self.scrape_category(
            NIFTY_BROAD_INDICES,
            "Broad Market Indices"
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        self.generate_summary(duration)
    
    def generate_summary(self, duration: float):
        """Generate and save summary report"""
        logger.info(f"{'='*70}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*70}")
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        
        logger.info(f"Total processed: {total}")
        logger.info(f"Successful: {successful} ({(successful/total*100):.1f}%)")
        logger.info(f"Failed: {failed} ({(failed/total*100):.1f}%)")
        logger.info(f"Duration: {duration:.1f} seconds")
        
        # Save summary to CSV if configured
        if OUTPUT_CONFIG['create_summary']:
            summary_file = Path(SCRAPER_CONFIG['download_dir']) / 'scraping_summary.csv'
            
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['category', 'url', 'success', 'timestamp'])
                writer.writeheader()
                writer.writerows(self.results)
            
            logger.info(f"Summary saved to: {summary_file}")
        
        # List failed URLs
        if failed > 0:
            logger.warning(f"\nFailed URLs:")
            for result in self.results:
                if not result['success']:
                    logger.warning(f"  - {result['url']}")


def main():
    """Main execution"""
    try:
        batch_scraper = BatchScraper()
        batch_scraper.scrape_all()
        
        logger.info("\n✓ Batch scraping completed!")
        
    except KeyboardInterrupt:
        logger.warning("\n✗ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()