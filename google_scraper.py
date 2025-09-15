import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import time

class GoogleAIScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.base_url = "https://ai.googleblog.com"
        self.blog_url = "https://ai.googleblog.com"

    def get_latest_blog_posts(self, limit=10):
        try:
            print(f"Fetching Google AI blog posts from {self.blog_url}")
            time.sleep(2)  # Be respectful with requests
            
            response = self.session.get(self.blog_url, timeout=15)
            
            if response.status_code == 403:
                print("Access forbidden. Google AI blog may have bot protection.")
                return []
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            blog_posts = []
            
            # Multiple selectors to try for Google AI blog
            selectors = [
                'h2.post-title a',
                '.post-title a', 
                'h3 a[href*="blogspot.com"]',
                'h2 a[href*="blogspot.com"]',
                '.entry-title a',
                'h1.entry-title a',
                'h2.entry-title a',
                'article h2 a',
                '.blog-post h2 a',
                '.post h2 a'
            ]
            
            found_posts = set()
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                for element in elements:
                    href = element.get('href', '')
                    title = element.get_text().strip()
                    
                    # Filter for valid blog posts
                    if (title and len(title) > 15 and 
                        href and href not in found_posts and
                        ('blogspot.com' in href or 'ai.googleblog.com' in href)):
                        
                        # Make sure URL is absolute
                        if href.startswith('/'):
                            full_url = self.base_url + href
                        elif not href.startswith('http'):
                            full_url = self.base_url + '/' + href
                        else:
                            full_url = href
                        
                        post_data = {
                            'title': title,
                            'url': full_url,
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'Google AI Blog'
                        }
                        
                        blog_posts.append(post_data)
                        found_posts.add(href)
                        
                        if len(blog_posts) >= limit:
                            break
                
                if len(blog_posts) >= limit:
                    break
            
            # Remove duplicates based on title similarity
            unique_posts = []
            seen_titles = set()
            for post in blog_posts:
                title_lower = post['title'].lower()
                if title_lower not in seen_titles:
                    unique_posts.append(post)
                    seen_titles.add(title_lower)
            
            return unique_posts[:limit]
            
        except Exception as e:
            print(f"Error scraping Google AI blog: {str(e)}")
            return []

    def get_rss_posts(self, limit=10):
        """Try to get posts from RSS feed as fallback"""
        rss_urls = [
            "https://ai.googleblog.com/feeds/posts/default",
            "https://ai.googleblog.com/rss.xml",
            "https://ai.googleblog.com/atom.xml"
        ]
        
        for rss_url in rss_urls:
            try:
                print(f"Trying RSS feed: {rss_url}")
                response = self.session.get(rss_url, timeout=10)
                if response.status_code == 200:
                    return self._parse_rss_content(response.content, limit)
            except Exception as e:
                print(f"RSS feed failed {rss_url}: {str(e)}")
        
        return []

    def _parse_rss_content(self, content, limit):
        """Parse RSS/Atom content"""
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(content)
            posts = []
            
            # Try different RSS/Atom formats
            entries = (root.findall('.//entry') or 
                      root.findall('.//item') or
                      root.findall('.//{http://www.w3.org/2005/Atom}entry'))
            
            for entry in entries[:limit]:
                title_elem = (entry.find('title') or 
                             entry.find('{http://www.w3.org/2005/Atom}title'))
                link_elem = (entry.find('link') or 
                            entry.find('{http://www.w3.org/2005/Atom}link'))
                
                if title_elem is not None:
                    title = title_elem.text or ''
                    link = ''
                    
                    if link_elem is not None:
                        link = link_elem.text or link_elem.get('href', '')
                    
                    if title.strip():
                        posts.append({
                            'title': title.strip(),
                            'url': link.strip(),
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'Google AI Blog RSS'
                        })
            
            return posts
            
        except Exception as e:
            print(f"Error parsing RSS: {str(e)}")
            return []

    def save_posts_to_json(self, posts, filename=None):
        if not posts:
            print("No posts to save.")
            return
            
        if not filename:
            filename = f"google_ai_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(posts, f, indent=2)
        
        print(f"Saved {len(posts)} posts to {filename}")

    def generate_markdown_report(self, posts):
        if not posts:
            print("No posts to generate report for.")
            return None
            
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_content = f"# Google AI Blog Posts Report\n\n"
        report_content += f"**Generated:** {report_date}\n\n"
        report_content += f"**Total Posts Found:** {len(posts)}\n\n"
        report_content += f"**Source:** {posts[0].get('source', 'Google AI Blog') if posts else 'N/A'}\n\n"
        
        report_content += "## Latest Blog Posts\n\n"
        for i, post in enumerate(posts, 1):
            report_content += f"{i}. **{post['title']}**\n"
            report_content += f"   - URL: {post['url']}\n"
            report_content += f"   - Scraped: {post['scraped_at']}\n\n"
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        report_filename = f"reports/google_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Report saved to {report_filename}")
        return report_filename

    def run(self):
        print("Starting Google AI blog scraper...")
        
        # Try HTML scraping first
        posts = self.get_latest_blog_posts()
        
        # If HTML scraping fails, try RSS
        if not posts:
            print("HTML scraping failed, trying RSS feeds...")
            posts = self.get_rss_posts()
        
        if posts:
            print(f"\nFound {len(posts)} blog posts:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post['title']}")
            
            # Save to JSON
            self.save_posts_to_json(posts)
            
            # Generate markdown report
            self.generate_markdown_report(posts)
        else:
            print("No blog posts found from Google AI.")

if __name__ == "__main__":
    scraper = GoogleAIScraper()
    scraper.run()