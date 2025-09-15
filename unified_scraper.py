import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
from openai_scraper import OpenAIScraper
from google_scraper import GoogleAIScraper

class UnifiedCompetitorScraper:
    def __init__(self):
        self.scrapers = {
            'OpenAI': OpenAIScraper(),
            'Google AI': GoogleAIScraper()
        }
        self.results = {}

    def scrape_all_competitors(self, limit_per_source=5):
        """Scrape all configured competitors"""
        print("Starting unified competitor scraping...")
        
        for competitor_name, scraper in self.scrapers.items():
            print(f"\n{'='*50}")
            print(f"Scraping {competitor_name}")
            print(f"{'='*50}")
            
            try:
                if competitor_name == 'OpenAI':
                    posts = scraper.get_latest_blog_posts(limit_per_source)
                elif competitor_name == 'Google AI':
                    posts = scraper.get_latest_blog_posts(limit_per_source)
                    if not posts:  # Fallback to RSS
                        posts = scraper.get_rss_posts(limit_per_source)
                else:
                    posts = []
                
                self.results[competitor_name] = posts
                print(f"Found {len(posts)} posts for {competitor_name}")
                
            except Exception as e:
                print(f"Error scraping {competitor_name}: {str(e)}")
                self.results[competitor_name] = []
            
            # Be respectful with delays between different sites
            time.sleep(3)

    def generate_unified_report(self):
        """Generate a unified markdown report for all competitors"""
        if not self.results:
            print("No data to generate report from.")
            return None
        
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_content = f"# AI Competitor Intelligence Report\n\n"
        report_content += f"**Generated:** {report_date}\n\n"
        
        # Summary section
        total_posts = sum(len(posts) for posts in self.results.values())
        report_content += f"**Total Posts Found:** {total_posts}\n\n"
        
        report_content += "## Summary by Competitor\n\n"
        for competitor, posts in self.results.items():
            status = "✅" if posts else "❌"
            report_content += f"- **{competitor}**: {len(posts)} posts {status}\n"
        report_content += "\n"
        
        # Detailed sections for each competitor
        for competitor, posts in self.results.items():
            report_content += f"## {competitor}\n\n"
            
            if posts:
                for i, post in enumerate(posts, 1):
                    report_content += f"{i}. **{post['title']}**\n"
                    report_content += f"   - URL: {post['url']}\n"
                    report_content += f"   - Scraped: {post['scraped_at']}\n"
                    if 'source' in post:
                        report_content += f"   - Source: {post['source']}\n"
                    report_content += "\n"
            else:
                report_content += "No posts found or scraping failed.\n\n"
        
        # Save unified report
        os.makedirs('reports', exist_ok=True)
        report_filename = f"reports/unified_competitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Unified report saved to {report_filename}")
        return report_filename

    def save_unified_json(self):
        """Save all results to a unified JSON file"""
        if not self.results:
            print("No data to save.")
            return None
        
        # Add metadata
        unified_data = {
            'generated_at': datetime.now().isoformat(),
            'total_competitors': len(self.scrapers),
            'total_posts': sum(len(posts) for posts in self.results.values()),
            'competitors': self.results
        }
        
        filename = f"unified_competitor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(unified_data, f, indent=2)
        
        print(f"Unified data saved to {filename}")
        return filename

    def run(self):
        """Run the unified scraping process"""
        print("🚀 Starting Unified AI Competitor Tracking")
        print("=" * 60)
        
        # Scrape all competitors
        self.scrape_all_competitors()
        
        # Generate reports
        print(f"\n{'='*50}")
        print("Generating Reports")
        print(f"{'='*50}")
        
        self.generate_unified_report()
        self.save_unified_json()
        
        # Summary
        print(f"\n{'='*50}")
        print("SCRAPING COMPLETE")
        print(f"{'='*50}")
        
        total_posts = sum(len(posts) for posts in self.results.values())
        print(f"Total posts found: {total_posts}")
        
        for competitor, posts in self.results.items():
            status = "✅ SUCCESS" if posts else "❌ FAILED"
            print(f"{competitor}: {len(posts)} posts {status}")

if __name__ == "__main__":
    scraper = UnifiedCompetitorScraper()
    scraper.run()