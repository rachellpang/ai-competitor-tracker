import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

class CompetitorScraper:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Creating default config.")
            return {}

    def scrape_website(self, url, selectors):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    article = {
                        'title': element.get_text().strip(),
                        'url': url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return []

    def scrape_all_competitors(self):
        all_data = {}
        
        for competitor, config in self.config.get('competitors', {}).items():
            print(f"Scraping {competitor}...")
            articles = self.scrape_website(config['url'], config['selectors'])
            all_data[competitor] = articles
            time.sleep(self.config.get('delay_between_requests', 1))
        
        return all_data

    def generate_report(self, data):
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_content = f"# AI Competitor Intelligence Report - {report_date}\n\n"
        
        for competitor, articles in data.items():
            report_content += f"## {competitor}\n\n"
            if articles:
                for article in articles[:5]:  # Limit to top 5 articles
                    report_content += f"- {article['title']}\n"
            else:
                report_content += "No new articles found.\n"
            report_content += "\n"
        
        report_filename = f"reports/report_{report_date}.md"
        os.makedirs('reports', exist_ok=True)
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Report saved to {report_filename}")

    def run(self):
        print("Starting competitor tracking...")
        data = self.scrape_all_competitors()
        self.generate_report(data)
        print("Competitor tracking completed.")

if __name__ == "__main__":
    scraper = CompetitorScraper()
    scraper.run()