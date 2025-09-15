import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os

class OpenAIRSScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        # Try multiple potential RSS feed URLs
        self.rss_urls = [
            "https://openai.com/blog/rss.xml",
            "https://openai.com/rss.xml",
            "https://openai.com/feed.xml",
            "https://openai.com/blog/feed"
        ]

    def fetch_rss_feed(self):
        """Try to fetch RSS feed from multiple possible URLs"""
        for rss_url in self.rss_urls:
            try:
                print(f"Trying RSS URL: {rss_url}")
                response = self.session.get(rss_url, timeout=10)
                if response.status_code == 200:
                    print(f"Successfully fetched RSS from: {rss_url}")
                    return response.content
                else:
                    print(f"Failed to fetch {rss_url}: Status {response.status_code}")
            except Exception as e:
                print(f"Error fetching {rss_url}: {str(e)}")
        
        print("No valid RSS feed found.")
        return None

    def parse_rss(self, rss_content):
        """Parse RSS XML content and extract blog posts"""
        try:
            root = ET.fromstring(rss_content)
            posts = []
            
            # Handle different RSS formats
            items = root.findall('.//item')  # Standard RSS
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')  # Atom format
            
            for item in items:
                title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text if link_elem.text else link_elem.get('href')
                    
                    post = {
                        'title': title.strip() if title else 'No title',
                        'url': link.strip() if link else '',
                        'scraped_at': datetime.now().isoformat(),
                        'source': 'RSS'
                    }
                    posts.append(post)
            
            return posts
            
        except ET.ParseError as e:
            print(f"Error parsing RSS XML: {str(e)}")
            return []
        except Exception as e:
            print(f"Error processing RSS: {str(e)}")
            return []

    def get_latest_blog_posts(self, limit=10):
        """Get latest blog posts from RSS feed - NO FAKE DATA"""
        rss_content = self.fetch_rss_feed()
        
        if not rss_content:
            print("Could not fetch any RSS feed. No fake data will be provided.")
            return []
        
        posts = self.parse_rss(rss_content)
        
        if not posts:
            print("No posts found in RSS feed.")
            return []
        
        print(f"Found {len(posts)} posts in RSS feed")
        return posts[:limit]

    def save_posts_to_json(self, posts, filename=None):
        if not posts:
            print("No posts to save.")
            return
            
        if not filename:
            filename = f"openai_rss_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(posts, f, indent=2)
        
        print(f"Saved {len(posts)} posts to {filename}")

    def generate_markdown_report(self, posts):
        if not posts:
            print("No posts to generate report for.")
            return None
            
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_content = f"# OpenAI Blog Posts Report (RSS)\n\n"
        report_content += f"**Generated:** {report_date}\n\n"
        report_content += f"**Total Posts Found:** {len(posts)}\n\n"
        report_content += f"**Data Source:** Real RSS feed (no fake data)\n\n"
        
        report_content += "## Latest Blog Posts\n\n"
        for i, post in enumerate(posts, 1):
            report_content += f"{i}. **{post['title']}**\n"
            report_content += f"   - URL: {post['url']}\n"
            report_content += f"   - Scraped: {post['scraped_at']}\n\n"
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        report_filename = f"reports/openai_rss_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Report saved to {report_filename}")
        return report_filename

    def run(self):
        print("Starting OpenAI RSS scraper (NO FAKE DATA)...")
        posts = self.get_latest_blog_posts()
        
        if posts:
            print(f"\nFound {len(posts)} real blog posts:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post['title']}")
            
            # Save to JSON
            self.save_posts_to_json(posts)
            
            # Generate markdown report
            self.generate_markdown_report(posts)
        else:
            print("No real data found. Application will not generate fake content.")

if __name__ == "__main__":
    scraper = OpenAIRSScraper()
    scraper.run()